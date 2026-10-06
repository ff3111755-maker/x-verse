// HTML syntax assistance, not a validator. Only called for a single typed ">".
const VOID = new Set('area base br col embed hr img input link meta param source track wbr command keygen'.split(' '));
const PAIRED = new Set(('a abbr acronym address applet article aside audio b bdi bdo big blockquote body button canvas caption center cite code colgroup data datalist dd del details dfn dialog dir div dl dt em fieldset figcaption figure font footer form frameset h1 h2 h3 h4 h5 h6 head header hgroup html i iframe ins kbd label legend li main map mark marquee menu meter nav nobr noembed noframes noscript object ol optgroup option output p picture plaintext portal pre progress q rb rp rt rtc ruby s samp script search section select slot small span strike strong style sub summary sup table tbody td template textarea tfoot th thead time title tr tt u ul var video xmp').split(' '));
const RAW = new Set('script style textarea title xmp iframe noembed noframes plaintext'.split(' '));
const namePattern = '[A-Za-z][\\w:.-]*';
const tokenPattern = new RegExp(`^<(/?)(${namePattern})(?=[\\s/>])`);
function closingAt(text,name){
  return new RegExp(`^\\s*</${name.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\$&')}\\s*>`,'i').test(text);
}
export function pairedTagEdit(value, caret) {
  if(caret<1 || value[caret-1]!=='>') return null;
  // Tokenize through the insertion point so ">" in attributes, comments or raw text
  // is not mistaken for an opening tag. No DOM normalization of user code.
  const before=value.slice(0,caret);
  let i=0,raw=null,last=null;
  while(i<before.length){
    if(raw){
      if(raw==='plaintext')return null;
      const re=new RegExp(`</${raw}\\s*>`,'ig');re.lastIndex=i;
      const m=re.exec(before);
      if(!m)return null;
      i=re.lastIndex;raw=null;last=null;continue;
    }
    if(before[i]!=='<'){i++;continue;}
    if(before.startsWith('<!--',i)){
      const end=before.indexOf('-->',i+4);
      if(end<0)return null;
      i=end+3;last=null;continue;
    }
    if(before.startsWith('<![CDATA[',i)){
      const end=before.indexOf(']]>',i+9);
      if(end<0)return null;
      i=end+3;last=null;continue;
    }
    const start=i;
    const match=before.slice(i).match(tokenPattern);
    if(!match){
      if(before[i+1]==='!'||before[i+1]==='?'){
        let quote=null,j=i+2;
        for(;j<before.length;j++){
          const c=before[j];
          if(quote){if(c===quote)quote=null;}
          else if(c==='"'||c==="'")quote=c;
          else if(c==='>')break;
        }
        if(j===before.length)return null;
        i=j+1;last=null;continue;
      }
      i++;continue;
    }
    let quote=null,j=i+match[0].length;
    for(;j<before.length;j++){
      const c=before[j];
      if(quote){if(c===quote)quote=null;}
      else if(c==='"'||c==="'")quote=c;
      else if(c==='>')break;
      else if(c==='<')break;
    }
    if(j===before.length)return null;
    if(before[j]!=='>' || quote){i=j;continue;}
    const original=match[2],name=original.toLowerCase(),closing=!!match[1];
    const selfClosing=/\/\s*>$/.test(before.slice(start,j+1));
    i=j+1;
    last={name,original,closing,selfClosing,end:i};
    if(!closing&&!selfClosing&&RAW.has(name)&&i<before.length)raw=name;
  }
  if(!last || last.end!==caret || last.closing || last.selfClosing || VOID.has(last.name))return null;
  // Known paired HTML elements and autonomous custom elements only.
  if(!PAIRED.has(last.name)&&!last.name.includes('-'))return null;
  if(closingAt(value.slice(caret),last.name))return null;
  const suffix=`</${last.original}>`;
  return {value:value.slice(0,caret)+suffix+value.slice(caret),caret,tag:last.name};
}
export function completeTypedTag(previous,next,caret,inputType,enabled=true){
  if(!enabled || inputType!=='insertText' || caret==null)return null;
  // A paste, replacement selection, IME update, undo, or deletion is left untouched.
  if(next.length!==previous.length+1 || next[caret-1]!=='>')return null;
  if(next.slice(0,caret-1)+next.slice(caret)!==previous)return null;
  return pairedTagEdit(next,caret);
}