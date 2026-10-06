# Deploy X Verse

## Choose a setup

| Setup | Frontend | API + saved data | Java/JavaScript execution |
|---|---|---|---|
| **Render — simplest** | Render web service | Same service + persistent disk | Optional separate runner |
| **Vercel + Render** | Vercel | Render web service + persistent disk | Optional separate runner |

**Vercel alone does not host this version's persistent SQLite database or isolated Docker runner.** Ordinary Render web services also do not provide the Docker daemon needed to launch per-user execution containers. The included web image deliberately does not execute learner code directly.

Without a runner, the website, all 106 lessons, 7 project briefs, sign-in, saved drafts, HTML/CSS preview/checks, quizzes, and HTML/CSS completion work. Java/JavaScript Run, executable checks, and lesson completion require the separate runner. The UI explains this rather than showing fake output.

Render's persistent disk requires a paid disk-compatible service. Hosting, authentication email, and the optional runner may incur costs. Check current provider pricing before creating services.

## 1. Put the code on GitHub

Unzip the source archive. Open the inner `x-verse` folder: `render.yaml`, `vercel.json`, `Dockerfile`, and `frontend/` must be at the repository root, not inside an extra nested folder.

Create a repository and upload the source. The included `.gitignore` excludes databases, credentials, dependencies, and local builds. Never commit real `.env` files.

## 2. Create Supabase authentication

1. Create your own project at https://supabase.com/dashboard.
2. In Authentication, enable **Email** sign-in and keep email confirmation enabled.
3. Copy the **Project URL** and **publishable key** from the project's API settings. A legacy `anon` key also works.
4. Do **not** use a secret key or `service_role` key. The public publishable key is intentionally served to the frontend; privileged keys are rejected.
5. Configure production SMTP for reliable confirmation and sign-in emails. Supabase's default email service has restrictions and is not a production mail setup.
6. Once you know your deployment address, set:
   - **Site URL** to the public frontend's HTTPS origin.
   - **Redirect URLs** to the same exact origin, for example `https://your-app.vercel.app` or `https://your-app.onrender.com`.
   - Add custom domains explicitly when you switch domains.

X Verse uses email/password sign-up and sign-in, with an email-link option for existing accounts. Sign-up passwords must have at least 12 characters. The backend verifies access tokens with Supabase Auth on each protected request.

No Supabase database tables or RLS migrations are needed: only **Auth** is used. Progress and drafts live in SQLite on Render's disk.

## 3A. Deploy everything except the runner on Render

1. In Render, choose **New → Blueprint** and connect the repository.
2. Render reads `render.yaml`. Review the paid `starter` service and 1 GB disk before approving.
3. Supply:
   - `SUPABASE_URL` — your Supabase project URL.
   - `SUPABASE_PUBLISHABLE_KEY` — its publishable or legacy anon key.
4. Leave these provided values:
   - `AUTH_MODE=supabase`
   - `RUNNER_MODE=disabled` until a separate runner is ready.
   - `SQLITE_PATH=/var/data/academy.sqlite`
   - `ALLOWED_ORIGINS` empty when Render serves the frontend and API at the same origin.
5. Deploy. Render builds the Dockerfile; the server listens on Render's `PORT`.
6. Set the Render URL in Supabase's Site URL/Redirect URLs, then open the app.
7. Select **Sign in** or the appearance/settings button to create an account.

Manual alternative: create a Docker Web Service, use repository root as build context and `./Dockerfile`, add a persistent disk mounted at `/var/data`, enter the same environment variables, and set health check `/readyz`. Do not override the image's start command.

The container fixes the disk directory ownership on startup and drops to an unprivileged application user. It runs one API worker. Keep one instance with this SQLite architecture; horizontal scaling needs a shared database redesign.

## 3B. Use Vercel for the frontend

First deploy the Render backend using section 3A; its bundled frontend can remain available.

1. Import the same GitHub repository into Vercel.
2. Set **Root Directory** to the repository root. `vercel.json` supplies:
   - Install: `npm --prefix frontend ci`
   - Build: `npm --prefix frontend run build`
   - Output: `frontend/dist`
   - Node.js: 22.x (root `package.json`).
3. Add a **Vercel environment variable**:
   ```text
   VITE_API_BASE_URL=https://YOUR_RENDER_SERVICE.onrender.com
   ```
   Use the HTTPS backend origin only, with no `/api` suffix or trailing slash.
4. Deploy. Copy the resulting Vercel frontend origin.
5. On the **Render backend**, set:
   ```text
   ALLOWED_ORIGINS=https://YOUR_APP.vercel.app
   ```
   Redeploy/restart the Render service after changing its environment.
6. Set Supabase's Site URL and Redirect URLs to the Vercel frontend origin.
7. Open Vercel, sign in, and test a saved draft.

Environment values beginning with `VITE_` are baked into the frontend and are public. **Never put runner credentials or Supabase secret/service-role keys in Vercel's frontend variables.** Supabase's public URL/key are read from the backend config.

Changing `VITE_API_BASE_URL` requires a Vercel rebuild. CORS allows exact origins only: for a custom domain, add that origin to `ALLOWED_ORIGINS` and Supabase redirects. Multiple allowed origins are comma-separated. Vercel preview domains do not inherit production access automatically; add only previews you trust, and preferably use separate preview authentication/data.

## 4. Optional: enable Java and JavaScript execution

This needs a **separate Linux host with Docker Engine**, such as a dedicated VPS. Neither the Render web image nor Vercel is the runner. The current PromptQL VM is not used as an external deployment dependency.

### Prepare the host

Install a supported Docker Engine, Python 3.12+, uv, and Caddy. Configure Docker to start on boot. On the dedicated host, copy these files into `/opt/xverse`:

- `runner_server.py`
- `code_runner.py`
- `requirements.txt`
- `Dockerfile.javascript`
- `javascript-runner.mjs`
- `deploy/runner.service`
- `deploy/Caddyfile.example`

Then, as a host administrator:

```sh
sudo useradd --system --create-home --user-group xverse-runner
sudo usermod -aG docker xverse-runner
cd /opt/xverse

uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
mkdir -p runner-build
cp Dockerfile.javascript javascript-runner.mjs runner-build/
sudo docker build -f runner-build/Dockerfile.javascript -t xverse-javascript:1 runner-build
sudo docker pull eclipse-temurin:21-jdk

# Generates a new secret on YOUR machine; keep it private.
sudo python3 - <<'PY'
import secrets, os
path = "/etc/xverse-runner.env"
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    f.write("RUNNER_API_KEY=" + secrets.token_urlsafe(48) + "\n")
PY

sudo install -m 644 deploy/runner.service /etc/systemd/system/xverse-runner.service
sudo systemctl daemon-reload
sudo systemctl enable --now xverse-runner.service
```

Ensure the `xverse-runner` user can read and execute `/opt/xverse/.venv` and the runner source, and that the source directory is not writable by untrusted users. The virtualenv must be installed at its final path.

### Put TLS in front

1. Point a domain such as `runner.yourdomain.com` at the dedicated host.
2. Adapt `deploy/Caddyfile.example` with your real domain and install it as the host's Caddy config.
3. Open only the required HTTPS/ACME ports (443/80) and restricted SSH.
4. Keep port 9000 bound to loopback. Do not expose the Docker socket.
5. The runner's `/readyz` and `/v1/run` both require the Bearer key.

On the **Render backend**, configure:

```text
RUNNER_MODE=remote
RUNNER_URL=https://runner.yourdomain.com
RUNNER_API_KEY=<same secret from /etc/xverse-runner.env>
```

`RUNNER_URL` has no `/v1/run` suffix. Restart/redeploy Render. These variables belong only on backend/runner services, never in the frontend. Java and JavaScript should now execute.

### Security and limits

The runner launches fresh non-root, networkless containers with no host mounts, read-only root filesystems, dropped capabilities, two concurrent runs, 384 MB RAM, 0.75 CPU, 64 PIDs, 15 seconds, and 32 KB output per run. The API allows 20 execution requests/minute per signed-in account.

Docker access is effectively host-root privilege. Use a dedicated host with no unrelated credentials or workloads, keep it patched, enforce infrastructure spending/rate limits, and monitor it. These containers share the host kernel and are not a guarantee against all sandbox escapes. An open, high-volume public coding service warrants an independently reviewed execution tier. Keep a single runner/API worker unless you implement shared quotas.

## 5. Verify after deployment

- `/readyz` returns HTTP 204.
- `/api/config` reports `auth_mode: "supabase"` and never contains runner secrets.
- Create an account, confirm its email, sign in, edit a draft, then refresh.
- Sign in using another account: the first account's drafts must not appear.
- Complete an HTML lesson and check that XP persists.
- With the optional runner: run `console.log("Hello")` and the first Java example; test a syntax error too.
- Restart/redeploy the Render service and confirm saved data remains.
- Check mobile layout and custom-domain redirects.

This package was tested locally using its actual Docker image, SQLite restart persistence, verified-auth logic with a mocked Supabase service, frontend sign-in flows with mocks, CORS checks, and a loopback authenticated runner. **It has not been deployed into your Vercel/Render account or tested with your live Supabase project.**

## Backups and migration

Use SQLite's backup API or an appropriate Render disk backup process. Do not casually copy a live database without its WAL handling. The source archive contains **no learner database or personal data**.

Your new deployment starts empty. PromptQL user IDs and Supabase user IDs are different, so records do not automatically map across systems. Use the app's export for a personal archive; importing/linking those records requires an explicit migration, not blindly relabeling users.

## Troubleshooting

- **Website opens but lessons fail to load:** check `VITE_API_BASE_URL`, HTTPS, and the Render service's health.
- **CORS error:** add the exact frontend origin to Render `ALLOWED_ORIGINS`, then restart Render. Do not use `*`.
- **Account creation email missing:** check Supabase Email provider settings, SMTP, spam, rate limits, and redirect allowlist.
- **No saved progress after redeploy:** verify disk mount `/var/data` and `SQLITE_PATH`; do not rely on the container's temporary filesystem.
- **Java/JS unavailable:** `RUNNER_MODE=disabled` is intentional until a runner is configured. Check runner TLS/domain/key/service logs if `remote`.
- **Container busy:** wait for active runs; do not remove isolation/resource limits to work around load.
- **Do not set `AUTH_MODE=promptql` on Vercel/Render.** It trusts a platform-injected header and is only safe behind PromptQL's trusted app proxy.
- **API says configuration invalid:** use a publishable/anon Supabase key, exact HTTPS origins, and a random runner key of at least 32 characters.

## Official references

- Render Blueprint: https://render.com/docs/infrastructure-as-code
- Render Docker services: https://render.com/docs/docker
- Render persistent disks: https://render.com/docs/disks
- Vite on Vercel: https://vercel.com/docs/frameworks/frontend/vite
- Supabase Auth: https://supabase.com/docs/guides/auth