"""Offline deployment tests; provider authentication is mocked, never real user credentials."""
import os,tempfile,json,base64
from unittest.mock import patch
from pathlib import Path
testdir=tempfile.TemporaryDirectory()
os.environ.update(STORAGE_MODE='server',AUTH_MODE='supabase',RUNNER_MODE='disabled',SQLITE_PATH=testdir.name+'/academy.sqlite',
                  SUPABASE_URL='https://test-project.supabase.co',SUPABASE_PUBLISHABLE_KEY='sb_publishable_test_only',
                  ALLOWED_ORIGINS='https://xverse-test.vercel.app')
from fastapi.testclient import TestClient
import httpx,server,hosting

def fake_verify(url,headers,**kwargs):
    token=headers['Authorization']
    if token=='Bearer valid-user-a':return httpx.Response(200,json={'id':'user-a','email':'a@example.test','user_metadata':{'display_name':'Test A'}})
    if token=='Bearer valid-user-b':return httpx.Response(200,json={'id':'user-b','email':'b@example.test'})
    return httpx.Response(401,json={'error':'Invalid token'})

with patch.object(hosting.httpx,'get',side_effect=fake_verify), TestClient(server.app) as c:
    origin='https://xverse-test.vercel.app'
    h={'Authorization':'Bearer valid-user-a','Origin':origin,'Sec-Fetch-Site':'cross-site'}
    config=c.get('/api/config').json()
    assert config['auth_mode']=='supabase' and not config['runner_enabled']
    assert 'RUNNER_API_KEY' not in json.dumps(config)
    fake='x.'+base64.urlsafe_b64encode(b'{"sub":"user-a"}').decode().rstrip('=')+'.x'
    assert c.get('/api/state',headers={'X-PromptQL-Visitor-Token':fake}).json()['user'] is None
    assert c.get('/api/state',headers={'Authorization':'Bearer forged'}).status_code==401
    assert c.get('/api/state',headers=h).json()['user']['id']=='user-a'
    pre=c.options('/api/drafts/playground',headers={'Origin':origin,'Access-Control-Request-Method':'PUT','Access-Control-Request-Headers':'authorization,content-type'})
    assert pre.status_code==200 and pre.headers['access-control-allow-origin']==origin
    assert 'access-control-allow-credentials' not in pre.headers
    draft={'html':'<h1>private</h1>','css':''}
    saved=c.put('/api/drafts/playground',headers=h,json=draft)
    assert saved.status_code==200 and saved.headers['access-control-allow-origin']==origin
    assert c.get('/api/state',headers=h).json()['drafts']['playground']['html']==draft['html']
    assert c.get('/api/state',headers={'Authorization':'Bearer valid-user-b'}).json()['drafts']=={}
    assert c.put('/api/drafts/playground',headers={**h,'Origin':'https://evil.example'},json=draft).status_code==403
    assert c.post('/api/run',headers=h,json={'language':'java','source':'unused'}).status_code==503
    assert c.post('/api/run',json={'language':'java','source':'unused'}).status_code==401
    lesson=server.DATA['lessons'][0]
    r=c.post('/api/complete/'+lesson['id'],headers=h,json={'html':lesson['solution_html'],'css':lesson['solution_css'],'answer':lesson['quiz']['answer']})
    assert r.status_code==200
print('PASS default standalone auth verifies bearer with provider; spoofed PromptQL identity ignored; account isolation; CORS; disabled-runner notice; HTML completion.')
testdir.cleanup()