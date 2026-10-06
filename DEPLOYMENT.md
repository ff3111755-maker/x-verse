# Deploy X Verse — browser-saving edition

**Simplest setup: Render → New → Web Service → Docker → Free.** No Blueprint, persistent disk, Supabase project, Redis, Postgres, or login is required for progress and draft saving.

This package defaults to `STORAGE_MODE=browser`: each learner's progress and code live in **IndexedDB in their browser**, not Render's filesystem. Render can restart without deleting those browser records.

Hosting providers may still require account verification or change their free-tier conditions. This configuration does not select a paid instance or disk; it cannot bypass a provider's payment-verification policy.

## 1. Put the updated source on GitHub

Extract `x-verse-browser-storage.zip`. Put the **contents of its `x-verse` folder** at your repository root:

```text
Dockerfile
render.yaml
vercel.json
server.py
hosting.py
frontend/
data/
deploy/
...
```

Replace the old deployment files as well as the frontend code. Never commit real `.env` files, tokens, or learner databases.

## 2. Render Free, manually — no Blueprint

1. Choose **New → Web Service** and connect the repository.
2. Select **Docker** as the runtime.
3. Set Dockerfile path to `./Dockerfile`, with the repository root as the build context. If your files are nested, use that folder as the Root Directory.
4. Choose the **Free** instance type.
5. **Do not add a persistent disk.**
6. Set these environment variables:
   ```text
   STORAGE_MODE=browser
   RUNNER_MODE=disabled
   ```
   Both are defaults in the new package; setting them explicitly makes the intended setup clear.
7. Leave `ALLOWED_ORIGINS` empty when the frontend and API are on the same Render origin.
8. Do not override the Docker start command. Set health check path to `/readyz`.
9. Deploy and open the Render URL.

If moving an existing service from the old package, remove obsolete `SUPABASE_URL`/`SUPABASE_PUBLISHABLE_KEY` variables if you no longer use account mode. Incomplete/invalid leftover credentials can still cause startup configuration errors. Do not set `AUTH_MODE=promptql` on public hosting.

**Already created a paid service/disk?** Updating code does not cancel or downgrade it. Review those resources in Render. Export learner records before removing an old disk. Starting a separate Free Web Service is the clearest way to avoid inheriting a paid setup; do not delete the old data until any migration has been verified.

### Optional Blueprint

The updated `render.yaml` also selects **Free**, browser storage, no disk, and no required Supabase keys. You may use it instead, but manual deployment is supported and easier to review.

### What works without a paid runner

- All 106 lesson pages and seven project briefs.
- HTML/CSS editor, live preview, exercise checks, quizzes, and completion.
- Java/JavaScript source editing, automatic draft saving, and source download.
- Local progress, XP, milestones, JSON export/import.
- Color presets, hologram, and smart HTML tag pairs.

**Java/JavaScript execution, executable checks, and their completion still require a protected code runner.** Browser storage does not provide a Java runtime. The free deployment tells learners that execution is unavailable instead of showing fabricated output or opening an unrestricted public runner.

Render Free may sleep when idle and take time to wake. X Verse is **not a fully offline app**: loading the curriculum and checking/completing exercises still use the API. Already-loaded HTML/CSS preview and local saving are browser-side.

## 3. Vercel frontend + Render Free API

1. Deploy the Render service above.
2. Import the same repository into Vercel. Keep Root Directory at the repository root.
3. The included `vercel.json` configures:
   - Install: `npm --prefix frontend ci`
   - Build: `npm --prefix frontend run build`
   - Output: `frontend/dist`
   - Node: 22.x via root `package.json`.
4. Set this **Vercel build environment variable**:
   ```text
   VITE_API_BASE_URL=https://YOUR_SERVICE.onrender.com
   ```
   Use the API origin only, without `/api`.
5. Deploy. On **Render**, set:
   ```text
   ALLOWED_ORIGINS=https://YOUR_APP.vercel.app
   ```
   Restart/redeploy Render after changing it.
6. Add your exact custom-domain origin if needed. Multiple allowed origins are comma-separated; do not use `*`.

No Supabase redirects or keys are needed in browser mode. Changing `VITE_API_BASE_URL` requires rebuilding Vercel.

**Vercel alone is not supported by this package:** its curriculum and exercise-check API still runs on Render or another Python host.

## 4. Browser storage and backups

Open **Preferences & backups** using the palette icon, or **Backups & storage** in the banner.

- Drafts save automatically as you edit. Wait for **Saved in this browser** before closing the page.
- **Export backup** downloads a versioned JSON file containing completed lessons and all saved lesson, project, and playground drafts. It flushes active editors first.
- **Import backup** reads a JSON file, validates its structure, and shows the number of lessons/drafts before any data is changed.
- **Merge backup** keeps existing completions. For matching drafts, the newer timestamp wins. Import is transactional: invalid input is rejected, not partially applied.
- Export before importing if you want a recovery copy of both versions.
- **Ask browser to protect saved data** requests persistent browser storage when supported. The browser can decline; it does not stop a person clearing site data.
- Backups contain source code. Store them privately if your drafts contain anything sensitive. They do not contain account tokens.

### Limits to understand

- One learning profile per browser profile and website origin. People sharing that browser profile share these records; there is no account isolation in browser mode.
- No automatic cross-device or cross-browser sync.
- A Render domain, a Vercel domain, and a custom domain each have separate storage. **Export on the old URL and import on the new URL.**
- Clearing site data, private/incognito sessions, storage eviction, browser/profile removal, or device loss can erase records.
- Appearance preferences and temporary project-review checkboxes are not in the learning backup.
- Import supports version 1 backups and the previous X Verse account-export JSON format. Imported progress is a personal learning record, not a tamper-proof certificate.
- If storage is blocked/full, the UI reports a failure rather than claiming a successful save. Export/download what you can and fix the storage setting before continuing.
- Multiple tabs share storage; refresh an inactive tab to see progress changed elsewhere. Avoid editing the same document in two tabs simultaneously.

## 5. Existing data

This source archive contains **no learner data**.

The PromptQL-hosted app keeps its previous server database intact. In its backup panel, **Import my previously saved account data** loads only the currently authorized visitor's account export, shows a preview, and asks for merge confirmation. It does not delete the original records.

For an older standalone account-mode deployment, export while that version is still available, then import the downloaded JSON on the new browser-saving version. If old ephemeral SQLite data has already disappeared, browser storage cannot recover it.

Browser saving does not copy the whole project's records to a device or link unrelated identities.

## 6. Optional account mode and protected execution

The previous server mode remains available for an operator who deliberately wants account-based saving:
```text
STORAGE_MODE=server
AUTH_MODE=supabase
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_YOUR_PUBLIC_KEY
SQLITE_PATH=/var/data/academy.sqlite
```
That mode uses Supabase Auth and SQLite on a **persistent disk**, not Supabase's database. It is not the no-disk free recipe. Supabase email/provider/redirect settings are required; use only a publishable or legacy anon key, never a service-role key.

A separate runner can be connected in authenticated account mode. See [RUNNER.md](RUNNER.md). Public browser mode deliberately does not remove the runner's authentication requirement; simply setting `RUNNER_MODE=remote` will not turn this into an anonymous public compiler. The PromptQL-hosted version can retain execution through its trusted identity boundary.

Do not expose Docker sockets or execute submitted code directly in the API process.

## Verification

- `/readyz` returns HTTP 204.
- `/api/config` reports `storage_mode: "browser"`.
- Open a fresh browser with no login, edit a draft, wait for Saved, refresh, and reopen it.
- Complete an HTML lesson and verify its progress after refresh.
- Export, import in a different browser profile, confirm the merge, and check progress/drafts.
- Test on mobile and after a Render restart.
- A second clean browser should start empty until a backup is imported.

The package has local browser tests, backend tests, and Docker deployment tests. It has **not been deployed to your hosting account**. Provider-specific verification, billing, and availability remain outside the app.

## References

- Render Free: https://render.com/docs/free
- Render Docker: https://render.com/docs/docker
- Vite on Vercel: https://vercel.com/docs/frameworks/frontend/vite
- IndexedDB: https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API