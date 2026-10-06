"""Stateless browser-mode contract; no provider credentials or database."""
import os,tempfile
from pathlib import Path
folder=tempfile.TemporaryDirectory()
os.environ.update(STORAGE_MODE='browser',AUTH_MODE='supabase',RUNNER_MODE='disabled',
                  SQLITE_PATH=folder.name+'/not-created/academy.sqlite',
                  ALLOWED_ORIGINS='https://frontend.example')
os.environ.pop('SUPABASE_URL',None)
os.environ.pop('SUPABASE_PUBLISHABLE_KEY',None)
from fastapi.testclient import TestClient
import server
with TestClient(server.app) as c:
    assert c.get('/readyz').status_code==204
    config=c.get('/api/config').json()
    assert config['storage_mode']=='browser' and not config['auth_configured']
    for lesson in server.DATA['lessons']:
        if lesson['track'] not in ('html','css'):continue
        body=dict(html=lesson['solution_html'],css=lesson['solution_css'],answer=lesson['quiz']['answer'])
        r=c.post('/api/validate-completion/'+lesson['id'],json=body)
        assert r.status_code==200,(lesson['id'],r.text)
        body['answer']=(body['answer']+1)%len(lesson['quiz']['options'])
        assert c.post('/api/validate-completion/'+lesson['id'],json=body).status_code==400
    body=dict(html='<h1>not saved server side</h1>',css='')
    assert c.put('/api/drafts/playground',json=body).status_code==409
    assert c.post('/api/complete/'+server.DATA['lessons'][0]['id'],json={**body,'answer':0}).status_code==409
    assert c.get('/api/state').json()['user'] is None
    assert c.get('/api/export').status_code==401
    forged={'X-PromptQL-Visitor-Token':'x.eyJzdWIiOiJhZG1pbiJ9.x'}
    assert c.get('/api/state',headers=forged).json()['user'] is None
    assert c.post('/api/run',json={'language':'java','source':'code'}).status_code==401
    headers={'Origin':'https://frontend.example','Sec-Fetch-Site':'cross-site'}
    lesson=server.DATA['lessons'][0]
    assert c.post('/api/check/'+lesson['id'],json={'html':lesson['solution_html'],'css':lesson['solution_css']},headers=headers).status_code==200
    assert c.post('/api/check/'+lesson['id'],json=body,headers={**headers,'Origin':'https://evil.example'}).status_code==403
assert not Path(os.environ['SQLITE_PATH']).parent.exists()
print('PASS 46 unauthenticated HTML/CSS completion checks; wrong quiz rejected; server writes blocked; exact CORS; legacy data private; no SQLite directory/file created.')
folder.cleanup()