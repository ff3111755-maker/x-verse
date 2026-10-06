import React,{createContext,useContext,useState,useEffect,useRef} from 'react';
import {Check,RotateCcw,Palette} from 'lucide-react';
import './customization.css';

export const THEMES=[
 {id:'hologram',name:'Hologram',note:'Cool blue',accent:'#7de5ef',bg:'#0c1218',panel:'#131c25'},
 {id:'ember',name:'Ember',note:'Warm orange',accent:'#fba371',bg:'#101113',panel:'#1e1a18'},
 {id:'nebula',name:'Nebula',note:'Muted violet',accent:'#c6a6ff',bg:'#111019',panel:'#1d1928'},
 {id:'matrix',name:'Botanical',note:'Soft green',accent:'#8ee6b4',bg:'#0d1512',panel:'#15231c'},
 {id:'rose',name:'Rosé',note:'Soft pink',accent:'#ffa4c5',bg:'#171016',panel:'#271b24'}
];
const defaults={theme:'hologram',custom:'#7de5ef',autoClose:true};
const SettingsContext=createContext(null);
export const useWorkspace=()=>useContext(SettingsContext);
export function readableAccent(hex){
 if(!/^#[a-f0-9]{6}$/i.test(hex))return defaults.custom;
 let c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
 const lum=x=>{const a=x.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4});return .2126*a[0]+.7152*a[1]+.0722*a[2]};
 // A bright accent for text on dark backgrounds and dark text on primary buttons.
 while(lum(c)<.42)c=c.map(v=>Math.min(255,v+3));
 return '#'+c.map(v=>v.toString(16).padStart(2,'0')).join('');
}
export function WorkspaceProvider({children}){
 const [prefs,setPrefs]=useState(()=>{
  try{
   const p=JSON.parse((localStorage.getItem('xverse-preferences-v1')||localStorage.getItem('cokeboys-preferences-v1'))||'null')||{};
   return {...defaults,theme:[...THEMES.map(t=>t.id),'custom'].includes(p.theme)?p.theme:defaults.theme,custom:/^#[a-f0-9]{6}$/i.test(p.custom)?p.custom:defaults.custom,autoClose:typeof p.autoClose==='boolean'?p.autoClose:true};
  }catch{return defaults}
 });
 const chosen=THEMES.find(t=>t.id===prefs.theme)||THEMES[0];
 const accent=prefs.theme==='custom'?readableAccent(prefs.custom):chosen.accent;
 useEffect(()=>{
  const root=document.documentElement;
  root.style.setProperty('--accent',accent);
  root.style.setProperty('--app-bg',chosen.bg);
  root.style.setProperty('--app-panel',chosen.panel);
  root.dataset.theme=prefs.theme;
  try{localStorage.setItem('xverse-preferences-v1',JSON.stringify(prefs))}catch{}
  const meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.content=chosen.bg;
 },[prefs,accent,chosen]);
 const update=patch=>setPrefs(p=>({...p,...patch}));
 return <SettingsContext.Provider value={{prefs,update,accent}}>{children}</SettingsContext.Provider>
}
export function ThemePicker(){
 const {prefs,update,accent}=useWorkspace();
 return <section className="theme-picker" aria-labelledby="theme-title"><div className="theme-intro"><Palette size={19}/><div><h3 id="theme-title">Color theme</h3><p>Changes this website, not your practice code.</p></div></div><div className="theme-grid">{THEMES.map(t=><button key={t.id} className={'theme-option '+(prefs.theme===t.id?'chosen':'')} aria-pressed={prefs.theme===t.id} onClick={()=>update({theme:t.id})}><span className="theme-sample" style={{background:t.bg,'--sample-accent':t.accent}}><i/><i/><i/><b/>{prefs.theme===t.id&&<Check size={15}/>}</span><strong>{t.name}</strong><small>{t.note}</small></button>)}</div><div className="custom-color"><label htmlFor="custom-accent"><strong>Custom accent</strong><span>Pick a custom accent</span></label><input id="custom-accent" aria-label="Custom accent color" type="color" value={prefs.custom} onChange={e=>update({theme:'custom',custom:e.target.value})}/><button className={'btn secondary '+(prefs.theme==='custom'?'chosen':'')} aria-pressed={prefs.theme==='custom'} onClick={()=>update({theme:'custom'})}>Use custom</button></div><p className="theme-footnote">Saved in this browser. Dark accents are brightened for readability.{prefs.theme==='custom'&&<> Active: <code>{accent}</code></>}</p></section>
}
export function XVerseLogo(){return <div className="brand coke-brand"><span className="cb-mark" aria-hidden="true"><svg viewBox="0 0 44 44"><path d="M8 8h9l19 28h-9Z" fill="currentColor"/><path d="m29 8-7 10M15 26 8 36" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="square"/></svg></span><div>X <span className="brand-boys">Verse</span><span className="brand-sub">LEARN. PRACTICE. BUILD.</span></div></div>}

export function Hologram({motion}){
 const {accent}=useWorkspace();
 const canvas=useRef(null),rotation=useRef({x:-.22,y:.35}),drag=useRef(null),redraw=useRef(()=>{});
 const reset=()=>{rotation.current={x:-.22,y:.35};redraw.current()};
 useEffect(()=>{
  const el=canvas.current,ctx=el.getContext('2d');if(!ctx)return;
  let w=360,h=350,raf=0,phase=0,last=0,visible=true;
  const rgb=[1,3,5].map(i=>parseInt(accent.slice(i,i+2),16));
  const color=a=>`rgba(${rgb.join(',')},${a})`;
  function project(x,y,z){
   const rx=rotation.current.x,ry=rotation.current.y;
   const xx=x*Math.cos(ry)+z*Math.sin(ry),zz=-x*Math.sin(ry)+z*Math.cos(ry);
   const yy=y*Math.cos(rx)-zz*Math.sin(rx),depth=y*Math.sin(rx)+zz*Math.cos(rx);
   const s=1/(1+depth/800),scale=Math.min(w,h)/390;
   return {x:w/2+xx*s*scale,y:h*.49+yy*s*scale,z:depth};
  }
  function line(points,alpha=1,width=1,close=false){
   ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));
   if(close)ctx.closePath();ctx.strokeStyle=color(alpha);ctx.lineWidth=width;ctx.stroke();
  }
  function ring(radius,tilt,y=0,start=0,end=Math.PI*2,spin=0){
   const pts=[];
   for(let i=0;i<=100;i++){
    const a=start+(end-start)*i/100+spin,x=radius*Math.cos(a),z=radius*Math.sin(a);
    pts.push(project(x,y+z*Math.sin(tilt),z*Math.cos(tilt)));
   }
   return pts;
  }
  function draw(){
   ctx.clearRect(0,0,w,h);
   const cx=w/2,cy=h*.49,r=Math.min(w,h)*.43;
   const glow=ctx.createRadialGradient(cx,cy,0,cx,cy,r);glow.addColorStop(0,color(.14));glow.addColorStop(.6,color(.035));glow.addColorStop(1,color(0));
   ctx.fillStyle=glow;ctx.fillRect(0,0,w,h);
   // Floating globe: seven longitudes and five latitudes, not a flat logo.
   for(let i=0;i<7;i++){
    const a=i*Math.PI/7+phase*.12,pts=[];
    for(let j=0;j<=80;j++){const b=j*Math.PI*2/80;pts.push(project(90*Math.cos(b)*Math.cos(a),90*Math.sin(b),90*Math.cos(b)*Math.sin(a)))}
    line(pts,.24);
   }
   for(let i=-2;i<=2;i++){const y=i*28,r=Math.sqrt(90**2-y**2);line(ring(r,0,y,0,Math.PI*2,phase*.12),.24)}
   line(ring(136,.38,0),.16);
   line(ring(150,-.6,0),.2);
   line(ring(168,.12,0),.11);
   for(let i=0;i<4;i++){
    const a=phase*(i%2?-.35:.3)+i*Math.PI*.5;
    line(ring(136,.38,0,a,a+.7),.85,1.8);
    line(ring(150,-.6,0,-a,-a+.3),.55,2);
   }
   // Dotted, counter-rotating equatorial telemetry.
   for(let i=0;i<64;i++){
    const a=i*Math.PI*2/64-phase*.18,p=project(169*Math.cos(a),0,169*Math.sin(a));
    ctx.fillStyle=color(i%8===0?.95:.36);ctx.beginPath();ctx.arc(p.x,p.y,i%8===0?2:1,0,Math.PI*2);ctx.fill();
   }
   // A luminous latitude sweeps slowly through the sphere.
   const sweep=Math.sin(phase*.6)*82,rr=Math.sqrt(90**2-sweep**2);
   line(ring(rr,0,sweep),.8,1.5);
   for(let i=0;i<18;i++){
    const a=i*2.39996+phase*.1,y=80-i*9.4,r=Math.sqrt(Math.max(0,90**2-y**2)),p=project(r*Math.cos(a),y,r*Math.sin(a));
    ctx.fillStyle=color(.65);ctx.shadowColor=accent;ctx.shadowBlur=6;ctx.beginPath();ctx.arc(p.x,p.y,1.6,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
   }
   // Core reticle and horizon projection, all simulation rather than fake live data.
   const core=project(0,0,0);
   ctx.strokeStyle=color(.8);ctx.lineWidth=1;
   ctx.strokeRect(core.x-8,core.y-8,16,16);
   ctx.fillStyle='#e3fcff';ctx.fillRect(core.x-2,core.y-2,4,4);
   for(const n of [-1,1]){
    line([project(n*108,-65,0),project(n*152,-105,0),project(n*190,-105,0)],.38);
    line([project(n*107,69,0),project(n*149,107,0),project(n*182,107,0)],.28);
   }
   const beam=ctx.createLinearGradient(0,h*.55,0,h*.91);beam.addColorStop(0,color(0));beam.addColorStop(1,color(.06));
   ctx.fillStyle=beam;ctx.beginPath();ctx.moveTo(cx-r*.55,h*.51);ctx.lineTo(cx+r*.55,h*.51);ctx.lineTo(cx+r*.23,h*.91);ctx.lineTo(cx-r*.23,h*.91);ctx.closePath();ctx.fill();
   ctx.beginPath();ctx.ellipse(cx,h*.91,r*.34,r*.055,0,0,Math.PI*2);ctx.strokeStyle=color(.5);ctx.stroke();
  }
  function tick(t){
   if(!motion||!visible)return;
   if(t-last>30){phase+=Math.min((t-last)/1000,.06);last=t;draw()}
   raf=requestAnimationFrame(tick);
  }
  redraw.current=draw;
  const resize=new ResizeObserver(entries=>{const b=entries[0].contentRect;w=b.width;h=b.height;const dpr=Math.min(devicePixelRatio||1,2);el.width=w*dpr;el.height=h*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);draw()});resize.observe(el);
  const observer=new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;cancelAnimationFrame(raf);if(visible&&motion){last=performance.now();raf=requestAnimationFrame(tick)}else draw()});
  observer.observe(el);draw();
  return()=>{cancelAnimationFrame(raf);resize.disconnect();observer.disconnect();redraw.current=()=>{}};
 },[motion,accent]);
 return <div className="holo-scene"><div className="holo-label"><span>X VERSE / INTERACTIVE VIEW</span><span className="holo-status"><i/> {motion?'ACTIVE':'PAUSED'}</span></div><div className="holo-stage"><div className="holo-corner tl"/><div className="holo-corner tr"/><div className="holo-corner bl"/><div className="holo-corner br"/><canvas ref={canvas} tabIndex={0} role="img" aria-label="Interactive holographic core" aria-describedby="holo-help" onPointerDown={e=>{drag.current={x:e.clientX,y:e.clientY};e.currentTarget.setPointerCapture(e.pointerId)}} onPointerMove={e=>{if(!drag.current)return;rotation.current.y+=(e.clientX-drag.current.x)*.008;rotation.current.x=Math.max(-1.2,Math.min(1.2,rotation.current.x+(e.clientY-drag.current.y)*.008));drag.current={x:e.clientX,y:e.clientY};redraw.current()}} onPointerUp={e=>{drag.current=null;if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId)}} onPointerCancel={()=>{drag.current=null}} onKeyDown={e=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home'].includes(e.key))return;e.preventDefault();if(e.key==='Home')reset();else{if(e.key==='ArrowLeft')rotation.current.y-=.15;if(e.key==='ArrowRight')rotation.current.y+=.15;if(e.key==='ArrowUp')rotation.current.x=Math.max(-1.2,rotation.current.x-.15);if(e.key==='ArrowDown')rotation.current.x=Math.min(1.2,rotation.current.x+.15);redraw.current()}}}/><span className="holo-tag left">HTML<br/><b>STRUCTURE</b></span><span className="holo-tag right">CSS<br/><b>EXPRESSION</b></span></div><div className="holo-bottom"><span id="holo-help">DRAG TO ROTATE · ARROW KEYS TO TILT</span><button aria-label="Reset hologram orientation" title="Reset hologram orientation" onClick={reset}><RotateCcw size={13}/></button></div></div>
}

