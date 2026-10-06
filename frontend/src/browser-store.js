/** Local learning records. Never stores credentials or sends drafts over the network. */
const DB_NAME='xverse-learning-v1';
const MAX_BYTES=50*1024*1024;
let dbPromise,catalog;
export const LOCAL_USER={id:'browser-local',name:'Learner',local:true};
export function configureCatalog(data){catalog=data;}
const storeError=e=>new Error(e?.name==='QuotaExceededError'
 ? 'Browser storage is full. Export a backup and free some space; this change was not saved.'
 : 'Browser saving is unavailable. Allow site storage and avoid private browsing. Your unsaved work is not backed up.');
export function openStore(){
 if(dbPromise)return dbPromise;
 dbPromise=new Promise((resolve,reject)=>{
  if(!globalThis.indexedDB){reject(storeError());return;}
  const req=indexedDB.open(DB_NAME,1);
  req.onupgradeneeded=()=>{
   const db=req.result;
   db.createObjectStore('drafts',{keyPath:'document_id'});
   db.createObjectStore('completed',{keyPath:'lesson_id'});
  };
  req.onerror=()=>reject(storeError(req.error));
  req.onblocked=()=>reject(new Error('Close other X Verse tabs and reload to enable browser saving.'));
  req.onsuccess=()=>{
   req.result.onversionchange=()=>{req.result.close();dbPromise=null};
   resolve(req.result);
  };
 }).catch(e=>{dbPromise=null;throw e});
 return dbPromise;
}
async function transaction(names,mode,fn){
 const db=await openStore();
 return new Promise((resolve,reject)=>{
  const tx=db.transaction(names,mode);
  let result;
  try{result=fn(tx)}catch(e){tx.abort();reject(storeError(e));return;}
  tx.oncomplete=()=>resolve(typeof result==='function'?result():result);
  tx.onerror=()=>reject(storeError(tx.error));
  tx.onabort=()=>reject(storeError(tx.error));
 });
}
function docs(){
 if(!catalog)throw new Error('Load the curriculum before restoring learning data.');
 return new Set([...catalog.lessons.map(l=>l.id),...catalog.projects.map(p=>p.id),'playground','playground-javascript','playground-java']);
}
function validCode(code){
 if(!code||typeof code.html!=='string'||typeof code.css!=='string'||code.html.length>100000||code.css.length>100000)
  throw new Error('Each draft must contain HTML/source and CSS strings of at most 100,000 characters each.');
}
function validDate(value){
 if(typeof value!=='string'||value.length>40||!Number.isFinite(Date.parse(value)))throw new Error('A backup contains an invalid date.');
 return new Date(value).toISOString();
}
export async function readLocalState(){
 return transaction(['drafts','completed'],'readonly',tx=>{
  const drafts=tx.objectStore('drafts').getAll(),completed=tx.objectStore('completed').getAll();
  return ()=>({user:LOCAL_USER,completed:completed.result,drafts:Object.fromEntries(drafts.result.map(({document_id,...d})=>[document_id,d]))});
 });
}
export async function saveLocalDraft(id,code){
 if(!docs().has(id))throw new Error('Unknown document.');
 validCode(code);
 const updated_at=new Date().toISOString();
 await transaction(['drafts'],'readwrite',tx=>{tx.objectStore('drafts').put({document_id:id,html:code.html,css:code.css,updated_at})});
 return {saved:true,updated_at};
}
export async function completeLocal(id,code){
 if(!catalog.lessons.some(l=>l.id===id))throw new Error('Unknown lesson.');
 validCode(code);
 const stamp=new Date().toISOString();
 let record={lesson_id:id,completed_at:stamp};
 await transaction(['completed','drafts'],'readwrite',tx=>{
  const store=tx.objectStore('completed'),existing=store.get(id);
  existing.onsuccess=()=>{record=existing.result||record;store.put(record)};
  tx.objectStore('drafts').put({document_id:id,html:code.html,css:code.css,updated_at:stamp});
 });
 return {...record,completed:true};
}
export async function flushEditors(){
 const tasks=[];
 window.dispatchEvent(new CustomEvent('xverse-flush-editors',{detail:{tasks}}));
 await Promise.all(tasks);
}
export async function exportLocal(){
 await flushEditors();
 const state=await readLocalState();
 return {format:'x-verse-learning-backup',version:1,exported_at:new Date().toISOString(),completed:state.completed,drafts:state.drafts};
}
export function validateBackup(input){
 if(!input||typeof input!=='object'||Array.isArray(input))throw new Error('Choose an X Verse JSON backup.');
 // Compatibility with older account exports; identity fields are deliberately ignored.
 const legacy=!Object.hasOwn(input,'format')&&!Object.hasOwn(input,'version')&&Object.hasOwn(input,'user');
 if(!legacy&&(input.format!=='x-verse-learning-backup'||input.version!==1))throw new Error('This backup format or version is not supported.');
 if(!Array.isArray(input.completed)||!input.drafts||typeof input.drafts!=='object'||Array.isArray(input.drafts))throw new Error('This backup is missing progress or drafts.');
 if(input.completed.length>catalog.lessons.length||Object.keys(input.drafts).length>docs().size)throw new Error('The backup contains too many records.');
 const allowed=docs(),lessonIds=new Set(catalog.lessons.map(l=>l.id)),seen=new Set();
 const completed=input.completed.map(c=>{
  if(!c||!lessonIds.has(c.lesson_id)||seen.has(c.lesson_id))throw new Error('The backup contains an unknown or repeated lesson.');
  seen.add(c.lesson_id);
  return {lesson_id:c.lesson_id,completed_at:validDate(c.completed_at)};
 });
 const drafts=Object.fromEntries(Object.entries(input.drafts).map(([id,d])=>{
  if(!allowed.has(id))throw new Error('The backup contains an unknown document.');
  validCode(d);
  return [id,{html:d.html,css:d.css,updated_at:validDate(d.updated_at)}];
 }));
 return {completed,drafts};
}
export async function parseBackupFile(file){
 if(!file||file.size>MAX_BYTES)throw new Error('Choose a JSON backup smaller than 50 MB.');
 let parsed;try{parsed=JSON.parse(await file.text())}catch{throw new Error('This file is not valid JSON. No data has been changed.')}
 return validateBackup(parsed);
}
export async function mergeBackup(input){
 // Revalidate before writing and merge in one transaction. No partial import on failure.
 const backup=validateBackup({format:'x-verse-learning-backup',version:1,...input});
 await flushEditors();
 let added=0,updated=0,kept=0;
 await transaction(['completed','drafts'],'readwrite',tx=>{
  const progress=tx.objectStore('completed'),drafts=tx.objectStore('drafts');
  for(const item of backup.completed){
   const req=progress.get(item.lesson_id);
   req.onsuccess=()=>{if(!req.result){progress.put(item);added++}};
  }
  for(const [id,item] of Object.entries(backup.drafts)){
   const req=drafts.get(id);
   req.onsuccess=()=>{
    if(!req.result||Date.parse(item.updated_at)>Date.parse(req.result.updated_at)){drafts.put({document_id:id,...item});updated++}else kept++;
   };
  }
 });
 window.dispatchEvent(new CustomEvent('xverse-data-restored'));
 return {added,updated,kept};
}