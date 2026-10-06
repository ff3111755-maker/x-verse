"""Prepare the Render disk mount, then drop privileges before serving requests."""
import os,pwd
from pathlib import Path
path=Path(os.getenv('SQLITE_PATH','/var/data/academy.sqlite'))
if not path.is_absolute():raise SystemExit('SQLITE_PATH must be an absolute path')
if os.getuid()==0:
    user=pwd.getpwnam('app')
    if os.getenv('STORAGE_MODE','browser')=='server':
        path.parent.mkdir(parents=True,exist_ok=True)
        os.chown(path.parent,user.pw_uid,user.pw_gid)
        for suffix in ('','-wal','-shm'):
            file=Path(str(path)+suffix)
            if file.exists() and not file.is_symlink():os.chown(file,user.pw_uid,user.pw_gid)
    os.setgroups([])
    os.setgid(user.pw_gid)
    os.setuid(user.pw_uid)
os.umask(0o077)
os.execvp('uvicorn',['uvicorn','server:app','--host','0.0.0.0','--port',os.getenv('PORT','10000'),'--workers','1','--no-access-log'])