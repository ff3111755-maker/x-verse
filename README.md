# X Verse — Coding Academy

A full-stack learning website for HTML, CSS, JavaScript, and Java.

## Deployment

**Start with [DEPLOYMENT.md](DEPLOYMENT.md).** Includes Render Blueprint, Docker image, Vercel frontend config, Supabase sign-in, exact-origin CORS, persistent SQLite configuration, and an optional dedicated execution service. Render is the simplest web/API deployment; Vercel hosts the frontend with Render as its backend. The separate code runner requires a Docker-capable host.

## Courses and features

- **106 lessons:** 20 HTML, 26 CSS, 30 JavaScript, 30 Java.
- Each lesson includes concepts, an exercise, a quiz, an example solution, and official-reference links.
- **Seven projects:** three HTML/CSS projects, two JavaScript projects, and two Java projects.
- Sandboxed live HTML/CSS preview with smart paired-tag completion.
- Executable JavaScript (Node.js 22) and Java (JDK 21), with output and compiler/runtime errors.
- Per-user SQLite progress, drafts, XP, milestones, and export.
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

React, Vite, Radix Dialog, Lucide, self-hosted fonts; FastAPI, Uvicorn, SQLite; Docker-isolated code execution.

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

Open http://localhost:8000. Default `AUTH_MODE=supabase` and `RUNNER_MODE=disabled` allow browsing without credentials. Configure `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` to use sign-in; update the provider's local redirect allowlist. Variables are loaded from the process environment, not automatically from `.env`. See `.env.example` and the deployment guide.

For local execution, build `xverse-javascript:1` using the isolated `runner-build` context in the deployment guide, pull `eclipse-temurin:21-jdk`, and start the API with `RUNNER_MODE=docker`. Standalone programming runs require a signed-in user.

The runtime curriculum is already included. To regenerate after authoring changes:

```sh
python build_curriculum.py
python add_programming.py
```

Run both scripts: the first builds HTML/CSS; the second adds JavaScript, Java, course metadata, and programming projects.

## Identity and deployment security

Standalone deployments verify bearer tokens through Supabase Auth. No authentication cookies are used; exact CORS origins control cross-origin browser access. `AUTH_MODE=promptql` is an explicit compatibility option ONLY for PromptQL's trusted app proxy. Do not enable it on public standalone hosting.

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

SQLite uses `SQLITE_PATH` when set, otherwise `data/academy.sqlite`. Render stores it at `/var/data/academy.sqlite` on the mounted disk. Existing HTML/CSS lesson IDs and drafts are preserved across the rebrand. Programming source uses the existing draft `html` field with an empty `css` field for backward compatibility.

Preferences are browser-local. X Verse migrates prior color/tag preferences when available; it no longer exposes a companion preference. Project checklist checkmarks are temporary, but project code drafts persist per user.

Back up SQLite through its backup API. The source archive excludes the database, tokens, dependencies, screenshots, and test identities.

## Tests

```sh
# With the web service running:
.venv/bin/python test_api.py
.venv/bin/python test_courses.py
.venv/bin/python test_hosting.py
.venv/bin/python test_remote_runner.py
cd frontend
node test-tags.mjs
node test-ui.mjs
node test-xverse.mjs
node test-hosting.mjs
```

Legacy `test_api.py` and `test-xverse.mjs` target the trusted PromptQL-hosted test mode; do not enable that mode on public hosting just to run them. `test_hosting.py` and `test-hosting.mjs` mock Supabase rather than using real accounts. `test_remote_runner.py` needs Docker.\n\nBrowser tests require Chrome or an adjusted Playwright browser configuration. `test-xverse.mjs` writes a synthetic test identity to `qa-user.txt`; remove only that identity's records from `drafts` and `progress` after testing. API tests clean their own records. `test_courses.py` validates all 60 programming solutions independently of the HTTP rate limiter.

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
- `render.yaml`, `Dockerfile`, `deploy/start-web.py`: disk-backed web/API service.
- `vercel.json`: static frontend deployment.
- `hosting.py`: explicit auth modes and validated deployment settings.
- `runner_gateway.py`, `runner_server.py`: authenticated remote execution boundary.
- `frontend/src/api-client.js`, `account.jsx`: standalone API client and sign-in UI.
- `.env.example`, `frontend/.env.example`: safe configuration templates.
