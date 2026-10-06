import {apiFetch} from './api-client.js';
import React,{useState,useEffect,useRef} from 'react';
import {Play,Download,Copy,Save,RotateCcw,Loader2,Terminal} from 'lucide-react';
export const languageName=t=>t==='javascript'?'JavaScript':t==='java'?'Java':t==='html'?'HTML':'CSS';
export const JS_STARTER='// Run JavaScript in Node.js 22.\nconst name = "X Verse";\nconsole.log(`Hello, ${name}!`);\n';
export const JAVA_STARTER='public class Main {\n  public static void main(String[] args) {\n    System.out.println("Hello, X Verse!");\n  }\n}\n';
export function ProgramLab({docId,language,initialHtml,user,onDraft,toast,onCode,execution}){
 const [source,setSource]=useState(initialHtml),[result,setResult]=useState(null),[running,setRunning]=useState(false),[saved,setSaved]=useState(''),[reset,setReset]=useState(false);
 const latest=useRef(source),original=useRef(initialHtml),dirty=useRef(false),release=useRef(false),initial=useRef(true),editor=useRef(null);
 const label=languageName(language),filename=language==='java'?'Main.java':'main.mjs';
 async function persist(){
  if(!user){setSaved('Session only · download to keep');return;}
  const snapshot=latest.current;
  try{
   const r=await apiFetch('/api/drafts/'+docId,{expectedUserId:user?.id,method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({html:snapshot,css:''})});
   const d=await r.json();if(!r.ok)throw new Error(d.detail||'Save failed');
   if(latest.current===snapshot){dirty.current=false;setSaved('Saved');}
  }catch(e){setSaved('Not saved');toast(e.message);}
 }
 useEffect(()=>{
  latest.current=source;onCode?.({html:source,css:''});setResult(null);
  if(initial.current){initial.current=false;return;}
  dirty.current=true;onDraft(docId,{html:source,css:''});setSaved('Unsaved changes');
  const t=setTimeout(persist,1400);return()=>clearTimeout(t);
 },[source]);
 useEffect(()=>{if(execution)setResult(execution)},[execution]);
 useEffect(()=>{
  const flush=()=>{if(dirty.current&&user)apiFetch('/api/drafts/'+docId,{expectedUserId:user?.id,method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({html:latest.current,css:''}),keepalive:true}).catch(()=>{})};
  window.addEventListener('pagehide',flush);return()=>{window.removeEventListener('pagehide',flush);flush()};
 },[]);
 async function run(){
  setRunning(true);setResult(null);const snapshot=latest.current;
  try{
   const r=await apiFetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language,source:snapshot})});
   const d=await r.json();if(!r.ok)throw new Error(d.detail||'Run failed');
   setResult({...d,stale:latest.current!==snapshot});
  }catch(e){setResult({stdout:'',stderr:e.message,exit_code:1})}finally{setRunning(false)}
 }
 const download=()=>{const u=URL.createObjectURL(new Blob([source],{type:'text/plain'}));const a=document.createElement('a');a.href=u;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(u),500)};
 const keyboard=e=>{
  if(e.key==='Escape'){release.current=true;return;}
  if(e.key==='Tab'&&release.current){release.current=false;return;}
  if(e.key==='Tab'&&!e.shiftKey){e.preventDefault();const a=e.target.selectionStart,b=e.target.selectionEnd;setSource(source.slice(0,a)+'  '+source.slice(b));requestAnimationFrame(()=>editor.current?.setSelectionRange(a+2,a+2))}
  if((e.ctrlKey||e.metaKey)&&e.key==='s'){e.preventDefault();persist();}
 };
 return <div className="program-lab code-lab">
  <div className="lab-toolbar"><span className="program-filename"><Terminal size={16}/>{filename}</span><div className="lab-actions">
   <button className="icon-button" aria-label="Copy program" onClick={async()=>{try{await navigator.clipboard.writeText(source);toast('Code copied')}catch{toast('Select the code to copy it.')}}}><Copy size={15}/></button>
   <button className="icon-button" aria-label="Download program" onClick={download}><Download size={15}/></button>
   <button className="icon-button" aria-label="Reset program" onClick={()=>setReset(true)}><RotateCcw size={15}/></button>
   <button className="btn run-program" disabled={running} onClick={run}>{running?<Loader2 className="spin" size={14}/>:<Play size={14}/>} {running?'Running…':'Run '+label}</button>
  </div></div>
  {reset&&<div className="program-reset" role="group" aria-label="Confirm reset"><p>Replace your edits with the code loaded when this editor opened?</p><button className="btn secondary" onClick={()=>setReset(false)}>Keep editing</button><button className="btn" onClick={()=>{setSource(original.current);setReset(false)}}>Reset</button></div>}
  <div className="program-columns"><div className="editor-pane"><div className="editor-meta"><span>{label} · {language==='java'?'JDK 21':'NODE.JS 22'}</span><span>EDITABLE</span></div><div className="editor-body"><div className="line-numbers" aria-hidden="true">{source.split('\n').map((_,i)=><div key={i}>{i+1}</div>)}</div><textarea ref={editor} spellCheck={false} aria-label={label+' code'} aria-describedby={'help-'+docId} value={source} onChange={e=>setSource(e.target.value)} onKeyDown={keyboard} onScroll={e=>e.target.previousElementSibling.scrollTop=e.target.scrollTop}/></div></div>
  <div className="program-output"><div className="editor-meta"><span>CONSOLE</span><span>{running?'RUNNING':result?(result.exit_code===0?'FINISHED':'ERROR'):'READY'}</span></div><div className="console-scroll" role="log" aria-label="Program output">
  {!result&&!running&&<p>Run your program to see output and errors here.</p>}{running&&<p>Starting an isolated {label} runtime…</p>}
  {result&&<>{result.stale&&<p>Output is from the previous version of your code.</p>}<pre>{result.stdout||(!result.stderr?'Finished with no output.':'')}</pre>{result.stderr&&<pre className="error-output">{result.stderr}</pre>}<small>Exit {result.exit_code}{result.duration_ms!=null?' · '+(result.duration_ms/1000).toFixed(2)+'s':''}</small></>}
  </div></div></div>
  <div className="program-notice" id={'help-'+docId}>{language==='java'?'Use public class Main. Standard library only; no interactive input.':'ES modules supported. document and window use a DOM fixture, not a full browser.'} No network. Temporary files reset after each run. 15-second limit. Esc, then Tab leaves the editor.</div>
  <div className="editor-footer"><span>{saved||(user?'Autosave ready':'Session only · download to keep your code')}</span><button className="text-btn" onClick={persist}><Save size={13}/> Save draft</button></div>
 </div>
}