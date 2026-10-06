"""Dedicated Docker-host API. Bind to loopback, publish through TLS, keep the key server-only."""
import os,secrets
from fastapi import FastAPI,Header,HTTPException,Depends
from pydantic import BaseModel,Field
from code_runner import run_code

KEY=os.getenv('RUNNER_API_KEY','')
if len(KEY)<32:raise RuntimeError('Set a random RUNNER_API_KEY of at least 32 characters')
app=FastAPI(docs_url=None,redoc_url=None,openapi_url=None)
def authorize(authorization:str=Header(default='')):
    if not secrets.compare_digest(authorization,'Bearer '+KEY):raise HTTPException(401,'Unauthorized')
class Program(BaseModel):
    language:str
    source:str=Field(max_length=100000)
@app.get('/readyz',dependencies=[Depends(authorize)])
def ready():
    return {'status':'ready'}
@app.post('/v1/run',dependencies=[Depends(authorize)])
def execute(data:Program):
    if data.language not in ('javascript','java'):raise HTTPException(400,'Unsupported language')
    return run_code(data.language,data.source)