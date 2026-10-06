"""Roundtrip test on loopback with a temporary key; no external deployment."""
import os,secrets,socket,subprocess,time,sys
import httpx
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
key=secrets.token_urlsafe(48)
env={**os.environ,'RUNNER_API_KEY':key}
p=subprocess.Popen([sys.executable,'-m','uvicorn','runner_server:app','--host','127.0.0.1','--port',str(port),'--no-access-log'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    url=f'http://127.0.0.1:{port}'
    for _ in range(40):
        try:
            r=httpx.get(url+'/readyz')
            if r.status_code==401:break
        except httpx.HTTPError:pass
        time.sleep(.1)
    assert httpx.post(url+'/v1/run',json={'language':'javascript','source':'console.log(1)'}).status_code==401
    os.environ.update(RUNNER_MODE='remote',RUNNER_URL=url,RUNNER_API_KEY=key,ALLOW_INSECURE_LOCAL='true',AUTH_MODE='supabase')
    from runner_gateway import run_code
    for lang,code,expected in [('javascript','console.log("Remote JS ready");','Remote JS ready'),
                              ('java','public class Main {public static void main(String[] a){System.out.println("Remote Java ready");}}','Remote Java ready')]:
        r=run_code(lang,code)
        assert r['exit_code']==0 and r['stdout'].strip()==expected,r
    print('PASS authenticated remote gateway: JavaScript and Java, unauthorized rejection. Loopback test only; production requires TLS.')
finally:
    p.terminate();p.wait(timeout=5)