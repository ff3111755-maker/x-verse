/** Offline UI contract test. Supabase calls are mocked; no live account is created. */
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import AxeBuilder from '@axe-core/playwright';
const b=await chromium.launch({channel:'chrome'});
try {
const context=await b.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});const p=await context.newPage();
const errors=[];p.on('pageerror',e=>errors.push(e.message));
const user={id:'00000000-0000-4000-8000-000000000001',email:'learner@example.test',aud:'authenticated',role:'authenticated',app_metadata:{provider:'email'},user_metadata:{display_name:'Deployment Learner'},created_at:new Date().toISOString()};
const token='eyJhbGciOiJIUzI1NiJ9.'+Buffer.from(JSON.stringify({sub:user.id,exp:Math.floor(Date.now()/1000)+3600})).toString('base64url')+'.test';
const drafts={};let signup=false;
await p.route('https://deployment-test.supabase.co/**',async route=>{
 const url=route.request().url();
 if(url.includes('/signup')){signup=true;return route.fulfill({json:{user,session:null}})}
 if(url.includes('/token'))return route.fulfill({json:{access_token:token,token_type:'bearer',expires_in:3600,refresh_token:'mock-refresh',user}});
 if(url.includes('/user'))return route.fulfill({json:user});
 if(url.includes('/logout'))return route.fulfill({status:204});
 return route.fulfill({json:{}});
});
await p.route('**/api/config',route=>route.fulfill({json:{auth_mode:'supabase',auth_configured:true,supabase_url:'https://deployment-test.supabase.co',supabase_publishable_key:'sb_publishable_mock_test',runner_enabled:false,runner_message:'Code execution is not configured on this deployment.'}}));
await p.route('**/api/state',route=>route.fulfill({json:route.request().headers()['authorization']==='Bearer '+token?{user:{id:user.id,name:'Deployment Learner'},completed:[],drafts}:{user:null,completed:[],drafts:{}}}));
await p.route('**/api/drafts/**',route=>{
 assert.equal(route.request().headers()['authorization'],'Bearer '+token);
 const body=route.request().postDataJSON();
 const id=route.request().url().split('/').at(-1);drafts[id]=body;
 return route.fulfill({json:{saved:true}});
});
await p.goto('http://127.0.0.1:8000/',{waitUntil:'networkidle'});
await p.getByRole('button',{name:'Sign in',exact:true}).click();
await p.getByRole('button',{name:'Create account',exact:true}).click();
await p.getByLabel('Email',{exact:true}).fill(user.email);
await p.getByLabel('Password',{exact:true}).fill('NotARealPassword123!');
await p.locator('form').getByRole('button',{name:'Create account'}).click();
await p.getByText('Check your email to confirm your account, then sign in.').waitFor();
assert(signup);
await p.getByRole('button',{name:'Sign in',exact:true}).click();
await p.getByLabel('Password',{exact:true}).fill('NotARealPassword123!');
await p.locator('form').getByRole('button',{name:'Sign in'}).click();
await p.getByText('Signed in as',{exact:false}).waitFor();
const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
console.log('Account accessibility',axe.violations.map(v=>({id:v.id,html:v.nodes.map(n=>n.html)})));
await p.getByRole('button',{name:'Close dialog'}).click();
await p.getByRole('button',{name:'Open navigation'}).click();
await p.getByRole('button',{name:'Code lab LIVE',exact:true}).click();
await p.getByRole('textbox',{name:'HTML code'}).fill('<h1>Standalone saved draft</h1>');
await p.waitForTimeout(1900);
assert.equal(drafts.playground.html,'<h1>Standalone saved draft</h1>');
await p.getByRole('button',{name:'Customize appearance'}).click();
await p.getByRole('button',{name:'Sign out',exact:true}).click();
await p.getByRole('button',{name:'Sign in',exact:true}).last().waitFor();
await p.getByRole('button',{name:'Close dialog'}).click();
await p.getByRole('button',{name:'Open navigation'}).click();
await p.getByRole('button',{name:'Code lab LIVE',exact:true}).click();
assert(!(await p.getByRole('textbox',{name:'HTML code'}).inputValue()).includes('Standalone saved draft'));
assert.deepEqual(errors,[]);
console.log('PASS mocked signup confirmation, login, authenticated autosave, logout and private drafts cleared. No live Supabase account tested.');
}finally{await b.close()}