import React,{useState} from 'react';
import {LogIn,LogOut,Mail,Loader2} from 'lucide-react';
import {getConfig,getAuthClient,isBrowserStorage} from './api-client.js';
export function AccountPanel({user}){
 const config=getConfig(),client=getAuthClient();
 const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[mode,setMode]=useState('signin'),[busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
 if(config?.auth_mode!=='supabase')return null;
 async function action(kind){
  setBusy(true);setError('');setMessage('');
  try{
   let result;
   if(kind==='signout')result=await client.auth.signOut();
   else if(kind==='link'){
    if(!email.trim())throw new Error('Enter your email address first.');
    result=await client.auth.signInWithOtp({email:email.trim(),options:{emailRedirectTo:window.location.origin,shouldCreateUser:false}});
    if(!result.error)setMessage('If an account exists, a sign-in link will be sent. Open it in this browser.');
   }else if(mode==='signup'){
    result=await client.auth.signUp({email:email.trim(),password,options:{emailRedirectTo:window.location.origin}});
    if(!result.error&&!result.data.session)setMessage('Check your email to confirm your account, then sign in.');
   }else result=await client.auth.signInWithPassword({email:email.trim(),password});
   if(result?.error)throw result.error;
   setPassword('');
  }catch(e){setError(e.message)}finally{setBusy(false)}
 }
 return <section className="account-panel" aria-labelledby="account-title"><h3 id="account-title">Your account</h3>
 {!config.auth_configured?<p className="muted">Sign-in hasn’t been configured yet. Set the Supabase URL and publishable key on the backend to enable saved progress.</p>:user?<><p>Signed in as <strong>{user.name}</strong>. Progress and drafts are private to your account.</p><p className="muted small">Wait for “Saved” before signing out. Unsaved edits will not transfer between accounts.</p><button className="btn secondary" disabled={busy} onClick={()=>action('signout')}><LogOut size={14}/> Sign out</button></>:<>
 <div className="segmented"><button aria-pressed={mode==='signin'} className={mode==='signin'?'active':''} onClick={()=>{setMode('signin');setError('')}}>Sign in</button><button aria-pressed={mode==='signup'} className={mode==='signup'?'active':''} onClick={()=>{setMode('signup');setError('')}}>Create account</button></div>
 <form onSubmit={e=>{e.preventDefault();action('password')}}><label>Email<input type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" autoComplete={mode==='signup'?'new-password':'current-password'} minLength={mode==='signup'?12:undefined} maxLength={128} required value={password} onChange={e=>setPassword(e.target.value)}/></label>{mode==='signup'&&<small>Use at least 12 characters. Confirm your email before signing in.</small>}<button className="btn" disabled={busy}>{busy?<Loader2 size={15} className="spin"/>:<LogIn size={15}/>} {mode==='signup'?'Create account':'Sign in'}</button></form>
 <button className="text-btn" disabled={busy} onClick={()=>action('link')}><Mail size={14}/> Existing account? Email me a sign-in link</button>
 <p className="muted small">Authentication is handled by Supabase. New accounts start with their own progress; existing PromptQL records are not automatically linked.</p>
 </>}
 {error&&<p className="account-error" role="alert">{error}</p>}{message&&<p className="account-message" role="status">{message}</p>}
 </section>
}
export function HostingNotice({onSignIn,user}){
 const c=getConfig();if(isBrowserStorage())return <div className="hosting-notice"><p>Auto-saved on this device. <button className="text-btn" onClick={onSignIn}>Backups & storage</button></p>{!c.browser_runner_available&&<p>Java and JavaScript execution needs a configured, protected runner. You can still read lessons, save code, and download programs.</p>}</div>;if(c?.auth_mode!=='supabase')return null;
 return <div className="hosting-notice">{!user&&<p><button className="text-btn" onClick={onSignIn}>Sign in</button> to save progress, drafts, and run programs.</p>}{!c.runner_enabled&&<p>{c.runner_message}</p>}</div>
}