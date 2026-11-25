# SecretSanta

Native **Android** gift-exchange app plus a **FastAPI** backend. People create a group, share an invite link, add wishlists, then run a private random draw so everyone gives exactly one gift and nobody draws themselves.

Christmas 2026 is the first launch window. The same flows work for birthdays, offices, families, New Year and custom events.

## What you get

- Email/password accounts, email verification, password reset, Google sign-in hook
- Group wizard, invite links, WhatsApp/system share from Android
- Private wishlists (only you and your assigned giver)
- Cryptographically shuffled derangement, plus constrained matching with exclusions
- Privacy modes: Secret Santa (default), organizer-visible, public
- In-app + email assignment notices
- Gift tracking and a reveal-night screen
- Docker Compose, Alembic, OpenAPI at `/docs`, automated tests

The original product brief also described a Next.js website and AdSense. This repository ships the **Android client** and the **API it needs**. Ads belong on public web content, not next to assignments; the Android app does not show ads on private screens.

## Architecture

```
android/     Kotlin + Jetpack Compose (Material 3)
backend/    FastAPI + SQLAlchemy + PostgreSQL
```

Assignments are written in a single database transaction. The public API never returns the full mapping in Secret Santa mode — authorization is enforced on the server.

## Run it online

The FastAPI server now also serves a browser app at `/`.

**Quick public demo (this machine):** start the API, then open a Cloudflare tunnel.

```bash
cd backend
export DATABASE_URL=sqlite:///./secretsanta.db
export SECRET_KEY=change-me
export APP_ENV=development
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
# in another terminal
cloudflared tunnel --url http://127.0.0.1:8001
```

That prints a `https://….trycloudflare.com` link anyone can open. The tunnel dies when you stop `cloudflared` or the laptop sleeps.

**Lasting host:** put `backend/` on Render, Fly.io or Railway with Postgres, set `SECRET_KEY`, `DATABASE_URL`, `FRONTEND_URL` and `API_PUBLIC_URL` to the public HTTPS origin, then point the Android `API_BASE_URL` at the same origin.

## Local backend

```bash
cp .env.example .env
docker compose up db redis -d   # optional; SQLite also works for a quick try

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./secretsanta.db
export SECRET_KEY=dev-only-change-me
export APP_ENV=development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

With Postgres:

```bash
docker compose up --build
```

Run migrations against Postgres:

```bash
cd backend
alembic upgrade head
```

Tests:

```bash
cd backend
.venv/bin/python -m pytest -q
```

## Android app

Open `android/` in Android Studio (Ladybug / API 35). Let it install the Gradle wrapper and SDK, then run the `app` configuration on an emulator.

The debug build talks to `http://10.0.2.2:8000/` (the emulator’s alias for your computer’s localhost). Start the API first.

On a physical phone, set `API_BASE_URL` in `android/app/build.gradle.kts` to your computer’s LAN address, for example `http://192.168.1.12:8000/`, and keep the phone on the same Wi-Fi.

### App screens

| Screen | Route |
| --- | --- |
| Sign in / register / reset | welcome, register, forgot |
| Dashboard | home |
| Create group wizard | create |
| Join by invite | join/{code} |
| Group, people, wishlist, assignment, gifts, reveal | group/{id}/… |
| Notifications, profile, legal | notifications, profile, privacy, terms, contact |

Deep links: `https://secretsanta.app/join/{inviteCode}`

## Assignment rules

- At least two joined participants
- Every giver gets exactly one recipient, every recipient exactly one giver
- No self-assignment
- Exclusions (couples, family, personal blocks) use randomized backtracking
- If no complete matching exists, the API returns the conflicting constraints and writes nothing
- A second draw is blocked until the organizer resets

## Privacy modes

- **secret** (default): only `GET /api/groups/{id}/assignments/me` is allowed
- **organizer**: the organizer can list the mapping; participants still only see their own recipient
- **public**: members can list the mapping

## Monetization note

Google AdSense is a **web** product. This Android app is not an AdSense surface. If you add a marketing site later, keep ads off assignment, confirmation and checkout-style screens. Mobile ads, if any, would use AdMob and the same placement rules.

## Deploy (keep it online)

The website and API are the same FastAPI app in `backend/`. Deploy that. Then point the Android app at the HTTPS URL.

### Option A — Render (easiest)

1. Push this repo to GitHub.
2. Open [https://dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
3. **New** → **Blueprint** → select this repository (`render.yaml` is already in the repo).
   Or create a **Web Service** manually:
   - Runtime: Docker
   - Dockerfile path: `Dockerfile` (repo root — Render’s build context is the whole repo)
   - If you instead use `backend/Dockerfile`, set the Docker context / Root Directory to `backend`
   - Add a **Postgres** database and copy its Internal Database URL into `DATABASE_URL`.
4. Set environment variables:

   | Key | Value |
   | --- | --- |
   | `APP_ENV` | `production` |
   | `SECRET_KEY` | a long random string |
   | `DATABASE_URL` | Render Postgres URL (the `postgres://` form is fine) |
   | `CORS_ORIGINS` | `*` |
   | `FRONTEND_URL` | `https://YOUR-SERVICE.onrender.com` |
   | `API_PUBLIC_URL` | same as `FRONTEND_URL` |

5. After the first deploy, open `https://YOUR-SERVICE.onrender.com/health`. You should see `{"status":"ok","service":"secretsanta"}`.
6. Use the site at that URL. Invite links will look like `https://YOUR-SERVICE.onrender.com/join/...`.

Free Render web services sleep after idle time. The first request after sleep can take ~30–60 seconds.

### Option B — Docker on a VPS (DigitalOcean, AWS, Hetzner)

```bash
cp .env.example .env
# edit SECRET_KEY, FRONTEND_URL, API_PUBLIC_URL, DATABASE_URL
docker compose up --build -d
```

Put HTTPS in front with Caddy or Cloudflare. Point `FRONTEND_URL` and `API_PUBLIC_URL` at `https://your-domain.com`.

### Option C — temporary public URL from this laptop

```bash
cd backend
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
cloudflared tunnel --url http://127.0.0.1:8001
```

That link dies when the laptop sleeps.

### Android production build

In `android/app/build.gradle.kts`, set the release URL (trailing slash required):

```kotlin
buildConfigField("String", "API_BASE_URL", "\"https://YOUR-SERVICE.onrender.com/\"")
```

Then in Android Studio: **Build → Generate Signed App Bundle** and upload the `.aab` to Google Play.

### After deploy checklist

- Change `SECRET_KEY`.
- Add `SMTP_*` if you want real assignment emails.
- Add `GOOGLE_CLIENT_ID` before turning on Google sign-in.
- Do not commit `.env`.
# christmas
