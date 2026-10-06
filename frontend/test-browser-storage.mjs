import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs';
const base=process.env.TEST_BASE||'http://127.0.0.1:8000';
const b=await chromium.launch({channel:'chrome'});
const errors=[];
let backup;
async function settings(p){await p.getByRole('button',{name:'Customize appearance'}).click();}
async function nav(p,name){
 if(await p.getByRole('button',{name:'Open navigation'}).isVisible())await p.getByRole('button',{name:'Open navigation'}).click();
 await p.getByRole('button',{name,exact:true}).click();
}
async function choose(p,payload){await p.getByLabel('Choose backup file').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(payload))});}
try{
 const c=await b.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));const forbidden=[];
 p.on('request',r=>{if(/\/api\/(drafts|state|export|complete\/)/.test(r.url()))forbidden.push(r.url())});
 await p.goto(base,{waitUntil:'networkidle'});
 await p.getByRole('button',{name:'Start learning',exact:true}).click();
 const curriculum=await (await c.request.get(base+'/api/curriculum')).json(),lesson=curriculum.lessons[0];
 await p.getByRole('button',{name:'Load example solution',exact:false}).click();
 await p.getByRole('button',{name:'Run code checks',exact:true}).click();
 await p.getByText('Code checks passed. Now complete the knowledge check.',{exact:true}).waitFor();
 await p.locator('.quiz-option').nth(lesson.quiz.answer).click();
 await p.getByRole('button',{name:'Check answer',exact:true}).click();
 await p.getByRole('button',{name:/Complete lesson ·/}).click();
 await p.getByRole('button',{name:'Next lesson',exact:false}).waitFor();
 await nav(p,'Code lab LIVE');
 const text=p.getByRole('textbox',{name:'HTML code',exact:true});
 await text.fill('<h1>Local draft survived</h1>');
 await p.getByText('Saved in this browser',{exact:true}).waitFor();
 await p.reload({waitUntil:'networkidle'});
 await nav(p,'Code lab LIVE');
 assert.equal(await text.inputValue(),'<h1>Local draft survived</h1>');
 // Export immediately after editing; explicit flush covers pending saves.
 await text.fill('<h1>Latest export</h1>');
 await settings(p);
 const download=p.waitForEvent('download');
 await p.getByRole('button',{name:'Export backup',exact:true}).click();
 backup=JSON.parse(fs.readFileSync(await (await download).path(),'utf8'));
 assert.equal(backup.format,'x-verse-learning-backup');
 assert.equal(backup.completed.length,1);
 assert.equal(backup.drafts.playground.html,'<h1>Latest export</h1>');
 assert.equal(backup.user,undefined);
 assert.deepEqual(forbidden,[]);
 const axe=await new AxeBuilder({page:p}).exclude('iframe').withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 assert.deepEqual(axe.violations.map(v=>v.id),[]);
 // Import into clean browser; exact merge confirmation required.
 const c2=await b.newContext({viewport:{width:320,height:800},reducedMotion:'reduce'});
 const q=await c2.newPage();q.on('pageerror',e=>errors.push(e.message));
 await q.goto(base,{waitUntil:'networkidle'});await settings(q);
 await choose(q,backup);
 await q.getByRole('heading',{name:'Review your import'}).waitFor();
 await q.getByRole('button',{name:'Merge backup',exact:true}).click();
 await q.getByText(/Restored: 1 new completions/).waitFor();
 assert.equal(await q.locator('.dialog').evaluate(el=>el.scrollWidth>el.clientWidth),false);
 await q.getByRole('button',{name:'Close dialog'}).click();await nav(q,'Code lab LIVE');
 assert.equal(await q.getByRole('textbox',{name:'HTML code',exact:true}).inputValue(),'<h1>Latest export</h1>');
 await q.getByRole('textbox',{name:'HTML code',exact:true}).fill('<p>Newer local edit</p>');
 await q.getByText('Saved in this browser',{exact:true}).waitFor();
 await settings(q);await choose(q,backup);await q.getByRole('button',{name:'Merge backup',exact:true}).click();
 await q.getByText(/Kept 2 newer or identical local drafts/).waitFor();
 // Invalid backup must not erase existing records.
 await choose(q,{...backup,version:999});
 await q.getByRole('alert').filter({hasText:'not supported'}).waitFor();
 await choose(q,{...backup,drafts:{'__bad-document':{html:'x',css:'',updated_at:new Date().toISOString()}}});
 await q.getByRole('alert').filter({hasText:'unknown document'}).waitFor();
 await q.getByRole('button',{name:'Close dialog'}).click();await nav(q,'Code lab LIVE');
 assert.equal(await q.getByRole('textbox',{name:'HTML code',exact:true}).inputValue(),'<p>Newer local edit</p>');
 await q.getByRole('button',{name:'Java',exact:true}).click();
 await q.getByRole('textbox',{name:'Java code'}).fill('public class Main { /* browser saved */ }');
 await q.getByText('Saved in this browser',{exact:true}).waitFor();
 await q.reload({waitUntil:'networkidle'});await nav(q,'Code lab LIVE');
 await q.getByRole('button',{name:'Java',exact:true}).click();
 assert.equal(await q.getByRole('textbox',{name:'Java code'}).inputValue(),'public class Main { /* browser saved */ }');
 const c3=await b.newContext(),r=await c3.newPage();
 await r.addInitScript(()=>{Object.defineProperty(window,'indexedDB',{get(){return undefined}})});
 await r.goto(base,{waitUntil:'networkidle'});
 await r.getByText(/Browser saving is unavailable/).waitFor();
 await q.screenshot({path:'../browser-storage-mobile.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('PASS local completion, autosave/reload, immediate export, clean-browser import, conflict protection, malformed backups, Java drafts, no account/draft network traffic, blocked-storage message, accessibility and 320px dialog.');
}finally{await b.close()}