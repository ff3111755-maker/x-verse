# Optional protected execution service

For the account-based `STORAGE_MODE=server` deployment with verified Supabase sign-in. It is NOT required for browser saving. Default browser mode does not offer unauthenticated execution; do not bypass the identity check to enable a public compiler.

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

