import {writeFile} from 'node:fs/promises';
import {parseHTML} from 'linkedom';
let source='';
for await (const chunk of process.stdin) source+=chunk;
const {document,window}=parseHTML('<html><body><main id="app"><h1>Ready</h1><button id="add">Add</button><ul id="list"></ul></main></body></html>');
globalThis.document=document;
globalThis.window=window;
await writeFile('/tmp/program.mjs',source);
try { await import('file:///tmp/program.mjs'); }
catch(error){ console.error(error?.stack || String(error)); process.exitCode=1; }