import {configureCatalog,readLocalState,saveLocalDraft,completeLocal,exportLocal} from './browser-store.js';
import {createClient} from '@supabase/supabase-js';
const base=(import.meta.env.VITE_API_BASE_URL||'').replace(/\/+$/,'');
if(base && (!/^https:\/\//.test(base) && !(import.meta.env.DEV && /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(base))))throw new Error('VITE_API_BASE_URL must be an HTTPS backend URL.');
let curriculum=null;
export const isBrowserStorage=()=>config?.storage_mode==='browser';
let config=null,client=null,session=null,initializing=null;
export const getConfig=()=>config;
export const getAuthClient=()=>client;
export async function initializeAPI(){
 if(initializing)return initializing;
 initializing=(async()=>{
  const r=await fetch(base+'/api/config',{credentials:'omit'});
  if(!r.ok)throw new Error('Cannot reach the backend. Check VITE_API_BASE_URL and CORS settings.');
  config=await r.json();
  if(config.storage_mode==='browser'){
   const cr=await fetch(base+'/api/curriculum',{credentials:'omit'});
   if(!cr.ok)throw new Error('Cannot load the curriculum. Please retry.');
   curriculum=await cr.json();configureCatalog(curriculum);
  }
  if(config.storage_mode!=='browser'&&config.auth_mode==='supabase'&&config.auth_configured){
   client=createClient(config.supabase_url,config.supabase_publishable_key,{
    auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true,flowType:'pkce',storageKey:'xverse-auth-'+new URL(config.supabase_url).host}
   });
   session=(await client.auth.getSession()).data.session;
   client.auth.onAuthStateChange((event,next)=>{
    session=next;
    if(event!=='TOKEN_REFRESHED'&&event!=='INITIAL_SESSION')window.dispatchEvent(new CustomEvent('xverse-auth-changed'));
   });
  }
  return config;
 })();
 try{return await initializing}catch(e){initializing=null;throw e}
}
export async function apiFetch(path,options={}){
 if(isBrowserStorage()&&!config.browser_runner_available){
  const lessonId=path.startsWith('/api/check/')?path.slice('/api/check/'.length):path.startsWith('/api/validate-completion/')?path.slice('/api/validate-completion/'.length):null;
  const track=curriculum?.lessons.find(l=>l.id===lessonId)?.track;
  if(path==='/api/run'||['javascript','java'].includes(track)){
   return new Response(JSON.stringify({detail:'Execution is unavailable in this browser-only deployment. Your code can still be saved and downloaded. Java/JavaScript execution and completion need a configured, authenticated runner.'}),{status:503,headers:{'Content-Type':'application/json'}});
  }
 }
 if(isBrowserStorage()&&path.startsWith('/api/drafts/')&&options.method==='PUT'){
  const saved=await saveLocalDraft(path.slice('/api/drafts/'.length),JSON.parse(options.body));
  return new Response(JSON.stringify(saved),{headers:{'Content-Type':'application/json'}});
 }
 const {expectedUserId,...rest}=options;
 const headers=new Headers(rest.headers||{});
 if(!isBrowserStorage()&&config?.auth_mode==='supabase'){
  if(expectedUserId && session?.user?.id!==expectedUserId)throw new Error('Account changed. This draft was not sent.');
  if(session?.access_token)headers.set('Authorization','Bearer '+session.access_token);
 }
 if(rest.body&&!headers.has('Content-Type'))headers.set('Content-Type','application/json');
 // No cookie authentication, including across a Vercel-to-Render boundary.
 const response=await fetch(base+path,{...rest,headers,credentials:'omit'});
 if(!isBrowserStorage()&&config?.auth_mode==='supabase'&&expectedUserId&&session?.user?.id!==expectedUserId)throw new Error('Account changed. Ignored an earlier save response.');
 return response;
}
export async function api(url,options={}){
 await initializeAPI();
 if(isBrowserStorage()){
  if(url==='/curriculum')return curriculum;
  if(url==='/state')return readLocalState();
  if(url==='/export')return exportLocal();
  if(url.startsWith('/complete/')){
   const id=url.slice('/complete/'.length),body=JSON.parse(options.body);
   const response=await apiFetch('/api/validate-completion/'+id,options);
   const validation=await response.json();
   if(!response.ok)throw new Error(validation.detail||'Checks did not pass.');
   return completeLocal(id,body);
  }
 }
 if(url==='/export-account')url='/export';
 const r=await apiFetch('/api'+url,options);
 let data;try{data=await r.json()}catch{throw new Error('The API returned an unexpected response. Check the deployment URL.')}
 if(!r.ok)throw new Error(typeof data.detail==='string'?data.detail:'The request could not be completed.');
 return data;
}