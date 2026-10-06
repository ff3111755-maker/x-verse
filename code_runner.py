"""Disposable, networkless Docker execution. No host paths, tokens, or app data enter containers."""
import os,selectors,subprocess,tempfile,threading,time,uuid
LIMIT=32768
DOCKER_ENV={'PATH':'/usr/local/bin:/usr/bin:/bin','HOME':'/tmp','DOCKER_CONFIG':'/tmp/xverse-docker-config'}
SLOTS=threading.BoundedSemaphore(2)
IMAGES={'javascript':'xverse-javascript:1','java':'eclipse-temurin:21-jdk'}
def run_code(language,source):
    if language not in IMAGES:return dict(stdout='',stderr='Unsupported language',exit_code=1,timed_out=False)
    if not SLOTS.acquire(blocking=False):return dict(stdout='',stderr='Both runners are busy. Try again in a moment.',exit_code=1,timed_out=False)
    name='xverse-'+uuid.uuid4().hex
    started=time.monotonic()
    process=None
    out={'stdout':bytearray(),'stderr':bytearray()}
    timed_out=False
    truncated=False
    try:
        command=['docker','run','--rm','-i','--name',name,'--network=none','--read-only',
                 '--cap-drop=ALL','--security-opt=no-new-privileges','--pids-limit=64',
                 '--memory=384m','--memory-swap=384m','--cpus=0.75','--user=65534:65534',
                 '--tmpfs=/tmp:rw,nosuid,nodev,size=48m,mode=1777',
                 '--ulimit=nofile=128:128','--ulimit=fsize=33554432:33554432',
                 '--log-driver=none','--env=HOME=/tmp','--workdir=/tmp',IMAGES[language]]
        if language=='java':
            command+=['sh','-c','cat > Main.java && javac -J-Xmx128m -J-XX:ActiveProcessorCount=1 Main.java && java -Xmx128m -XX:ActiveProcessorCount=1 -XX:+UseSerialGC -XX:MaxMetaspaceSize=96m Main']
        with tempfile.TemporaryFile() as inp:
            inp.write(source.encode());inp.seek(0)
            process=subprocess.Popen(command,stdin=inp,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=DOCKER_ENV)
            sel=selectors.DefaultSelector()
            for label,pipe in [('stdout',process.stdout),('stderr',process.stderr)]:
                os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ,label)
            while sel.get_map():
                if time.monotonic()-started>15:
                    timed_out=True;break
                for key,_ in sel.select(.1):
                    chunk=os.read(key.fileobj.fileno(),4096)
                    if not chunk:sel.unregister(key.fileobj);continue
                    room=LIMIT-sum(len(x) for x in out.values())
                    out[key.data]+=chunk[:max(room,0)]
                    if len(chunk)>room:truncated=True;break
                if truncated:break
            sel.close()
            if timed_out or truncated:
                subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=4,env=DOCKER_ENV)
                process.kill()
            try:code=process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill();code=-1
        stdout=out['stdout'].decode(errors='replace');stderr=out['stderr'].decode(errors='replace')
        if timed_out:stderr+='\nStopped after 15 seconds. Check for an infinite loop or a blocking operation.'
        if truncated:stderr+='\nStopped: output exceeded 32 KB.'
        return dict(stdout=stdout,stderr=stderr.strip(),exit_code=code if not (timed_out or truncated) else 124,
                    timed_out=timed_out,truncated=truncated,duration_ms=round((time.monotonic()-started)*1000))
    except Exception:
        return dict(stdout='',stderr='The isolated runner is unavailable. Please try again later.',exit_code=1,timed_out=False)
    finally:
        if process and process.poll() is None:process.kill()
        try:subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=4,env=DOCKER_ENV)
        except Exception:pass
        SLOTS.release()