# Technology Stack

**Analysis Date:** 2026-03-09

## Languages

**Primary:**
- Python 3.12 (Docker image) / 3.13 (host) - Backend API
- TypeScript 5.9.3 - Frontend application

**Secondary:**
- HTML/CSS - Frontend markup and styling

## Runtime

**Backend Environment:**
- Python 3.12-slim (Docker container via `backend/Dockerfile`)
- Runs as ASGI app via uvicorn

**Frontend Environment:**
- Node.js 22 (Docker build stage via `frontend/Dockerfile`)
- Served at runtime by nginx:alpine (Docker container)

**Package Manager:**
- Backend: pip (no lockfile — `backend/requirements.txt` only)
- Frontend: npm (lockfileVersion 3, `frontend/package-lock.json` present)

## Frameworks

**Core (Backend):**
- FastAPI 0.115.0 - REST API framework with automatic OpenAPI docs
- SQLAlchemy 2.0.35 - ORM for database access (declarative_base pattern)
- Pydantic 2.9.2 - Request/response schema validation (bundled with FastAPI)

**Core (Frontend):**
- Vue.js 3.5.25 - Reactive UI framework (Composition API)
- Vue Router 4.6.4 - SPA client-side routing
- Chart.js 4.5.1 - Canvas-based charting library
- vue-chartjs 5.3.3 - Vue wrapper for Chart.js

**Testing:**
- pytest 8.3.3 - Backend test runner
- httpx 0.27.2 - Async HTTP client used as FastAPI test client

**Build/Dev:**
- Vite 7.3.1 - Frontend build tool and dev server
- vue-tsc 3.1.5 - TypeScript type-checking for .vue files
- @vitejs/plugin-vue 6.0.2 - Vue SFC support in Vite
- @tailwindcss/vite 4.1.18 - Tailwind CSS Vite plugin (v4 integration)
- vite-plugin-pwa 1.2.0 - Progressive Web App manifest + service worker generation

## Key Dependencies

**Critical (Backend):**
- `psycopg2-binary` 2.9.9 - PostgreSQL driver (binary, no system lib required)
- `uvicorn[standard]` 0.30.6 - ASGI server with websocket/http2 extras

**Critical (Frontend):**
- `tailwindcss` 4.1.18 - Utility-first CSS framework (v4 — CSS-native config)
- `chart.js` 4.5.1 - Powers all data visualization components
- `vue-chartjs` 5.3.3 - Reactive chart components (`WeightChart.vue`)

**Infrastructure:**
- `sqlalchemy.dialects.postgresql.JSONB` - Used for `macros` column in `meal_recommendations` table
- `sqlalchemy.ARRAY(Text)` - Used for `ingredients` columns in `meals` and `meal_recommendations`

## Configuration

**Environment:**
- Backend reads `DATABASE_URL` env var; falls back to hardcoded `postgresql://fasting_coach:***@postgresql.host:5432/fasting_db`
- Frontend reads `VITE_API_URL` build arg (Docker build arg); defaults to `/api` in production, empty string in dev (relies on `import.meta.env.PROD` check in `frontend/src/api/client.ts`)
- Production env passed via `DATABASE_URL=${DATABASE_URL}` in `docker-compose.dokploy.yml`

**Build:**
- `frontend/vite.config.ts` - Vite config: plugins, PWA manifest, server settings
- `frontend/tsconfig.app.json` - TypeScript strict mode, targets `src/**`
- `frontend/tsconfig.node.json` - TypeScript config for Vite config file itself
- `backend/Dockerfile` - Python 3.12-slim, exposes 8042
- `frontend/Dockerfile` - Multi-stage: Node 22 build → nginx:alpine serve
- `frontend/nginx.conf` - SPA fallback + `/api/` proxy to `backend:8042`

## Platform Requirements

**Development:**
- Python 3.12+ with pip
- Node.js 22 with npm
- PostgreSQL 16 (or Docker)
- Backend runs on port 8042, frontend dev server on port 5173

**Production:**
- Docker + Docker Compose
- Two compose configs: `docker-compose.yml` (full stack with local postgres) and `docker-compose.dokploy.yml` (external DB, Dokploy platform deployment)
- Frontend served by nginx on port 80 (mapped to host 3099)
- Backend served by uvicorn on port 8042

---

*Stack analysis: 2026-03-09*
