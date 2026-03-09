# External Integrations

**Analysis Date:** 2026-03-09

## APIs & External Services

No third-party external APIs or SaaS services are used. All application functionality is self-contained.

## Data Storage

**Databases:**
- PostgreSQL 16
  - Connection: `DATABASE_URL` env var (backend reads via `os.getenv` in `backend/database.py`)
  - Default fallback: `postgresql://fasting_coach:***@postgresql.host:5432/fasting_db`
  - Client/ORM: SQLAlchemy 2.0 (`backend/database.py`, `backend/models.py`)
  - Driver: psycopg2-binary 2.9.9
  - Local dev: postgres:16-alpine Docker container (`docker-compose.yml`, service `db`)
  - Production: External hosted PostgreSQL at `postgresql.host` (`docker-compose.dokploy.yml`)

**File Storage:**
- None. No file uploads or object storage integrations.

**Caching:**
- Service worker cache (PWA) via `vite-plugin-pwa` / Workbox
  - API responses cached under key `api-cache`, NetworkFirst strategy, 5s timeout, 1-day expiry
  - Static assets cached with 1-year expiry via `frontend/nginx.conf`
- No server-side cache (no Redis, Memcached, etc.)

## Authentication & Identity

**Auth Provider:**
- None. The application has no authentication layer — all endpoints are publicly accessible.
- CORS is the only access restriction: `http://localhost:5173` and `https://openclaw.host` are the allowed origins (configured in `backend/main.py`).

## Monitoring & Observability

**Error Tracking:**
- None. No Sentry, Datadog, or similar integrations.

**Logs:**
- uvicorn access/error logs (stdout, default uvicorn behavior)
- No structured logging library configured

## CI/CD & Deployment

**Hosting:**
- Dokploy platform (`docker-compose.dokploy.yml` is the production compose file)
- Frontend container: nginx:alpine on port 80, mapped to host port 3099
- Backend container: uvicorn on port 8042

**CI Pipeline:**
- None detected. No GitHub Actions, GitLab CI, or similar config files present.

## Environment Configuration

**Required env vars (production):**
- `DATABASE_URL` - Full PostgreSQL connection string (e.g. `postgresql://user:pass@host:5432/db`)

**Build-time args (frontend Docker build):**
- `VITE_API_URL` - Set to empty string `""` in both compose files, causing the frontend to use relative `/api/` paths (proxied by nginx to the backend container)

**Secrets location:**
- `.env` file existence not detected in repository
- Production secrets managed via Dokploy environment configuration (injected as `${DATABASE_URL}` in `docker-compose.dokploy.yml`)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Internal API Communication

**Frontend → Backend:**
- All requests go to `/api/*` endpoints
- In development: `frontend/src/api/client.ts` prefixes `http://localhost:8042`
- In production (Docker): relative paths, proxied by nginx (`frontend/nginx.conf`, `location /api/` → `backend:8042`)
- HTTP client: native `fetch` API (no axios or other library)
- All calls defined in `frontend/src/api/client.ts`

---

*Integration audit: 2026-03-09*
