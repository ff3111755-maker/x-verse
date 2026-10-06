"""Extend the existing HTML/CSS curriculum, preserving lesson IDs and learner data."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
data=json.loads((ROOT/'data/curriculum.json').read_text())
data['lessons']=[l for l in data['lessons'] if l['track'] in ('html','css')]
new=[]
def add(track,module,slug,title,summary,concept,detail,pitfall,task,solution,expected,question,options,answer,explanation,reference=None):
    number=1+sum(l['track']==track for l in new)
    if track=='java' and not solution.startswith(('import ','public class')):
        solution='public class Main {\n  public static void main(String[] args) throws Exception {\n'+''.join('    '+line+'\n' for line in solution.splitlines())+'  }\n}\n'
    starter=('// '+task+'\nconsole.log("Start here");\n') if track=='javascript' else 'public class Main {\n  public static void main(String[] args) throws Exception {\n    // '+task+'\n  }\n}\n'
    new.append(dict(id=track+'-'+slug,track=track,module=module,title=title,number=number,minutes=20 if number<11 else 30,xp=100 if number<11 else 150,summary=summary,
        learn=[['How it works',concept],['In practice',detail],['Watch out for',pitfall],['Try the example','Read the task, write your own solution, then select Run code checks. Your program runs in an isolated '+('Node.js 22 container. The browser lessons include a small DOM fixture; they do not open a real browser.' if track=='javascript' else 'Java 21 container. Use a public class named Main; standard input and external network access are not available.')+' Load the example solution if you get stuck, then change a value and predict the output before running again.']],
        html=starter,css='',solution_html=solution,solution_css='',task=task,checks=[['output',expected]],expected_output=expected,
        quiz=dict(question=question,options=options,answer=answer,explanation=explanation),
        reference=reference or ('https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide' if track=='javascript' else 'https://dev.java/learn/')))
def J(*a,**k):add('javascript',*a,**k)
def V(*a,**k):add('java',*a,**k)

J('01 / Language basics','first-program','Run your first JavaScript program','Use the console and understand where JavaScript runs.',
'JavaScript is a separate language from Java. Browsers run it to respond to users and update pages; Node.js runs it outside a browser. Both implement ECMAScript, but their surrounding APIs differ.',
'console.log writes a value to the console. Statements describe actions; // starts a line comment and /* ... */ spans multiple lines. This course executes modules in Node.js 22.',
'Browser globals such as window are not automatically present in Node. The DOM lessons in this course supply an explicit fixture. A successful run means the program executed, not that every possible input is correct.',
'Print exactly Hello, X Verse!','console.log("Hello, X Verse!");','Hello, X Verse!',
'What is Node.js?',['A CSS framework','A JavaScript runtime outside the browser','Another name for Java'],1,'Node.js executes JavaScript outside the browser.')

J('01 / Language basics','bindings','Variables, types & equality','Choose bindings and compare values without surprises.',
'const prevents reassignment of a binding; let permits it. Neither makes an object deeply immutable. Primitive types include string, number, boolean, undefined, bigint, symbol, and null.',
'Use === and !== unless coercion is a deliberate requirement. typeof helps inspect primitives, but typeof null is the historical value "object". Number represents floating-point values; integers are exact only within the safe integer range.',
'== converts types before comparison. Also, const items = [] still allows items.push(). Start with const and use let only when you need to reassign.',
'Create price = 12 and quantity = 3; log the product, then whether "36" strictly equals 36.',
'const price = 12;\nconst quantity = 3;\nconsole.log(price * quantity);\nconsole.log("36" === 36);','36\nfalse',
'What does const prevent?',['Reassigning the binding','Changing any nested object','Calling a method'],0,'const protects the binding, not the contents of an object.')

J('01 / Language basics','strings','Strings, numbers & conversions','Format output and convert user input explicitly.',
'Template literals use backticks and interpolate expressions with ${...}. Strings are immutable; methods return new strings. Number(text) converts a complete numeric string, while parseInt may stop at a non-digit.',
'Validate converted numbers with Number.isFinite. Use integer minor units for money when possible because binary floating-point cannot exactly represent many decimal fractions.',
'Number("") is 0, and parseInt("12px", 10) is 12. Decide whether empty or partially numeric input is acceptable before converting it.',
'Convert "24" to a number, add 6, and print Total: 30.',
'const value = Number("24");\nconsole.log(`Total: ${value + 6}`);','Total: 30',
'What does Number("abc") produce?',['0','NaN','An empty string'],1,'An invalid numeric conversion produces NaN; validate it rather than treating it as a usable number.')

J('01 / Language basics','conditions','Conditions & nullish values','Write predictable branches and defaults.',
'if/else selects a branch; switch compares against cases. A ternary expression chooses one of two values. Falsy values include false, 0, "", null, undefined, and NaN.',
'Use ?? for a default only when a value is null or undefined. Optional chaining ?. safely stops a property lookup when its left side is nullish.',
'|| also replaces valid falsy values such as 0. Optional chaining does not make a nonexistent variable safe, nor does it catch exceptions inside called functions.',
'Preserve a score of 0 with ??, then print adult for age 18.',
'const score = 0;\nconsole.log(score ?? 10);\nconst age = 18;\nconsole.log(age >= 18 ? "adult" : "minor");','0\nadult',
'Which default preserves 0?',['value || 10','value ?? 10','value && 10'],1,'?? falls back only for null or undefined.')

J('01 / Language basics','loops','Loops & iteration','Repeat work and stop at the right point.',
'for loops combine initialization, a condition, and an update. while repeats while a condition is true; do/while runs at least once. for...of consumes values from an iterable.',
'break exits a loop and continue skips the rest of an iteration. Sum numbers with an accumulator initialized before the loop. Prefer clear loop bounds over clever expressions.',
'for...in enumerates property keys, not array values, and may include inherited enumerable properties. Infinite loops are stopped by this lab, but can freeze a real page.',
'Use a loop to add the integers 1 through 5 and print 15.',
'let total = 0;\nfor (let i = 1; i <= 5; i++) total += i;\nconsole.log(total);','15',
'What does for...of iterate?',['Property descriptors','Values of an iterable','Only object keys'],1,'for...of reads values through the iterable protocol.')

J('02 / Functions & data','functions','Functions, parameters & return values','Extract reusable behavior with a clear contract.',
'Functions accept arguments and return a value. A declaration is available before its line executes within its scope. Function expressions and arrow functions are values you can assign or pass.',
'Default parameters apply when an argument is undefined. Rest parameters gather remaining arguments into an array. An arrow with a block body needs an explicit return.',
'Logging a result is not the same as returning it. A missing return yields undefined. Keep calculations separate from display code so they are easier to test.',
'Write add(a, b = 1). Print add(4, 3) and add(4).',
'function add(a, b = 1) { return a + b; }\nconsole.log(add(4, 3));\nconsole.log(add(4));','7\n5',
'What does a function without return produce?',['null','undefined','The last local variable'],1,'Without an explicit returned value, the result is undefined.')

J('02 / Functions & data','scope','Scope, closures & private state','Keep state alive without exposing it globally.',
'let and const are block-scoped; var is function-scoped. A closure retains access to its lexical environment even after the outer function has returned.',
'A factory can create independent counters, each with its own private binding. This is useful for callbacks, event handlers, and stateful utilities.',
'Closures capture bindings, not frozen snapshots. Long-lived callbacks can retain data you no longer need; remove listeners or release references when finished.',
'Create a counter closure and print its first two results: 1 and 2.',
'function makeCounter() {\n  let count = 0;\n  return () => ++count;\n}\nconst next = makeCounter();\nconsole.log(next());\nconsole.log(next());','1\n2',
'What does a closure retain?',['Only the returned number','Access to its lexical environment','Every global forever'],1,'The function can still reach bindings in the scope where it was created.')

J('02 / Functions & data','arrays','Arrays & transformations','Filter and transform a collection without manual indexing.',
'Arrays are ordered collections. map creates transformed values; filter keeps matching values; reduce combines values into an accumulator. find returns the first match, while some and every return booleans.',
'Chain transformations when they stay readable. Supply an initial accumulator to reduce, especially when an array may be empty. join produces a string with an explicit separator.',
'sort mutates the array and defaults to string ordering. Use toSorted or copy before sorting, with a numeric comparator for numbers.',
'Keep even numbers from [1,2,3,4], double them, and print 4,8.',
'const values = [1, 2, 3, 4];\nconsole.log(values.filter(n => n % 2 === 0).map(n => n * 2).join(","));','4,8',
'Which method keeps matching elements?',['map','filter','join'],1,'filter returns a new array containing elements whose predicate is truthy.')

J('02 / Functions & data','objects','Objects, destructuring & spread','Model related values and copy them deliberately.',
'Objects group properties under keys. Destructuring reads properties into bindings; rest gathers remaining properties. Object spread copies enumerable own properties into a new object.',
'const {name, role = "learner"} = person provides a default for undefined. Object.entries exposes key/value pairs and Object.hasOwn checks ownership.',
'Spread is shallow: nested objects still share references. Avoid merging untrusted keys into sensitive objects without validation.',
'Copy {name:"Mira", points:10}, update points to 15, and print the original and updated values.',
'const user = {name: "Mira", points: 10};\nconst updated = {...user, points: 15};\nconsole.log(user.points);\nconsole.log(updated.points);','10\n15',
'Is object spread a deep clone?',['Yes, always','No, it is shallow','Only with const'],1,'Nested references remain shared after a shallow copy.')

J('02 / Functions & data','collections','Map, Set & structured data','Choose a collection suited to your keys and values.',
'Set stores unique values. Map stores key/value pairs and accepts keys of any type. Both preserve insertion order and expose a size property.',
'Use a Set to deduplicate primitive values. Use Map for keyed collections with frequent insertion and deletion instead of treating a plain object as a dictionary in every situation.',
'Two separately created objects are different keys even if their properties match. Set and Map use reference identity for objects.',
'Deduplicate ["html","css","html"], then map js to JavaScript and print the lookup.',
'const unique = new Set(["html", "css", "html"]);\nconsole.log([...unique].join(","));\nconst names = new Map([["js", "JavaScript"]]);\nconsole.log(names.get("js"));','html,css\nJavaScript',
'Which collection stores unique values?',['Set','Array','String'],0,'A Set removes duplicate values according to its equality semantics.')

J('03 / Object model','classes','Prototypes, classes & this','Understand methods without treating classes as magic.',
'Objects can delegate property lookup through a prototype chain. class syntax provides constructors and prototype methods. this depends on how a normal function is called; arrow functions capture lexical this.',
'Private fields prefixed with # are enforced by the language. Use methods to express behavior and composition when inheritance does not describe a real relationship.',
'Extracting a method and calling it without its receiver can lose this. Arrow functions are not constructors and do not define their own this.',
'Create a Counter class with private count, increment it twice, and print 2.',
'class Counter {\n  #count = 0;\n  increment() { this.#count++; }\n  value() { return this.#count; }\n}\nconst counter = new Counter();\ncounter.increment(); counter.increment();\nconsole.log(counter.value());','2',
'Where are ordinary class methods generally stored?',['On the prototype','Inside every number','Only in localStorage'],0,'Ordinary class methods live on the prototype; instance fields belong to instances.')

J('03 / Object model','errors','Errors & input validation','Reject invalid inputs with useful error messages.',
'Throw an Error when an operation cannot satisfy its contract. try/catch handles exceptions; finally runs cleanup whether execution succeeds or fails.',
'Validate at the boundary. Include enough context in errors to debug without exposing secrets. For async functions, a thrown error rejects the returned promise.',
'Do not swallow an error and silently pretend success. Catch only where you can recover or provide a meaningful message.',
'Write divide(a,b) that throws Error("Division by zero") when b is zero. Catch and print the message.',
'function divide(a, b) {\n  if (b === 0) throw new Error("Division by zero");\n  return a / b;\n}\ntry { divide(4, 0); } catch (error) { console.log(error.message); }','Division by zero',
'What should a catch block do?',['Always ignore the failure','Recover or report meaningfully','Delete all data'],1,'Handling should be deliberate; swallowing errors hides bugs.')

J('03 / Object model','modules','ES modules & package boundaries','Share code through explicit imports and exports.',
'ES modules use import and export. Named imports use braces; a default export can be imported under a local name. Module code runs in strict mode and has its own scope.',
'In a project, place reusable functions in a separate file and import them from a clear entry point. package.json type: module makes .js files ES modules in Node. This lab already uses module mode.',
'Node built-ins and browser modules are different environments. Bare package names need installation or a bundler/import map. This single-file lab supports built-ins and the provided DOM fixture, not arbitrary npm installs.',
'Import strictEqual from node:assert, check 2 + 3 equals 5, then print Module check passed.',
'import {strictEqual} from "node:assert";\nstrictEqual(2 + 3, 5);\nconsole.log("Module check passed");','Module check passed',
'How do you import a named export?',['import {name} from "./file.js"','include file.js','@import url(file.js)'],0,'Named imports use braces and must refer to an exported name.')

J('04 / Asynchronous code','event-loop','The event loop & microtasks','Predict the order of synchronous and deferred work.',
'JavaScript runs a stack of synchronous calls. Promise reactions and queueMicrotask callbacks run after the current synchronous work finishes; timer callbacks run in later tasks.',
'Use asynchronous APIs for waiting instead of blocking. A long synchronous loop still blocks the current thread even inside an async function.',
'A zero-delay timer is not an immediate call. Exact timer scheduling varies, but promise microtasks from the same turn run before its next timer task.',
'Log A, schedule a resolved-promise callback to log B, then log C. Observe A, C, B.',
'console.log("A");\nPromise.resolve().then(() => console.log("B"));\nconsole.log("C");','A\nC\nB',
'When does a promise reaction run?',['Before all synchronous code','After the current synchronous work','Only on a new operating-system thread'],1,'Promise callbacks are microtasks, not immediate function calls.')

J('04 / Asynchronous code','promises','Promises & async/await','Compose operations that finish later.',
'A promise represents eventual fulfillment or rejection. async functions always return a promise. await pauses that async function until the awaited value settles, not the whole runtime.',
'Promise.all runs independent work concurrently and rejects if any input rejects. Promise.allSettled reports every outcome. Handle failures with try/catch around await.',
'Starting unrelated work one await at a time can add avoidable latency. Conversely, unbounded Promise.all over huge collections can overload a service.',
'Await Promise.all for values 4 and 6, add them, and print 10.',
'const values = await Promise.all([Promise.resolve(4), Promise.resolve(6)]);\nconsole.log(values.reduce((sum, value) => sum + value, 0));','10',
'What happens if an input to Promise.all rejects?',['It fulfills with zero','The aggregate promise rejects','It ignores the failure'],1,'Promise.all rejects on the first observed rejection; other work is not automatically cancelled.')

J('04 / Asynchronous code','fetch','Fetch, JSON & HTTP failures','Separate network failures from unsuccessful responses.',
'fetch returns a Response. It rejects for network-level failures, but not simply because the HTTP status is 404 or 500. Check response.ok before consuming an expected success body.',
'Use await response.json() for JSON and validate the parsed shape. AbortController can cancel a request. This lab has no external network; its example uses a local Response object with the same parsing interface.',
'CORS is a browser access rule, not authentication. Do not put private server API keys in frontend code. JSON parsing can fail independently of request success.',
'Create Response.json({name:"Mira"}), check ok, parse it, and print Mira.',
'const response = Response.json({name: "Mira"});\nif (!response.ok) throw new Error(`HTTP ${response.status}`);\nconst data = await response.json();\nconsole.log(data.name);','Mira',
'Does fetch reject automatically for HTTP 404?',['Yes','No; inspect response.ok','Only when JSON is returned'],1,'HTTP failures are still responses; check their status explicitly.')

J('04 / Asynchronous code','cancellation','Cancellation & cleanup','Stop work that is no longer useful.',
'An AbortController owns a signal. APIs that accept that signal can stop their operation after abort() is called. Cancellation is cooperative rather than a universal kill switch.',
'Use finally to release resources and clear timers. For search-as-you-type, abort an obsolete request and still guard against older results overwriting newer state.',
'Not every promise supports cancellation. Aborting a signal only affects APIs listening to it. Distinguish an expected cancellation from an actual application error.',
'Listen once for abort, call controller.abort(), and print cancelled then true.',
'const controller = new AbortController();\ncontroller.signal.addEventListener("abort", () => console.log("cancelled"), {once:true});\ncontroller.abort();\nconsole.log(controller.signal.aborted);','cancelled\ntrue',
'Is cancellation automatic for every promise?',['Yes','No, the operation must support it','Only for arrays'],1,'The underlying operation has to observe the signal.')

J('05 / Browser programming','dom','Select & update the DOM','Change page content through DOM APIs.',
'The Document Object Model is a tree of nodes. querySelector returns the first matching element, or null. querySelectorAll returns a static NodeList of matches.',
'Set textContent for plain text, createElement for new nodes, and append to insert them. The lab provides document and window using linkedom, with <main id="app"><h1>Ready</h1><button id="add">Add</button><ul id="list"></ul></main>.',
'The fixture supports DOM operations but is not a layout engine. innerHTML parses markup; using it with untrusted input can introduce XSS in real sites.',
'Select #app h1, change its textContent to Hello DOM, and print the heading text.',
'const heading = document.querySelector("#app h1");\nheading.textContent = "Hello DOM";\nconsole.log(heading.textContent);','Hello DOM',
'Which property safely inserts plain user text?',['innerHTML','textContent','outerHTML'],1,'textContent treats input as text instead of parsing it as markup.',
reference='https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model')

J('05 / Browser programming','events','Events, listeners & delegation','Respond to interactions without inline handlers.',
'addEventListener registers a callback for an event type. Events often bubble from a target through ancestors. event.target is the originating node; currentTarget is the listener owner.',
'Delegation listens on a stable parent and checks the event target, so newly added children can work without new listeners. preventDefault stops a default action; stopPropagation affects propagation.',
'Use the same function reference to removeEventListener. Event delegation needs a suitable bubbling event; not every event bubbles.',
'Attach a click listener to #add, dispatch two click events, and print a count of 2.',
'let count = 0;\nconst button = document.querySelector("#add");\nbutton.addEventListener("click", () => count++);\nbutton.dispatchEvent(new window.Event("click", {bubbles:true}));\nbutton.dispatchEvent(new window.Event("click", {bubbles:true}));\nconsole.log(count);','2',
'What is event.currentTarget?',['The listener owner','Always the deepest clicked node','The page URL'],0,'currentTarget is the element whose listener is currently executing.')

J('05 / Browser programming','forms','Forms & application state','Validate data without losing the user’s work.',
'Forms have a submit event, while controls expose values as strings. Native labels and constraints help accessibility, but the server must still validate submitted data.',
'Keep application state separate from DOM rendering. Normalize input at the boundary, validate it, then update state and re-render. In a browser, preventDefault lets a submit listener handle an in-page workflow.',
'Client-side validation is a user-experience feature, not a security boundary. Do not accept hidden fields or disabled controls as authorization.',
'Normalize the string "  Mira  " with trim. Store it in a state object and print Welcome, Mira.',
'const rawInput = "  Mira  ";\nconst name = rawInput.trim();\nif (!name) throw new Error("Name required");\nconst state = {name};\nconsole.log(`Welcome, ${state.name}`);','Welcome, Mira',
'Where must submitted data also be validated?',['Only in CSS','On the server','Only in the placeholder'],1,'A user can bypass browser checks, so server validation is mandatory.')

J('05 / Browser programming','storage','JSON, storage & data boundaries','Serialize small amounts of state carefully.',
'JSON.stringify turns compatible values into text; JSON.parse reads JSON text back. Browser localStorage stores strings per origin and persists across sessions; sessionStorage lasts for the tab session.',
'Validate restored data, handle malformed JSON, and version your stored schema. The lab demonstrates serialization without browser storage; use the real storage API in your own browser project.',
'JSON does not preserve methods, undefined object properties, or Date instances as dates. Storage can fail or be cleared. Do not store sensitive authentication secrets casually in localStorage.',
'Serialize {theme:"dark", version:1}, parse it, and print dark then 1.',
'const saved = JSON.stringify({theme:"dark", version:1});\nconst restored = JSON.parse(saved);\nconsole.log(restored.theme);\nconsole.log(restored.version);','dark\n1',
'What does localStorage store?',['Strings','Live function closures','Only numbers'],0,'You must serialize structured data yourself.')

J('06 / Reliable applications','testing','Testing & debugging','Turn assumptions into repeatable checks.',
'A unit test supplies inputs and asserts outputs. Cover typical values, boundaries, and invalid inputs. Keep core logic pure where practical so tests do not depend on network or timing.',
'Node supplies assert and a test runner; browser projects may use dedicated test tools. Breakpoints, stack traces, and a small reproduction are more useful than random edits.',
'A passing example is not a proof for all inputs. Avoid tests that only repeat the implementation. Test the contract, including failure cases.',
'Write clamp(value,min,max); assert clamp(12,0,10) is 10 and clamp(-2,0,10) is 0, then print Tests passed.',
'import assert from "node:assert/strict";\nconst clamp = (value, min, max) => Math.min(max, Math.max(min, value));\nassert.equal(clamp(12,0,10),10);\nassert.equal(clamp(-2,0,10),0);\nconsole.log("Tests passed");','Tests passed',
'What should tests include?',['Only one happy path','Boundaries and invalid inputs too','Only console colors'],1,'Edge cases often expose assumptions that ordinary inputs do not.')

J('06 / Reliable applications','regex','Regular expressions & text processing','Match constrained text without overcomplicating it.',
'Regular expressions describe text patterns. Anchors ^ and $ constrain the start and end; character classes match categories; quantifiers repeat a preceding token.',
'Use test for a boolean and match or matchAll to extract results. Prefer ordinary string methods when a simple includes, startsWith, or split is clearer.',
'Regexes with nested ambiguous repetition can perform badly on hostile input. Global regexes have mutable lastIndex when used with test. Do not try to parse arbitrary HTML with regex.',
'Validate exactly three uppercase letters followed by two digits; print results for ABC12 and abc12.',
'const pattern = /^[A-Z]{3}\\d{2}$/;\nconsole.log(pattern.test("ABC12"));\nconsole.log(pattern.test("abc12"));','true\nfalse',
'What do ^ and $ anchor?',['Start and end of the input by default','Any two digits','CSS selectors'],0,'Anchors constrain where a match may begin and end.')

J('06 / Reliable applications','dates','Dates, time zones & internationalization','Format values without confusing local time and UTC.',
'Date represents a timestamp, not a stored time zone. An ISO string ending in Z denotes UTC. Intl.DateTimeFormat and Intl.NumberFormat format values for a locale.',
'Choose a time zone deliberately for calendar reporting. Use getUTC* methods for UTC components and local methods for the runtime zone. Store timestamps with a clear offset or epoch.',
'Adding 24 hours is not always the same as advancing one local calendar day across daylight saving. Avoid parsing ambiguous date strings such as 01/02/2026.',
'Parse 2026-01-02T00:00:00Z and print its ISO string and UTC year.',
'const date = new Date("2026-01-02T00:00:00Z");\nconsole.log(date.toISOString());\nconsole.log(date.getUTCFullYear());','2026-01-02T00:00:00.000Z\n2026',
'What does Z mean in an ISO timestamp?',['The browser locale','UTC','An invalid date'],1,'Z indicates a zero UTC offset.')

J('07 / Advanced JavaScript','iterators','Iterators & generators','Produce values lazily instead of building a whole array.',
'An iterable exposes Symbol.iterator; an iterator returns objects with value and done. Generator functions use function* and yield to suspend between values.',
'Generators are useful for ranges, paginated processing, and custom traversal. for...of consumes iterables; spread eagerly collects them into an array.',
'An unbounded generator is safe only when the consumer stops. Spreading an infinite iterable never finishes. Async iterables use Symbol.asyncIterator and for await...of.',
'Create a generator that yields 1, 2, 3 and print them joined by commas.',
'function* count() {\n  yield 1; yield 2; yield 3;\n}\nconsole.log([...count()].join(","));','1,2,3',
'What does yield do?',['Stops the whole process permanently','Produces a value and suspends the generator','Creates a CSS rule'],1,'The generator resumes from that point on its next iteration.')

J('07 / Advanced JavaScript','descriptors','Property descriptors & immutability','Know what can and cannot change.',
'Object properties have descriptors controlling writability, enumerability, and configurability. Object.freeze prevents ordinary changes to an object’s own properties.',
'Use Object.getOwnPropertyDescriptor to inspect a property. Immutable update patterns simplify state reasoning, but freezing and spreading are shallow operations.',
'A frozen object can still contain mutable nested objects. Freezing Map or Set objects does not freeze their internal collections.',
'Freeze {enabled:true}, print whether it is frozen, then inspect whether enabled is writable.',
'const config = Object.freeze({enabled:true});\nconsole.log(Object.isFrozen(config));\nconsole.log(Object.getOwnPropertyDescriptor(config,"enabled").writable);','true\nfalse',
'Is Object.freeze recursive?',['Yes','No','Only for strings'],1,'It freezes the object itself, not every nested object.')

J('07 / Advanced JavaScript','performance','Performance & algorithmic cost','Improve the work performed before optimizing syntax.',
'A loop over n items is often O(n); nested scans may be O(n²). A Set or Map can avoid repeated linear searches in common workloads.',
'Measure the real bottleneck with profiling. In browsers, reduce unnecessary DOM work, batch reads and writes, and yield long tasks. Debounce waits for a quiet period; throttle limits frequency.',
'Big-O describes growth, not exact elapsed time. Microbenchmarks can be misleading due to warm-up, input size, and runtime optimizations.',
'Use a Set to find the unique intersection of [1,2,3,4] and [3,4,5]. Print 3,4.',
'const right = new Set([3,4,5]);\nconst result = [...new Set([1,2,3,4])].filter(x => right.has(x));\nconsole.log(result.join(","));','3,4',
'What is a useful first step in performance work?',['Measure the actual bottleneck','Rewrite every loop immediately','Add more timers'],0,'Profiling keeps optimization focused on work that matters.')

J('08 / Production practice','security','Secure DOM updates & untrusted input','Treat strings from users as data, not code.',
'Cross-site scripting occurs when untrusted input is interpreted as executable content. Use textContent for plain text and a reviewed sanitizer only when rich HTML is genuinely required.',
'Validate data on the server, use authorization checks on every protected operation, and avoid eval or new Function on user input. Content Security Policy is defense in depth, not a substitute for safe rendering.',
'Escaping rules depend on the destination: HTML text, attributes, URLs, JavaScript, and SQL are not interchangeable contexts. A homemade replace is rarely a universal sanitizer.',
'Set a created paragraph’s textContent to "<img src=x>". Print its innerHTML to confirm the angle brackets are escaped.',
'const node = document.createElement("p");\nnode.textContent = "<img src=x>";\nconsole.log(node.innerHTML);','&lt;img src=x&gt;',
'Why use textContent for untrusted plain text?',['It executes scripts faster','It avoids treating the text as HTML','It authenticates the user'],1,'textContent inserts text rather than markup.')

J('08 / Production practice','node','Node.js files & server-side code','Use server APIs without confusing them with browser APIs.',
'Node provides filesystem, process, HTTP, and stream APIs. Prefer asynchronous file operations in servers so other requests can continue while storage is busy.',
'Use node:fs/promises and explicit encodings for text. In a real backend, validate filenames, restrict paths to intended directories, and check permissions before acting.',
'The lab allows temporary files only inside its disposable container. It has no external network and no persistent filesystem. Never accept arbitrary paths from an HTTP request.',
'Write hello to /tmp/example.txt, read it as UTF-8, and print hello.',
'import {writeFile, readFile} from "node:fs/promises";\nawait writeFile("/tmp/example.txt","hello","utf8");\nconsole.log(await readFile("/tmp/example.txt","utf8"));','hello',
'Why prefer async file APIs in a server?',['They let the event loop serve other work while waiting','They remove all permissions','They make files public'],0,'Asynchronous I/O avoids blocking the event loop during the wait.',
reference='https://nodejs.org/api/fs.html')

J('08 / Production practice','capstone','Build a tested task-list model','Combine state, validation, collection methods, and tests.',
'A small application benefits from a clear data model before UI details. Give records stable IDs, expose a narrow set of operations, and derive counts from source state rather than duplicating them.',
'Separate add, toggle, and remove behavior from rendering. Test the model, then wire it to DOM events and persistence in a browser project.',
'Array indexes are fragile IDs after deletion or sorting. Do not mutate a collection while assuming its order and length stay unchanged.',
'Build two tasks, mark the first completed, print the remaining count, and assert it equals 1.',
'import assert from "node:assert/strict";\nlet tasks = [{id:1,title:"Learn JS",done:false},{id:2,title:"Build a page",done:false}];\ntasks = tasks.map(task => task.id === 1 ? {...task,done:true} : task);\nconst remaining = tasks.filter(task => !task.done).length;\nassert.equal(remaining,1);\nconsole.log(remaining);','1',
'What is a robust record identity?',['Its current array position','A stable unique ID','Its display color'],1,'Stable IDs survive reordering, filtering, and deletion.')

V('01 / Java foundations','first-program','Your first Java program','Compile and run a class with a main method.',
'Java source is compiled into bytecode that runs on a Java Virtual Machine. Java and JavaScript are unrelated languages with different type systems and runtimes.',
'This course uses Java 21. A conventional entry point is public static void main(String[] args). Keep the public class name Main in this single-file lab. System.out.println writes a line.',
'Java is case-sensitive. A public class normally lives in a file with a matching name. Compilation errors happen before program execution and differ from runtime exceptions.',
'Print Hello, Java!','System.out.println("Hello, Java!");','Hello, Java!',
'What runs Java bytecode?',['A CSS parser','The JVM','Only a browser DOM'],1,'The Java Virtual Machine executes bytecode.',
reference='https://dev.java/learn/getting-started/')

V('01 / Java foundations','types','Types, variables & numeric operations','Understand primitive values and compile-time checks.',
'Java is statically typed. Primitive types include int, long, double, boolean, and char. Reference types point to objects. A variable has a declared type even when var infers it locally.',
'int division truncates toward zero. Use a floating-point operand for a fractional result. long literals often need L and narrowing conversions require explicit casts.',
'Integer overflow wraps silently in ordinary arithmetic. Math.addExact and related methods can detect it. var is not dynamic typing and cannot replace every type declaration.',
'Print 7 / 2 as an int and 7 / 2.0 as a double.',
'System.out.println(7 / 2);\nSystem.out.println(7 / 2.0);','3\n3.5',
'What is the type of 7 / 2?',['double','int','String'],1,'Both operands are int, so integer division produces int.')

V('01 / Java foundations','strings','Strings, equality & formatting','Compare text by content and build output clearly.',
'String is immutable. Methods such as trim and toUpperCase return values rather than changing the original. String literals are objects, not primitive character arrays.',
'Use equals for content equality and Objects.equals when either reference may be null. == checks reference identity for objects. StringBuilder is useful for repeated concatenation in loops.',
'String indexes operate on UTF-16 code units, which are not always complete user-perceived characters. Locale-sensitive case conversion deserves an explicit locale.',
'Compare two separate String("Java") objects using equals, then print JAVA.',
'String a = new String("Java");\nString b = new String("Java");\nSystem.out.println(a.equals(b));\nSystem.out.println(a.toUpperCase(java.util.Locale.ROOT));','true\nJAVA',
'Which compares String content?',['== in all cases','equals','instanceof'],1,'equals compares content; == compares reference identity.')

V('01 / Java foundations','branches','Conditions, switch & boolean logic','Choose behavior from validated inputs.',
'if/else selects blocks using boolean expressions. && and || short-circuit. Modern switch expressions can return a value with arrow cases; a multi-statement arm uses yield.',
'Use enums for a fixed set of named states. Keep branches readable by extracting complicated conditions into named methods.',
'Java does not treat integers or objects as booleans. Use comparisons explicitly. Legacy switch statements can fall through without break; arrow cases do not.',
'Use a switch expression to map 2 to Tue, with Unknown as the default. Print Tue.',
'int day = 2;\nString name = switch (day) {\n  case 1 -> "Mon";\n  case 2 -> "Tue";\n  default -> "Unknown";\n};\nSystem.out.println(name);','Tue',
'Do arrow switch cases fall through?',['Yes','No','Only for strings'],1,'Arrow cases avoid the implicit fall-through of colon cases.')

V('01 / Java foundations','loops-arrays','Loops & arrays','Traverse fixed-size collections safely.',
'Arrays have a fixed length and store elements of one declared component type. Indexes start at zero. The enhanced for loop reads each element without an explicit index.',
'Use an indexed loop when position matters. An accumulator belongs outside the loop, and its type must be large enough for the result.',
'Accessing index length is out of bounds. Arrays.toString prints contents; printing an array reference directly is generally not a useful representation.',
'Sum the array {2,4,6} with a loop and print 12.',
'int[] values = {2,4,6};\nint total = 0;\nfor (int value : values) total += value;\nSystem.out.println(total);','12',
'What is the final valid index of a length-3 array?',['3','2','1'],1,'Indexes are 0, 1, and 2.')

V('02 / Methods & object design','methods','Methods, overloading & value passing','Define reusable operations with explicit types.',
'A method declares parameter types and a return type. static methods belong to the class rather than a particular instance. Overloading uses the same name with different parameter lists.',
'Java passes arguments by value. For an object, the copied value is a reference: a method can mutate the referenced object but cannot replace the caller’s variable itself.',
'You cannot overload solely by return type. Avoid ambiguous overloads and distinguish a returned result from printed output.',
'Define static int square(int value). Print square(5).',
'public class Main {\n  static int square(int value) { return value * value; }\n  public static void main(String[] args) { System.out.println(square(5)); }\n}','25',
'How does Java pass arguments?',['By value','Always by reference','Only by copying entire objects'],0,'Even an object reference is passed as a copied value.')

V('02 / Methods & object design','classes','Classes, constructors & encapsulation','Keep invariants inside an object.',
'A class defines fields and methods. A constructor initializes a new instance and can validate initial data. Access modifiers control which code can see a member.',
'Make fields private and expose operations that preserve the object’s rules. this refers to the current instance and helps distinguish fields from parameters.',
'Getters and setters for every field are not automatically good encapsulation. A domain method such as deposit can enforce rules that a generic setBalance would bypass.',
'Create an Account with private balance, deposit 20, and print 20.',
'public class Main {\n  static class Account {\n    private int balance;\n    void deposit(int amount) { if (amount <= 0) throw new IllegalArgumentException(); balance += amount; }\n    int balance() { return balance; }\n  }\n  public static void main(String[] args) {\n    Account account = new Account(); account.deposit(20); System.out.println(account.balance());\n  }\n}','20',
'Why keep fields private?',['To prevent all object creation','To preserve rules through controlled operations','To make execution faster automatically'],1,'Encapsulation lets the class protect valid state.')

V('02 / Methods & object design','interfaces','Interfaces & polymorphism','Program against behavior rather than a concrete implementation.',
'An interface defines a contract. A class implements it and supplies behavior. A variable typed as the interface can refer to any compatible implementation.',
'Use @Override to catch signature mistakes. Prefer composition when you want to assemble behavior without inheriting an entire class hierarchy.',
'Inheritance should express a substitutable relationship. Sharing a little implementation is not always a reason to extend a class.',
'Define Greeter with greet(), implement it, and print Hello through an interface reference.',
'public class Main {\n  interface Greeter { String greet(); }\n  static class Friendly implements Greeter {\n    @Override public String greet() { return "Hello"; }\n  }\n  public static void main(String[] args) { Greeter g = new Friendly(); System.out.println(g.greet()); }\n}','Hello',
'What does an interface mainly describe?',['A behavioral contract','A database row count','A memory address'],0,'An interface decouples the required behavior from its implementation.')

V('02 / Methods & object design','records-enums','Records, enums & value models','Represent constrained data with less boilerplate.',
'Records declare data carriers and generate accessors, equals, hashCode, and toString based on components. Enums represent a fixed set of named constants.',
'A compact record constructor can validate components. Records work well for immutable-shaped values, request models, and results; enum switches can make states explicit.',
'Record fields are final, but referenced collections can still be mutable. Copy mutable inputs if the record must be deeply immutable.',
'Declare record Point(int x,int y) and enum Axis {X,Y}. Print a point’s x and Axis.Y.',
'public class Main {\n  record Point(int x, int y) {}\n  enum Axis {X, Y}\n  public static void main(String[] args) { Point p = new Point(3,4); System.out.println(p.x()); System.out.println(Axis.Y); }\n}','3\nY',
'Are mutable objects inside a record automatically frozen?',['Yes','No','Only lists'],1,'A final reference does not freeze the referenced object.')

V('02 / Methods & object design','equality','equals, hashCode & identity','Make value objects behave correctly in collections.',
'== compares object identity. equals defines logical equality. Equal objects must return equal hashCode values, or hash-based collections can behave incorrectly.',
'Records generate consistent value equality. For custom classes, use both relevant immutable fields in equals and hashCode. Objects.equals handles null safely.',
'Changing a field used by hashCode after inserting a key into HashMap can make lookups fail. Prefer immutable keys.',
'Put two equal Point records into a HashSet and print its size, 1.',
'public class Main {\n  record Point(int x,int y) {}\n  public static void main(String[] args) {\n    var points = new java.util.HashSet<Point>();\n    points.add(new Point(1,2)); points.add(new Point(1,2)); System.out.println(points.size());\n  }\n}','1',
'What must equal objects have?',['Different hash codes','Equal hash codes','The same memory location'],1,'equals and hashCode must satisfy the collection contract.')

V('03 / Collections & generics','lists','Lists & mutability','Choose between a mutable list and an unmodifiable value.',
'List preserves order and allows duplicates. ArrayList supports efficient indexed access and appending. Program to List when callers do not need a specific implementation.',
'List.of creates an unmodifiable list and rejects nulls. Use new ArrayList<>(...) when you need structural changes. Distinguish an unmodifiable view from an independent copy.',
'Removing items inside an enhanced loop can cause ConcurrentModificationException. Use removeIf or an iterator’s supported removal method.',
'Create a mutable list [3,1,2], sort it, and print [1, 2, 3].',
'var values = new java.util.ArrayList<>(java.util.List.of(3,1,2));\nvalues.sort(Integer::compareTo);\nSystem.out.println(values);','[1, 2, 3]',
'Can you add to List.of(1,2)?',['Yes','No, it is unmodifiable','Only on Mondays'],1,'Use a mutable implementation when structural changes are required.')

V('03 / Collections & generics','maps-sets','Maps, sets & counting','Index data and enforce uniqueness.',
'Map associates keys with values; Set stores unique elements. HashMap and HashSet do not promise iteration order. LinkedHashMap preserves insertion order; TreeMap sorts keys.',
'merge simplifies counting: counts.merge(word, 1, Integer::sum). Use getOrDefault when absence should yield a default. containsKey distinguishes an absent key from a mapped null where null is allowed.',
'Do not depend on HashMap iteration order for stable output. If order matters, choose an implementation or sort explicitly.',
'Count the words a,b,a using a map and print the count of a.',
'var counts = new java.util.HashMap<String,Integer>();\nfor (String word : java.util.List.of("a","b","a")) counts.merge(word,1,Integer::sum);\nSystem.out.println(counts.get("a"));','2',
'Which map preserves insertion order?',['HashMap by contract','LinkedHashMap','All maps'],1,'LinkedHashMap explicitly maintains insertion order.')

V('03 / Collections & generics','generics','Generics & bounded types','Make reusable code type-safe.',
'Generics parameterize classes and methods with types. List<String> lets the compiler reject the wrong element type and avoids unchecked casts when reading.',
'A bound such as T extends Number constrains a type parameter. Wildcards support flexible APIs: ? extends T is useful for producers and ? super T for consumers.',
'Generics are invariant: List<Integer> is not a List<Number>. Most generic type information is erased at runtime, and primitives need wrapper types as arguments.',
'Write a generic first(List<T>) method and print its result for List.of("Java","CSS").',
'public class Main {\n  static <T> T first(java.util.List<T> items) { return items.get(0); }\n  public static void main(String[] args) { System.out.println(first(java.util.List.of("Java","CSS"))); }\n}','Java',
'Is List<Integer> a subtype of List<Number>?',['Yes','No','Only if empty'],1,'Generic types are invariant; use an appropriate wildcard when needed.')

V('03 / Collections & generics','lambdas','Lambdas & functional interfaces','Pass behavior as a typed value.',
'A functional interface has one abstract method. A lambda supplies its implementation, and a method reference can name an existing compatible method.',
'Predicate<T> tests a value, Function<T,R> transforms it, and Consumer<T> performs an action. Keep lambdas short enough that the surrounding pipeline remains understandable.',
'Captured local variables must be final or effectively final. That restriction does not automatically make captured objects immutable or thread-safe.',
'Use Predicate<Integer> to test even numbers. Print true for 4 and false for 5.',
'java.util.function.Predicate<Integer> even = n -> n % 2 == 0;\nSystem.out.println(even.test(4));\nSystem.out.println(even.test(5));','true\nfalse',
'What does Predicate<T> return?',['boolean','Always String','void'],0,'A predicate is a boolean-valued function.')

V('03 / Collections & generics','streams','Streams & collectors','Describe a data transformation as a pipeline.',
'A stream is a one-use computation over a source, not a collection that stores results. Intermediate operations such as filter and map are lazy; a terminal operation triggers processing.',
'Use mapToInt for numeric operations without unnecessary boxing. Collectors group or summarize values. Keep operations free of shared mutable side effects.',
'A stream cannot be reused after a terminal operation. Parallel streams are not automatically faster and may introduce ordering or thread-safety problems.',
'Filter even numbers from [1,2,3,4], double them, and print their sum 12.',
'int total = java.util.List.of(1,2,3,4).stream().filter(n -> n % 2 == 0).mapToInt(n -> n * 2).sum();\nSystem.out.println(total);','12',
'When do lazy intermediate operations execute?',['At a terminal operation','Always at declaration','Never'],0,'A terminal operation consumes the pipeline.')

V('04 / Errors & resources','exceptions','Exceptions & recovery','Handle checked and unchecked failures intentionally.',
'Checked exceptions must be caught or declared; unchecked exceptions extend RuntimeException and do not have that compiler requirement. Error represents serious JVM-level problems not normally recovered from.',
'Catch specific failures at a boundary where you can recover or explain them. Preserve causes when wrapping exceptions. finally is for cleanup, not for masking an earlier exception with a return.',
'Do not catch Exception everywhere and continue as if an operation succeeded. User messages and diagnostic logs often need different levels of detail.',
'Parse "abc" as an integer, catch NumberFormatException, and print Invalid number.',
'try { Integer.parseInt("abc"); }\ncatch (NumberFormatException error) { System.out.println("Invalid number"); }','Invalid number',
'Which is an unchecked exception?',['RuntimeException','Every subclass of Exception without exception','Only IOException'],0,'RuntimeException and its subclasses are unchecked.')

V('04 / Errors & resources','resources','Try-with-resources & deterministic cleanup','Close resources even when code fails.',
'AutoCloseable defines close(). try-with-resources closes declared resources automatically, in reverse declaration order, when the block ends.',
'Use it for files, streams, database statements, and connections. If both the body and close fail, the close failure is suppressed rather than replacing the original exception.',
'Garbage collection is not a reliable resource-cleanup schedule. Memory management and closing operating-system resources are separate concerns.',
'Read a line from a StringReader through BufferedReader in try-with-resources. Print Java.',
'try (var reader = new java.io.BufferedReader(new java.io.StringReader("Java\\n"))) {\n  System.out.println(reader.readLine());\n}','Java',
'What interface supports try-with-resources?',['Runnable','AutoCloseable','Comparable'],1,'Resources implement AutoCloseable so Java can call close automatically.')

V('04 / Errors & resources','files','Paths, text files & NIO','Read and write files with explicit encodings.',
'java.nio.file.Path models a filesystem path; Files contains convenient operations. readString and writeString handle text, while streams suit larger data.',
'Normalize and validate paths derived from untrusted input. Resolve inside an intended base directory and account for symlinks when enforcing security.',
'Reading a huge file into one String can exhaust memory. The lab filesystem is disposable and only /tmp is writable; do not expect data to persist after a run.',
'Write saved to /tmp/note.txt with UTF-8, read it, and print saved.',
'var path = java.nio.file.Path.of("/tmp/note.txt");\njava.nio.file.Files.writeString(path,"saved",java.nio.charset.StandardCharsets.UTF_8);\nSystem.out.println(java.nio.file.Files.readString(path,java.nio.charset.StandardCharsets.UTF_8));','saved',
'Which API models a filesystem path?',['Path','StringBuilder only','Thread'],0,'Path provides filesystem-aware path operations.')

V('04 / Errors & resources','optional','Optional & absent values','Make an optional result explicit.',
'Optional<T> represents a present value or absence. It is useful as a return type when not finding a result is normal rather than exceptional.',
'Use map, flatMap, filter, or orElseGet to compose optional results. orElse eagerly evaluates its argument, while orElseGet invokes a supplier only when empty.',
'Calling get without checking presence reintroduces a failure-prone contract. Optional is not a replacement for every field, parameter, or collection element.',
'Create Optional.empty(), provide "Guest" with orElseGet, and print Guest.',
'java.util.Optional<String> name = java.util.Optional.empty();\nSystem.out.println(name.orElseGet(() -> "Guest"));','Guest',
'Which fallback is lazy?',['orElseGet','orElse','get'],0,'orElseGet calls its supplier only when the optional is empty.')

V('05 / Standard library','time','Date, time & zones','Use the java.time types that match your domain.',
'LocalDate is a calendar date without a zone; Instant is a point on the UTC timeline. ZonedDateTime combines local date/time with a region’s rules.',
'Use Duration for time-based amounts and Period for calendar-based amounts. DateTimeFormatter handles parsing and formatting. Inject a Clock when time-dependent logic needs repeatable tests.',
'A local day can be 23 or 25 hours across daylight-saving changes. Do not treat every business date operation as adding 86,400 seconds.',
'Create LocalDate.of(2026,1,31), add one month, and print 2026-02-28.',
'var date = java.time.LocalDate.of(2026,1,31);\nSystem.out.println(date.plusMonths(1));','2026-02-28',
'Which type represents a point on the UTC timeline?',['LocalDate','Instant','Period'],1,'Instant represents a timestamp independent of a local calendar zone.')

V('05 / Standard library','decimal','BigDecimal & exact decimal calculations','Avoid binary floating-point surprises in money calculations.',
'BigDecimal represents decimal values with arbitrary precision and scale. Construct it from decimal strings or valueOf rather than a binary floating-point approximation.',
'Specify rounding policy when division may not terminate. compareTo compares numeric value, while equals also considers scale, so 1.0 and 1.00 can compare numerically equal but not be equals.',
'Precision, scale, and business rounding rules are separate decisions. Do not silently round every intermediate result unless the domain requires it.',
'Add BigDecimal("0.1") and BigDecimal("0.2") and print 0.3.',
'var a = new java.math.BigDecimal("0.1");\nvar b = new java.math.BigDecimal("0.2");\nSystem.out.println(a.add(b));','0.3',
'Which constructor avoids importing a binary approximation?',['new BigDecimal("0.1")','new BigDecimal(0.1)','Both are always identical'],0,'A string expresses the intended decimal value exactly.')

V('05 / Standard library','regex','Regex, parsing & validation','Recognize structured text with clear limits.',
'Pattern compiles a regular expression; Matcher applies it. matches requires the whole input to match, while find searches for a matching subsequence.',
'Java string literals and regexes both use escaping, so a regex backslash often needs a second backslash in source. Compile reused patterns once.',
'Regex validation is not authorization and cannot replace a real parser for complex languages. Avoid patterns with catastrophic backtracking on untrusted text.',
'Validate three uppercase letters followed by two digits. Print true for ABC12 and false for abc12.',
'var pattern = java.util.regex.Pattern.compile("[A-Z]{3}\\\\d{2}");\nSystem.out.println(pattern.matcher("ABC12").matches());\nSystem.out.println(pattern.matcher("abc12").matches());','true\nfalse',
'What does Matcher.matches require?',['A whole-input match','Any substring match','A file extension'],0,'Use find when you want to search for a matching subsequence.')

V('06 / Concurrency','threads','Threads, races & synchronization','Understand why shared updates need coordination.',
'A thread executes independently within a process. Shared mutable state can produce races; count++ is a read-modify-write operation, not an atomic increment.',
'synchronized protects a critical section and establishes visibility rules. AtomicInteger provides atomic operations for a single integer. Prefer immutable data and limited sharing when possible.',
'volatile improves visibility but does not make compound operations such as increment atomic. join waits for a thread to finish.',
'Start two threads that each increment one AtomicInteger 100 times, join them, and print 200.',
'var count = new java.util.concurrent.atomic.AtomicInteger();\nRunnable task = () -> { for (int i=0;i<100;i++) count.incrementAndGet(); };\nThread a = new Thread(task), b = new Thread(task);\na.start(); b.start(); a.join(); b.join();\nSystem.out.println(count.get());','200',
'Does volatile make count++ atomic?',['Yes','No','Only when count starts at zero'],1,'Visibility is different from atomic read-modify-write behavior.')

V('06 / Concurrency','executors','Executors, futures & virtual threads','Manage tasks without manually creating every platform thread.',
'ExecutorService schedules tasks and returns Future results. Java 21 virtual threads are lightweight threads suited to many blocking I/O tasks, not a way to make CPU-bound work magically faster.',
'Bound expensive resources such as database connections independently of thread count. Close an executor or shut it down deliberately and handle task failures from Future.get.',
'Cancellation is cooperative: tasks must respond to interruption. Do not swallow InterruptedException without restoring the interrupt status or propagating it appropriately.',
'Use a single-thread executor to submit a task returning 42, print its Future result, and close the executor.',
'try (var executor = java.util.concurrent.Executors.newSingleThreadExecutor()) {\n  var result = executor.submit(() -> 42);\n  System.out.println(result.get());\n}','42',
'What are virtual threads especially suited to?',['Large numbers of blocking I/O tasks','Automatically accelerating every CPU calculation','Replacing all locks'],0,'They reduce the cost of waiting threads, not the computational work.')

V('06 / Concurrency','completablefuture','CompletableFuture & composition','Combine asynchronous stages and handle failures.',
'CompletableFuture models a result that may arrive later and supports transformations with thenApply, composition with thenCompose, and recovery with exceptionally.',
'thenCompose avoids a nested future when a stage already returns one. For real blocking work, use an appropriate executor instead of unexpectedly occupying the common pool.',
'Non-async stages may run on the thread completing the previous stage. Async does not guarantee a particular thread unless you provide and understand the executor.',
'Start from completedFuture(5), double it with thenApply, and print 10.',
'var result = java.util.concurrent.CompletableFuture.completedFuture(5).thenApply(n -> n * 2);\nSystem.out.println(result.join());','10',
'Which operation flattens a stage returning a future?',['thenCompose','thenApply in every case','toString'],0,'thenCompose chains the returned stage without creating a nested future.')

V('07 / Backend development','http','HTTP clients & API contracts','Build a request and handle responses deliberately.',
'Java’s HttpClient sends HTTP requests synchronously or asynchronously. HttpRequest describes the URI, method, headers, body, and timeout.',
'Check status codes, parse bodies according to Content-Type, and set timeouts. Authentication secrets belong in protected server configuration, not in committed source.',
'The lab blocks external network access. This exercise constructs and inspects a request without sending it. Production clients need retry policies that respect idempotency and service limits.',
'Build a GET request for https://example.com with a 5-second timeout. Print GET and example.com.',
'var request = java.net.http.HttpRequest.newBuilder(java.net.URI.create("https://example.com")).timeout(java.time.Duration.ofSeconds(5)).GET().build();\nSystem.out.println(request.method());\nSystem.out.println(request.uri().getHost());','GET\nexample.com',
'Should a production HTTP client have a timeout?',['Yes','Never','Only for localhost'],0,'Timeouts prevent a dependency from holding resources indefinitely.')

V('07 / Backend development','jdbc','JDBC, parameters & transactions','Learn the boundary between Java and a relational database.',
'JDBC uses Connection, PreparedStatement, and ResultSet. A driver connects to a specific database. Prepared statements keep SQL structure separate from parameter values.',
'Typical code is connection.prepareStatement("SELECT name FROM users WHERE id = ?"), then statement.setLong(1, id), then executeQuery(). Close resources with try-with-resources. For multi-step writes, disable auto-commit, commit on success, and roll back on failure.',
'Never concatenate untrusted values into SQL. Parameters substitute values, not arbitrary table names or SQL syntax. This lab has no JDBC driver or database, so the exercise checks the parameterized statement structure only.',
'Create a parameterized SQL string selecting name from users by id, then print it. Do not concatenate an ID into the query.',
'String sql = "SELECT name FROM users WHERE id = ?";\nSystem.out.println(sql);','SELECT name FROM users WHERE id = ?',
'What belongs in a PreparedStatement parameter?',['A data value','An arbitrary table name in every query','An entire SQL keyword clause'],0,'Placeholders represent values; dynamic identifiers need a trusted allowlist.',
reference='https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html')

V('07 / Backend development','testing-builds','Testing, Maven & Gradle','Make builds repeatable and behavior verifiable.',
'Maven and Gradle declare dependencies and build steps. A conventional layout separates src/main/java and src/test/java. JUnit tests assert behavior and run as part of a build.',
'Pin dependency versions, run tests in CI, and separate fast unit tests from integration tests that need infrastructure. In this dependency-free lab, throw AssertionError for a failed assertion.',
'Java assert statements are disabled unless enabled with -ea. Do not rely on them for user-input validation. A passing build does not remove the need for security and compatibility checks.',
'Define add(a,b), check add(2,3) equals 5 with an explicit assertion, and print Tests passed.',
'public class Main {\n  static int add(int a,int b) { return a+b; }\n  public static void main(String[] args) {\n    if (add(2,3) != 5) throw new AssertionError("Expected 5");\n    System.out.println("Tests passed");\n  }\n}','Tests passed',
'Are Java assert statements enabled by default?',['Yes','No; use -ea','Only inside loops'],1,'Explicit validation should not depend on the assertion flag.')

V('08 / Production Java','jvm-security','JVM memory, logging & secure services','Connect language skills to reliable application behavior.',
'The JVM manages heap memory and garbage collection; each thread also needs stack space. Reachable objects remain live, so caches and listeners can retain memory unintentionally.',
'Profile before tuning, bound caches and request sizes, and log useful event context without passwords or tokens. At API boundaries, authenticate identity, authorize each action, validate input, and return deliberate status codes.',
'Garbage collection does not prevent memory leaks through unwanted references. Do not deserialize untrusted native Java objects. Frameworks such as Spring add routing and dependency injection but do not replace these fundamentals.',
'Validate that an account name is nonblank and at most 20 characters; print Valid account for Mira.',
'String account = "Mira";\nif (account.isBlank() || account.length() > 20) throw new IllegalArgumentException("Invalid account");\nSystem.out.println("Valid account");','Valid account',
'Can reachable but unwanted objects cause a Java memory leak?',['Yes','No, GC removes every unused-looking object','Only primitive ints'],0,'The collector retains reachable objects even if the application no longer needs them.')

V('08 / Production Java','capstone','Build an inventory model','Combine records, collections, validation, and tests.',
'A small domain model should make invalid states difficult to create. Records can represent items; maps can index them by stable ID; methods can enforce rules for updates.',
'Start with deterministic business logic and tests before adding database persistence or an HTTP framework. Use integer minor units or BigDecimal for prices and explicit quantity validation.',
'Do not expose mutable internal collections directly. A real multi-user service also needs transactions, authorization, and concurrency control; an in-memory exercise is not a production backend.',
'Create Item(name,quantity), reject negative quantities, sum quantities 3 and 4, assert 7, and print Total: 7.',
'public class Main {\n  record Item(String name,int quantity) {\n    Item { if (name == null || name.isBlank() || quantity < 0) throw new IllegalArgumentException(); }\n  }\n  public static void main(String[] args) {\n    var items = java.util.List.of(new Item("Pen",3),new Item("Book",4));\n    int total = items.stream().mapToInt(Item::quantity).sum();\n    if (total != 7) throw new AssertionError();\n    System.out.println("Total: " + total);\n  }\n}','Total: 7',
'What should a domain model protect?',['Its invariants and valid state','Only the UI colors','The order of imported packages'],0,'Validation and controlled operations preserve the rules of the domain.')

data['lessons']+=new
data['tracks']=[
 dict(id='html',name='HTML',subtitle='Structure & accessibility',description='Documents, forms, semantics, and accessible content.'),
 dict(id='css',name='CSS',subtitle='Layout & design',description='Responsive layouts, typography, animation, and maintainable styles.'),
 dict(id='javascript',name='JavaScript',subtitle='Browser & application logic',description='Core language, DOM, async code, testing, and Node.js.'),
 dict(id='java',name='Java',subtitle='Objects & backend foundations',description='Java 21, collections, concurrency, files, and backend practices.')]
data['projects']=[p for p in data['projects'] if p.get('track') not in ('java','javascript')]
for track,slug,title,desc,checklist,starter in [
('javascript','js-taskboard','Task-list model','Build and test add, toggle, filter, and remove operations before connecting a browser UI.',
 ['Assign stable IDs to tasks','Reject blank titles','Toggle completion without losing other fields','Test removal and remaining counts','Add a DOM interface in your own browser project'],
 'const tasks = [];\n// Add your model functions and assertions here.\nconsole.log(tasks.length);'),
('javascript','js-data-report','Sales report','Transform sample records into a sorted, grouped report with validated totals.',
 ['Validate every amount','Group rows by category','Compute totals without mutating input','Format a readable report','Test an empty dataset'],
 'const sales = [{category:"Books",amount:12},{category:"Books",amount:8},{category:"Tools",amount:20}];\n// Group, sum, and print a report.\n'),
('java','java-library','Library catalogue','Model books, borrowing rules, and a searchable catalogue with plain Java.',
 ['Use stable book IDs','Prevent borrowing an unavailable book','Implement search by title','Keep internal collections private','Test success and failure paths'],
 'public class Main {\n  record Book(int id, String title) {}\n  public static void main(String[] args) {\n    var books = java.util.List.of(new Book(1,"Java Basics"));\n    System.out.println(books);\n  }\n}'),
('java','java-ledger','Expense ledger','Build an expense model with precise decimal arithmetic and category totals.',
 ['Use BigDecimal from strings','Reject invalid amounts','Group totals by category','Keep records immutable','Test rounding and empty input'],
 'public class Main {\n  public static void main(String[] args) {\n    var amount = new java.math.BigDecimal("12.50");\n    System.out.println(amount);\n  }\n}')
]:
 data['projects'].append(dict(id=slug,track=track,title=title,type=track.title(),level='Intermediate',description=desc,time='2–4 hours',tags=[track.title(),'Testing','Data modeling'],checklist=checklist,html=starter,css=''))
(ROOT/'data/curriculum.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print({t:sum(l['track']==t for l in data['lessons']) for t in ['html','css','javascript','java']})
print('Projects:',len(data['projects']))