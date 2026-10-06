"""Execution adapter for Docker-capable hosts or a dedicated HTTPS runner."""
import os,json,threading
import httpx
from fastapi import HTTPException
from hosting import RUNNER_MODE
REMOTE_SLOTS=threading.BoundedSemaphore(2)

def run_code(language,source):
    if RUNNER_MODE=='disabled':
        raise HTTPException(503,'Code execution is not configured on this deployment. Connect a separate runner to run Java and JavaScript. Lessons and HTML/CSS practice remain available.')
    if RUNNER_MODE=='docker':
        from code_runner import run_code as local
        return local(language,source)
    if not REMOTE_SLOTS.acquire(blocking=False):raise HTTPException(429,'Both runners are busy. Try again shortly.')
    try:
        # URL and credential are server-configured, never supplied by user code.
        with httpx.stream('POST',os.environ['RUNNER_URL'].rstrip('/')+'/v1/run',
                          headers={'Authorization':'Bearer '+os.environ['RUNNER_API_KEY']},
                          json={'language':language,'source':source},timeout=httpx.Timeout(23,connect=5),follow_redirects=False) as r:
            if r.status_code==429:raise HTTPException(429,'The runner is busy. Try again shortly.')
            if r.status_code!=200:raise HTTPException(503,'The execution service is unavailable. Check the runner configuration.')
            body=bytearray()
            for chunk in r.iter_bytes():
                body+=chunk
                if len(body)>262144:raise HTTPException(502,'The runner returned an oversized response.')
        result=json.loads(body)
        if not isinstance(result,dict) or not isinstance(result.get('stdout'),str) or not isinstance(result.get('stderr'),str) or not isinstance(result.get('exit_code'),int):
            raise ValueError()
        return {k:result[k] for k in ('stdout','stderr','exit_code','timed_out','truncated','duration_ms') if k in result}
    except httpx.TimeoutException:raise HTTPException(504,'The execution service timed out.')
    except (httpx.HTTPError,ValueError):raise HTTPException(503,'The execution service is unavailable.')
    finally:REMOTE_SLOTS.release()