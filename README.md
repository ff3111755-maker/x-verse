# X Verse — Coding Academy

A full-stack learning website for HTML, CSS, JavaScript, and Java.

## Deployment

**Start with [DEPLOYMENT.md](DEPLOYMENT.md).** Deploy manually to Render Free using Docker, no Blueprint or database required. Learners save progress/drafts in their browser without signing in, with JSON export/import backups. Vercel can host the frontend with Render as the API. Protected Java/JavaScript execution still needs a separate runner.

## Courses and features

- **106 lessons:** 20 HTML, 26 CSS, 30 JavaScript, 30 Java.
- Each lesson includes concepts, an exercise, a quiz, an example solution, and official-reference links.
- **Seven projects:** three HTML/CSS projects, two JavaScript projects, and two Java projects.
- Sandboxed live HTML/CSS preview with smart paired-tag completion.
- Executable JavaScript (Node.js 22) and Java (JDK 21), with output and compiler/runtime errors.
- IndexedDB progress, drafts, XP, milestones, and validated JSON backup export/import—no login required.
- Five color presets, custom accent, draggable holographic visual, reduced-motion support.
- Responsive layouts and keyboard-accessible editors.
- X Verse branding and no companion.

Courses cover a broad practical path from foundations to advanced concepts, not every API or framework in either ecosystem. Frameworks such as Spring and React are not complete standalone courses here. HTML/CSS checks inspect required patterns; programming checks execute source and compare expected output. Passing an exercise is not proof of general correctness.

## Programming lab scope

JavaScript executes ES modules in Node.js. A **linkedom DOM fixture** supplies `document` and `window` for browser API exercises. It is not a browser layout engine and does not render JavaScript visually. Its starting document is:

```html
<main id="app">
  <h1>Ready</h1>
  <button id="add">Add</button>
  <ul id="list"></ul>
</main>
```

Java supports one source file named `Main.java`, with a public `Main` class and standard-library dependencies. Nested/additional package-private classes in that file are supported.

The runtime has no external network, no interactive standard input, no installed third-party Java dependencies, and no persistent user filesystem. HTTP lessons construct requests or use local response objects; JDBC lessons teach prepared statements without connecting to a database. Use a local development environment for multi-file applications, external APIs, databases, and framework projects.

## Stack

React, Vite, Radix Dialog, Lucide, self-hosted fonts; FastAPI, Uvicorn, IndexedDB in the browser; optional legacy SQLite account mode; Docker-isolated code execution when configured.

## Local setup

Prerequisites: Node.js 22.12+, Python 3.12+, uv. Docker is optional unless using local program execution.

```sh
cd frontend
npm ci
npm run build
cd ..
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Open http://localhost:8000. Defaults are `STORAGE_MODE=browser` and `RUNNER_MODE=disabled`: no database or sign-in setup is needed for local learning records. Environment variables are read from the process, not automatically from `.env`.

A separate protected runner is optional; see [RUNNER.md](RUNNER.md). Java/JavaScript reading, editing, and source download work without it; executable checks and completion require execution. This is not a full offline app: curriculum loading and exercise checks still use the API.

The runtime curriculum is already included. To regenerate after authoring changes:

```sh
python build_curriculum.py
python add_programming.py
```

Run both scripts: the first builds HTML/CSS; the second adds JavaScript, Java, course metadata, and programming projects.

## Identity and deployment security

Optional server/account deployments verify bearer tokens through Supabase Auth. Browser-storage mode stores learning records locally and needs no account. No authentication cookies are used; exact CORS origins control cross-origin browser access. `AUTH_MODE=promptql` is an explicit compatibility option ONLY for PromptQL's trusted app proxy. Do not enable it on public standalone hosting.

The web image has no Docker access. A separate runner receives only language/source from the API with its own server-side credential; learner tokens are never sent into execution containers.

Program source runs in fresh containers, never directly in the API process:

- Non-root UID/GID 65534; no host directories or platform credentials mounted.
- No external network; read-only root; dropped capabilities; no-new-privileges.
- Docker's default seccomp profile.
- 384 MB RAM, 0.75 CPU, 64 PIDs, and a 48 MB disposable `/tmp`.
- 15-second wall-clock limit and 32 KB combined output limit.
- Two concurrent runs per API process and 20 run requests/minute per signed-in account in standalone mode.

Containers share the host kernel: this is not a claim of perfect isolation. A public multi-tenant service should use a separately hardened execution tier with infrastructure-level quotas, patched pinned images, and sandbox review. The web service's Docker access is privileged; protect it accordingly. Keep Uvicorn at one worker unless shared quotas are implemented.

`deploy/runner.service` is the dedicated-host runner example; it is not the Render start command.

The HTML/CSS preview is an iframe with no script permissions and a restrictive CSP. Downloaded user source is ordinary code: review it before executing or sharing it.

## Persistence

IndexedDB (`xverse-learning-v1`) stores one shared local learning profile per browser and origin. Nothing is sent to the server during draft autosave. Exercise checks/runs intentionally send the current exercise source for validation/execution. Previous account data is not automatically copied or deleted.

Browser storage can be cleared or evicted and does not sync across devices. Use Preferences & backups to export before changing devices/domains. Import validates a versioned JSON backup (or older account export) and merges atomically, keeping existing completions and the newer draft for each document. Backups include progress/code, not appearance preferences or temporary checklist marks.

In optional `STORAGE_MODE=server`, SQLite uses `SQLITE_PATH` and needs a persistent disk. Switching to browser mode leaves that database intact. The source archive excludes databases, tokens, and test identities.

## Tests

```sh
.venv/bin/python test_browser_backend.py
.venv/bin/python test_hosting.py
cd frontend
node test-tags.mjs
node test-browser-storage.mjs
node test-browser-failures.mjs
```

Run a built web service on localhost:8000 before browser tests. `test_hosting.py` tests optional server mode with mocked provider identity. `test_browser_backend.py` checks the no-database default. Browser tests require Chrome (or adjust the Playwright channel), use isolated temporary browser contexts, and create no real accounts.

Legacy UI/API tests target account mode; do not enable PromptQL-header trust on public hosting to run them. `test_courses.py` checks all 60 Java/JavaScript solutions with Docker. `test_remote_runner.py` exercises a protected local runner.

## Files

- `server.py`: API, identity, ownership, draft storage, and course checks.
- `code_runner.py`: bounded disposable Docker execution.
- `Dockerfile.javascript`, `javascript-runner.mjs`: Node runtime and DOM fixture.
- `build_curriculum.py`, `add_programming.py`: course authoring.
- `data/curriculum.json`: complete runtime curriculum.
- `frontend/src/main.jsx`: courses, quizzes, projects, and HTML/CSS editor.
- `frontend/src/program-lab.jsx`: executable language editor and console.
- `frontend/src/visuals.jsx`: branding, preferences, hologram.
- `frontend/src/editor-tools.js`: paired HTML tag completion.
- `frontend/src/*.css`: application styles.
- `deploy/runner.service`: optional dedicated-runner service example.
## Hosting files

- `DEPLOYMENT.md`: step-by-step Render, Vercel, auth, and runner setup.
- `render.yaml`, `Dockerfile`, `deploy/start-web.py`: browser-mode web/API service (no disk required).
- `vercel.json`: static frontend deployment.
- `hosting.py`: explicit auth modes and validated deployment settings.
- `runner_gateway.py`, `runner_server.py`: authenticated remote execution boundary.
- `frontend/src/api-client.js`, `account.jsx`: standalone API client and sign-in UI.
- `.env.example`, `frontend/.env.example`: safe configuration templates.

- `frontend/src/browser-store.js`: IndexedDB records, validated backups, atomic imports.
- `frontend/src/storage-panel.jsx`: backup and storage controls.
- `RUNNER.md`: optional protected execution setup.
