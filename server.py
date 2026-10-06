import os
import base64
import json
import re
import sqlite3
import time
import threading
from collections import defaultdict, deque
from runner_gateway import run_code
from hosting import STORAGE_MODE,AUTH_MODE,ORIGINS,visitor,require_user,public_config
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent
DATA=json.loads((ROOT/'data/curriculum.json').read_text())
LESSONS={x['id']:x for x in DATA['lessons']}
PROJECTS={x['id'] for x in DATA['projects']}
DB=Path(os.getenv('SQLITE_PATH',str(ROOT/'data/academy.sqlite')))
if STORAGE_MODE=='server':DB.parent.mkdir(parents=True,exist_ok=True)
def connect():
    db=sqlite3.connect(DB,timeout=15)
    db.row_factory=sqlite3.Row
    return db

@asynccontextmanager
async def lifespan(app):
    if STORAGE_MODE=='server':
      with connect() as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
        CREATE TABLE IF NOT EXISTS progress(user_id TEXT,lesson_id TEXT,completed_at TEXT,PRIMARY KEY(user_id,lesson_id));
        CREATE TABLE IF NOT EXISTS drafts(user_id TEXT,document_id TEXT,html TEXT,css TEXT,updated_at TEXT,PRIMARY KEY(user_id,document_id));
        """)
    app.state.ready=True
    yield
    app.state.ready=False

app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None)
app.state.ready=False
@app.middleware("http")
async def headers(req,call_next):
    if req.method in ('POST','PUT','DELETE'):
        origin=req.headers.get('origin','').rstrip('/')
        cross=req.headers.get('sec-fetch-site')=='cross-site'
        # Cookie-free standalone auth permits explicitly allowed frontend origins.
        # PromptQL mode retains its original same-site restriction.
        if cross and (AUTH_MODE=='promptql' or origin not in ORIGINS):
            return Response("Cross-site writes are not allowed",status_code=403)
        if AUTH_MODE=='supabase' and origin and origin not in ORIGINS:
            # Same-origin Render deployments need no ALLOWED_ORIGINS entry.
            from urllib.parse import urlparse
            if urlparse(origin).netloc!=req.headers.get('host'):
                return Response("Origin is not allowed",status_code=403)
        try:
            if int(req.headers.get('content-length','0'))>1200000:
                return Response("Request is too large",status_code=413)
        except ValueError:return Response("Invalid content length",status_code=400)
    r=await call_next(req)
    r.headers['X-Content-Type-Options']='nosniff'
    r.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    r.headers['Cache-Control']='no-store'
    return r

# Register after the security middleware so CORS headers cover error responses too.
app.add_middleware(CORSMiddleware,allow_origins=ORIGINS,allow_credentials=False,
                   allow_methods=['GET','POST','PUT','OPTIONS'],allow_headers=['Authorization','Content-Type'],
                   expose_headers=['Content-Disposition'],max_age=600)

@app.get('/api/config')
def config():
    return public_config()

@app.get('/readyz')
def ready():
    return Response(status_code=204 if app.state.ready and (ROOT/'frontend/dist/index.html').exists() else 503)

@app.get('/api/curriculum')
def curriculum():
    return DATA

@app.get('/api/state')
def state(req:Request):
    v=visitor(req)
    if not v:return dict(user=None,completed=[],drafts={})
    if not DB.exists():return dict(user=v,completed=[],drafts={})
    with connect() as db:
        completed=[dict(r) for r in db.execute("SELECT lesson_id,completed_at FROM progress WHERE user_id=?",(v['id'],))]
        drafts={r['document_id']:dict(html=r['html'],css=r['css'],updated_at=r['updated_at']) for r in db.execute("SELECT document_id,html,css,updated_at FROM drafts WHERE user_id=?",(v['id'],))}
    return dict(user=v,completed=completed,drafts=drafts)

class Code(BaseModel):
    html:str=Field(max_length=100000)
    css:str=Field(max_length=100000)
class Attempt(Code):
    answer:int=Field(ge=0,le=10)

def valid_doc(doc):
    if doc not in LESSONS and doc not in PROJECTS and doc not in ('playground','playground-javascript','playground-java'):
        raise HTTPException(404,"Unknown document")

@app.put('/api/drafts/{doc}')
def save_draft(doc:str,data:Code,req:Request):
    if STORAGE_MODE=='browser':raise HTTPException(409,'This deployment saves drafts in your browser, not on the server.')
    uid=require_user(req)
    valid_doc(doc)
    stamp=datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("INSERT INTO drafts VALUES (?,?,?,?,?) ON CONFLICT(user_id,document_id) DO UPDATE SET html=excluded.html,css=excluded.css,updated_at=excluded.updated_at",(uid,doc,data.html,data.css,stamp))
    return dict(saved=True,updated_at=stamp)

def evaluate_program(lesson,source):
    result=run_code(lesson['track'],source)
    expected=lesson.get('expected_output','').strip()
    checks=[
        dict(passed=result['exit_code']==0,label="Program runs without an error"),
        dict(passed=result['stdout'].strip()==expected and result['exit_code']==0,label="Output matches the exercise: "+expected.replace('\n',' · '))
    ]
    return dict(checks=checks,execution=result)

def check_code(lesson,html,css):
    if lesson['track'] in ('javascript','java'):
        return evaluate_program(lesson,html)['checks']
    soup=BeautifulSoup(html,'html.parser')
    results=[]
    for c in lesson['checks']:
        kind=c[0]
        if kind=='tag':
            passed=soup.find(c[1]) is not None;label=f"Include a <{c[1]}> element"
        elif kind=='count':
            passed=len(soup.find_all(c[1]))>=c[2];label=f"Include at least {c[2]} <{c[1]}> elements"
        elif kind=='attr':
            passed=any(el.has_attr(c[2]) and (len(c)<4 or (c[3] in el.get(c[2],[]) if isinstance(el.get(c[2]),list) else el.get(c[2])==c[3])) for el in soup.find_all(c[1]))
            label=f"<{c[1]}> has {c[2]}"+(f'="{c[3]}"' if len(c)>3 else '')
        elif kind=='attr_nonempty':
            passed=any(bool(el.get(c[2])) for el in soup.find_all(c[1]));label=f"<{c[1]}> has a nonempty {c[2]}"
        else:
            clean=re.sub(r'/\*.*?\*/','',css,flags=re.S)
            found=bool(re.search(c[1],clean,re.I|re.S))
            passed=not found if kind=='css_not' else found
            label=("Avoid " if kind=='css_not' else "Use ")+c[1].replace('\\s*',' ').replace('\\s+',' ').replace('\\','')
        results.append(dict(passed=bool(passed),label=label))
    return results

RUN_HISTORY=defaultdict(deque)
RUN_LOCK=threading.Lock()
def limit_runs(req):
    user=visitor(req)
    if AUTH_MODE=='supabase' and not user:raise HTTPException(401,'Sign in to run programs on this deployment.')
    key=user['id'] if user else 'anonymous'
    now=time.monotonic()
    with RUN_LOCK:
        for stale in list(RUN_HISTORY):
            if not RUN_HISTORY[stale] or now-RUN_HISTORY[stale][-1]>60:
                del RUN_HISTORY[stale]
        q=RUN_HISTORY[key]
        while q and q[0]<now-60:q.popleft()
        if len(q)>=20:raise HTTPException(429,"Run limit reached. Wait a minute before trying again.")
        q.append(now)

class RunInput(BaseModel):
    language:str
    source:str=Field(max_length=100000)

@app.post('/api/run')
def run_program(data:RunInput,req:Request):
    if data.language not in ('javascript','java'):raise HTTPException(400,"Choose JavaScript or Java")
    limit_runs(req)
    return run_code(data.language,data.source)

@app.post('/api/check/{doc}')
def check(doc:str,data:Code,req:Request):
    if doc not in LESSONS:raise HTTPException(404,"Unknown lesson")
    if LESSONS[doc]['track'] in ('javascript','java'):
        limit_runs(req)
        return evaluate_program(LESSONS[doc],data.html)
    return dict(checks=check_code(LESSONS[doc],data.html,data.css))

@app.post('/api/complete/{doc}')
def complete(doc:str,data:Attempt,req:Request):
    if STORAGE_MODE=='browser':raise HTTPException(409,'This deployment saves progress in your browser.')
    uid=require_user(req)
    if doc not in LESSONS:raise HTTPException(404,"Unknown lesson")
    l=LESSONS[doc]
    if l['track'] in ('javascript','java'):limit_runs(req)
    checks=check_code(l,data.html,data.css)
    if not all(x['passed'] for x in checks) or data.answer!=l['quiz']['answer']:
        raise HTTPException(400,"Pass the code checks and knowledge check before completing this lesson.")
    stamp=datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO progress VALUES (?,?,?)",(uid,doc,stamp))
        db.execute("INSERT INTO drafts VALUES (?,?,?,?,?) ON CONFLICT(user_id,document_id) DO UPDATE SET html=excluded.html,css=excluded.css,updated_at=excluded.updated_at",(uid,doc,data.html,data.css,stamp))
    return dict(completed=True,lesson_id=doc,completed_at=stamp)

@app.post('/api/validate-completion/{doc}')
def validate_completion(doc:str,data:Attempt,req:Request):
    # Stateless validation: no login or server record needed for HTML/CSS.
    if doc not in LESSONS:raise HTTPException(404,'Unknown lesson')
    lesson=LESSONS[doc]
    if data.answer!=lesson['quiz']['answer']:raise HTTPException(400,'Pass the knowledge check before completing this lesson.')
    if lesson['track'] in ('javascript','java'):limit_runs(req)
    checks=check_code(lesson,data.html,data.css)
    if not all(c['passed'] for c in checks):raise HTTPException(400,'Pass the code checks before completing this lesson.')
    return dict(valid=True,lesson_id=doc)

@app.get('/api/export')
def export(req:Request):
    s=state(req)
    if not s['user']:raise HTTPException(401,"Sign in to export saved data.")
    return Response(json.dumps(s,indent=2),media_type='application/json',headers={'Content-Disposition':'attachment; filename="x-verse-progress.json"'})

app.mount('/assets',StaticFiles(directory=ROOT/'frontend/dist/assets',check_dir=False),name="assets")
@app.get('/favicon.svg')
def favicon():
    return FileResponse(ROOT/'frontend/public/favicon.svg')
@app.get('/{path:path}')
def spa(path:str):
    if path.startswith('api/'):raise HTTPException(404)
    return FileResponse(ROOT/'frontend/dist/index.html')