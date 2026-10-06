import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const base=process.env.TEST_BASE||'http://127.0.0.1:8000';
const b=await chromium.launch({channel:'chrome'});
const errors=[];
async function exportBackup(p){
 const wait=p.waitForEvent('download');
 await p.getByRole('button',{name:'Export backup',exact:true}).click();
 return JSON.parse(fs.readFileSync(await (await wait).path(),'utf8'));
}
try{
 const c=await b.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'}),p=await c.newPage();
 p.on('pageerror',e=>errors.push(e.message));
 await p.goto(base,{waitUntil:'networkidle'});
 await p.getByRole('button',{name:'Code lab LIVE',exact:true}).click();
 await p.getByRole('textbox',{name:'HTML code',exact:true}).fill('<h1>Safe original</h1>');
 await p.getByText('Saved in this browser',{exact:true}).waitFor();
 await p.getByRole('button',{name:'Customize appearance'}).click();
 const before=await exportBackup(p);
 await p.evaluate(()=>{
  window.originalPut=IDBObjectStore.prototype.put;
  IDBObjectStore.prototype.put=function(...a){throw new DOMException('Storage quota exceeded','QuotaExceededError')};
 });
 await p.getByRole('button',{name:'Close dialog'}).click();
 await p.getByRole('textbox',{name:'HTML code',exact:true}).fill('<h1>Unsaved due to quota</h1>');
 await p.locator('.editor-footer').getByText(/Browser storage is full/).waitFor();
 await p.getByRole('button',{name:'Customize appearance'}).click();
 await p.getByRole('button',{name:'Export backup',exact:true}).click();
 await p.getByRole('alert').filter({hasText:'Browser storage is full'}).waitFor();
 // Restore storage and safely flush latest edit.
 await p.evaluate(()=>{IDBObjectStore.prototype.put=window.originalPut});
 const after=await exportBackup(p);assert.equal(after.drafts.playground.html,'<h1>Unsaved due to quota</h1>');
 await p.getByLabel('Choose backup file').setInputFiles({name:'old-export.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({
  user:{id:'untrusted-account-id',name:'Ignore this identity'},
  completed:[],drafts:{'playground-java':{html:'public class Main {}',css:'',updated_at:new Date().toISOString()}}
 }))});
 await p.getByRole('button',{name:'Merge backup',exact:true}).click();
 await p.getByText(/Restored: 0 new completions, 1 drafts/).waitFor();
 const imported=await exportBackup(p);
 assert.equal(imported.user,undefined);
 assert.equal(imported.drafts['playground-java'].html,'public class Main {}');
 assert.equal(imported.drafts.playground.html,after.drafts.playground.html);
 // Inject a bad record after a valid one: reject entire backup before writing anything.
 await p.getByLabel('Choose backup file').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({
  ...before,drafts:{'playground':{html:'<p>Must never be imported</p>',css:'',updated_at:'2099-01-01T00:00:00Z'},'playground-java':{html:44,css:'',updated_at:'2099-01-01T00:00:00Z'}}
 }))});
 await p.getByRole('alert').filter({hasText:'must contain'}).waitFor();
 const unchanged=await exportBackup(p);
 assert.deepEqual(unchanged.drafts,imported.drafts);
 assert.deepEqual(errors,[]);
 console.log('PASS quota errors visible; export flush refuses lost changes; save recovery; legacy export import ignores identity; malformed mixed import is atomic.');
}finally{await b.close()}