import base64,json,uuid,sqlite3,httpx
from pathlib import Path
BASE='http://127.0.0.1:8000'
uid='qa-'+str(uuid.uuid4())
other='qa-'+str(uuid.uuid4())
def headers(user):
    # Synthetic identity is only sent to loopback for exercising app logic.
    # The public proxy strips and replaces this header.
    claim=base64.urlsafe_b64encode(json.dumps({'sub':user,'display_name':'QA Developer'}).encode()).decode().rstrip('=')
    return {'X-PromptQL-Visitor-Token':f'test.{claim}.test'}
with httpx.Client(base_url=BASE) as c:
    data=c.get('/api/curriculum').json()
    assert c.get('/readyz').status_code==204
    assert c.get('/api/state').json()['completed']==[]
    l=data['lessons'][0]
    code={'html':l['solution_html'],'css':l['solution_css']}
    assert c.put('/api/drafts/'+l['id'],json=code).status_code==401
    assert c.post('/api/complete/'+l['id'],json={**code,'answer':l['quiz']['answer']}).status_code==401
    assert c.put('/api/drafts/'+l['id'],json={**code,'user_id':other},headers=headers(uid)).status_code==200
    assert l['id'] in c.get('/api/state',headers=headers(uid)).json()['drafts']
    assert c.get('/api/state',headers=headers(other)).json()['drafts']=={}
    assert c.post('/api/complete/'+l['id'],json={**code,'answer':0},headers=headers(uid)).status_code==400
    assert c.post('/api/complete/'+l['id'],json={'html':'','css':'','answer':1},headers=headers(uid)).status_code==400
    for _ in range(2):
        assert c.post('/api/complete/'+l['id'],json={**code,'answer':1},headers=headers(uid)).status_code==200
    assert len(c.get('/api/state',headers=headers(uid)).json()['completed'])==1
    assert c.get('/api/state',headers=headers(other)).json()['completed']==[]
    assert c.get('/api/export').status_code==401
    assert len(c.get('/api/export',headers=headers(uid)).json()['completed'])==1
    assert c.put('/api/drafts/bogus',json=code,headers=headers(uid)).status_code==404
    assert c.put('/api/drafts/playground',json={'html':'a'*100001,'css':''},headers=headers(uid)).status_code==422
    assert c.put('/api/drafts/playground',json=code,headers={**headers(uid),'sec-fetch-site':'cross-site'}).status_code==403
    print('PASS: readiness, anonymous protection, per-user drafts, body identity ignored, per-user completion, idempotency, answer and code validation, export privacy, input limits, CSRF site check.')
with sqlite3.connect(Path(__file__).parent/'data/academy.sqlite') as db:
    for table in ['progress','drafts']:
        db.execute(f'DELETE FROM {table} WHERE user_id IN (?,?)',(uid,other))