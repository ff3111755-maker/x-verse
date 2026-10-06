import React,{useRef,useState} from 'react';
import {Download,Upload,HardDrive,ShieldCheck} from 'lucide-react';
import {api,getConfig} from './api-client.js';
import {exportLocal,parseBackupFile,mergeBackup,validateBackup} from './browser-store.js';

export function StoragePanel(){
 const file=useRef(null);
 const [pending,setPending]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 async function perform(fn){
  setBusy(true);setError('');setNotice('');
  try{await fn()}catch(e){setError(e.message)}finally{setBusy(false)}
 }
 async function download(){
  const backup=await exportLocal();
  const url=URL.createObjectURL(new Blob([JSON.stringify(backup,null,2)],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download='x-verse-backup-'+new Date().toISOString().slice(0,10)+'.json';a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1500);
  setNotice('Backup downloaded. Keep it somewhere safe; it contains your code.');
 }
 return <section className="storage-panel" aria-labelledby="storage-title">
  <h3 id="storage-title"><HardDrive size={19}/> Saved in this browser</h3>
  <p>Progress and code drafts save automatically on this device. No account or database subscription needed.</p>
  <p className="muted small">This is one shared learning profile per browser and website address. It is not private from others using the same browser profile. Clearing site data, private browsing, or browser storage cleanup can remove it. Keep a backup before changing devices or domains.</p>
  <div className="storage-buttons"><button className="btn secondary" disabled={busy} onClick={()=>perform(download)}><Download size={15}/> Export backup</button>
  <button className="btn secondary" disabled={busy} onClick={()=>file.current?.click()}><Upload size={15}/> Import backup</button></div>
  <input ref={file} className="sr-only" type="file" accept=".json,application/json" aria-label="Choose backup file" onChange={e=>{const f=e.target.files?.[0];e.target.value='';if(f)perform(async()=>{setPending(null);setPending(await parseBackupFile(f))})}}/>
  {getConfig()?.legacy_import_available&&<button className="text-btn legacy-import" disabled={busy} onClick={()=>perform(async()=>{setPending(null);const state=await api('/export-account');setPending(validateBackup(state))})}>Import my previously saved account data</button>}
  {pending&&<div className="import-preview"><h4>Review your import</h4><p>{pending.completed.length} completed lessons · {Object.keys(pending.drafts).length} drafts</p><p className="muted small">Existing completions stay. For matching drafts, the newer timestamp wins; your current edits are saved before merging. Export first if you want an extra recovery copy.</p>
  <div className="storage-buttons"><button className="btn" disabled={busy} onClick={()=>perform(async()=>{const r=await mergeBackup(pending);setPending(null);setNotice(`Restored: ${r.added} new completions, ${r.updated} drafts. Kept ${r.kept} newer or identical local drafts.`)})}>Merge backup</button><button className="btn secondary" disabled={busy} onClick={()=>setPending(null)}>Cancel import</button></div></div>}
  <button className="text-btn legacy-import" disabled={busy} onClick={()=>perform(async()=>{
   if(!navigator.storage?.persist){setNotice('This browser does not support storage protection. Export backups regularly.');return;}
   const yes=await navigator.storage.persist();
   setNotice(yes?'Storage protection granted. Clearing site data can still erase it—keep backups.':'Storage protection was not granted. Saving still works; keep regular backups.');
  })}><ShieldCheck size={14}/> Ask browser to protect saved data</button>
  {busy&&<p className="muted small" role="status">Working…</p>}
  {error&&<p className="account-error" role="alert">{error} No import has been applied unless confirmation succeeded.</p>}
  {notice&&<p className="account-message" role="status">{notice}</p>}
 </section>
}