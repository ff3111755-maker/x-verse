"""Standalone hosting configuration and verified identities.

PromptQL header trust is opt-in and must ONLY be used behind its trusted proxy.
Default standalone mode verifies every bearer token with Supabase Auth.
"""
import os,base64,json
from urllib.parse import urlparse
import httpx
from fastapi import HTTPException

STORAGE_MODE=os.getenv('STORAGE_MODE','browser')
AUTH_MODE=os.getenv('AUTH_MODE','supabase')
RUNNER_MODE=os.getenv('RUNNER_MODE','disabled')
SUPABASE_URL=os.getenv('SUPABASE_URL','').rstrip('/')
SUPABASE_KEY=os.getenv('SUPABASE_PUBLISHABLE_KEY','')
ORIGINS=[s.strip().rstrip('/') for s in os.getenv('ALLOWED_ORIGINS','').split(',') if s.strip()]
DEV=os.getenv('ALLOW_INSECURE_LOCAL','false').lower()=='true'

def safe_url(value):
    parsed=urlparse(value)
    return parsed.scheme=='https' and bool(parsed.hostname) and not parsed.username and not parsed.password and not parsed.query and not parsed.fragment

def validate_settings():
    if STORAGE_MODE not in ('browser','server'):raise RuntimeError('STORAGE_MODE must be browser or server')
    if AUTH_MODE not in ('supabase','promptql'):raise RuntimeError('AUTH_MODE must be supabase or promptql')
    if RUNNER_MODE not in ('disabled','remote','docker'):raise RuntimeError('Unknown RUNNER_MODE')
    for origin in ORIGINS:
        parsed=urlparse(origin)
        if origin=='*' or parsed.path or not (safe_url(origin) or (DEV and parsed.scheme=='http' and parsed.hostname in ('localhost','127.0.0.1'))):
            raise RuntimeError('ALLOWED_ORIGINS must contain exact HTTPS origins, without paths or wildcard')
    if bool(SUPABASE_URL)!=bool(SUPABASE_KEY):raise RuntimeError('Set both SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY')
    if SUPABASE_URL and not safe_url(SUPABASE_URL):raise RuntimeError('SUPABASE_URL must be HTTPS')
    if SUPABASE_KEY:
        # Prevent an operator accidentally publishing a service-role/admin credential.
        public=SUPABASE_KEY.startswith('sb_publishable_')
        if not public:
            try:
                part=SUPABASE_KEY.split('.')[1]
                public=json.loads(base64.urlsafe_b64decode(part+'='*(-len(part)%4))).get('role')=='anon'
            except Exception:pass
        if not public:raise RuntimeError('Use the Supabase publishable key or legacy anon key, NEVER a secret/service-role key')
    if RUNNER_MODE=='remote':
        url=os.getenv('RUNNER_URL','').rstrip('/')
        if not (safe_url(url) or (DEV and urlparse(url).hostname in ('localhost','127.0.0.1') and url.startswith('http://'))):
            raise RuntimeError('RUNNER_URL must be an HTTPS endpoint')
        if len(os.getenv('RUNNER_API_KEY',''))<32:raise RuntimeError('RUNNER_API_KEY must be at least 32 characters')

validate_settings()

def public_config():
    return dict(storage_mode=STORAGE_MODE,auth_mode=AUTH_MODE,auth_configured=bool(SUPABASE_URL and SUPABASE_KEY) if AUTH_MODE=='supabase' else True,
                supabase_url=SUPABASE_URL if AUTH_MODE=='supabase' else '',
                supabase_publishable_key=SUPABASE_KEY if AUTH_MODE=='supabase' else '',
                runner_enabled=RUNNER_MODE!='disabled',
                browser_runner_available=RUNNER_MODE!='disabled' and AUTH_MODE=='promptql',
                legacy_import_available=STORAGE_MODE=='browser' and AUTH_MODE=='promptql',
                runner_message='' if RUNNER_MODE!='disabled' else 'Code execution is not configured on this deployment. You can still read lessons, edit code, download programs, and practice HTML/CSS.')

def visitor(req):
    if AUTH_MODE=='promptql':
        token=req.headers.get('x-promptql-visitor-token')
        if not token:return None
        try:
            payload=token.split('.')[1]
            claims=json.loads(base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)))
            uid=claims.get('sub')
            if not isinstance(uid,str) or not uid:return None
            return dict(id=uid,name=claims.get('display_name') or 'Learner')
        except Exception:return None
    # Standalone mode ignores all PromptQL headers; a user-controlled claim never identifies a learner.
    auth=req.headers.get('authorization','')
    if not auth.startswith('Bearer '):return None
    token=auth[7:]
    if not token or len(token)>8192:raise HTTPException(401,'Invalid sign-in token')
    if not SUPABASE_URL or not SUPABASE_KEY:raise HTTPException(503,'Sign-in is not configured on this deployment')
    try:
        r=httpx.get(SUPABASE_URL+'/auth/v1/user',headers={'Authorization':'Bearer '+token,'apikey':SUPABASE_KEY},timeout=8,follow_redirects=False)
    except httpx.HTTPError:raise HTTPException(503,'Sign-in service is temporarily unavailable')
    if r.status_code in (401,403):raise HTTPException(401,'Your session expired. Please sign in again.')
    if r.status_code!=200:raise HTTPException(503,'Unable to verify your sign-in right now')
    try:
        user=r.json()
        if not isinstance(user.get('id'),str) or not user['id']:raise ValueError()
        metadata=user.get('user_metadata') or {}
        name=metadata.get('display_name') or (user.get('email') or 'Learner').split('@')[0]
        return dict(id=user['id'],name=str(name)[:80])
    except (ValueError,TypeError):raise HTTPException(401,'Invalid account response')

def require_user(req):
    v=visitor(req)
    if not v:
        raise HTTPException(401,'Sign in to save progress and drafts.' if AUTH_MODE=='supabase' else 'Open this app through PromptQL to save your progress. You can still explore and practice.')
    return v['id']