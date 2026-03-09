# Fasting Tracker

## What This Is

A personal fasting tracker web application with a FastAPI backend and Vue 3 frontend. It tracks intermittent and extended fasts (16:8 through 72h), logs daily wellness metrics, records meals, and tracks weight over time. The UI is French-language, mobile-first, and PWA-capable with offline fallback.

## Core Value

A live, always-accurate dashboard that shows the current fast's progress with phase indicators and elapsed time — so the user can glance at their phone and know exactly where they are in a fast.

## Requirements

### Validated

- ✓ FastAPI backend with full CRUD for fasts, daily logs, meals, weight, and stats — existing
- ✓ Vue 3 frontend with 7 views: Dashboard, StartFast, FastDetail, History, Stats, Weight, Meals — existing
- ✓ Live circular progress timer with fasting phase indicators on Dashboard — existing
- ✓ Daily log form (water, electrolytes, energy, hunger, mood, notes) — existing
- ✓ Weight history chart with trend data — existing
- ✓ Meal logging with meal recommendations — existing
- ✓ Dark mode support — existing
- ✓ PWA manifest + service worker — existing
- ✓ Offline fallback (localStorage active fast cache) — existing
- ✓ Docker Compose deployment (Dokploy) — existing
- ✓ Bottom navigation bar (mobile) — existing

### Active

- [ ] Guard against starting a second fast when one is already active
- [ ] Error handling in FastDetail (endFast, submitLog, confirmDeleteFast lack catch blocks)
- [ ] Weight entry edit/delete in UI and backend endpoints
- [ ] Pagination on History view (currently hard-caps at 100 fasts)
- [ ] Fix `avg_duration_hours` always returning None in weekly stats
- [ ] Fix N+1 query pattern in `get_weekly_summary` (up to 32 DB round-trips)
- [ ] Add test coverage for core fast lifecycle (CRUD endpoints)
- [ ] Remove hardcoded DB credentials from `database.py` (security)
- [ ] Fix `useTimer` composable lifecycle issue (called after async await in onMounted)

### Out of Scope

- Authentication / multi-user support — single-user personal app, network-level protection sufficient
- Real-time sync across devices — not needed for single-user use case
- Native mobile app — PWA handles mobile use case

## Context

- PostgreSQL database at `postgresql.host:5432` with existing live data (1+ active fast, must not drop/recreate tables)
- Backend runs on port 8042, frontend dev server on port 5173
- Production: Docker + Dokploy, nginx serves frontend on port 3099, proxies `/api/` to backend
- All UI text in French
- Existing codebase issues documented in `.planning/codebase/CONCERNS.md`

## Constraints

- **Schema:** Do NOT drop or recreate database tables — use existing schema as-is
- **Stack:** FastAPI + SQLAlchemy + Pydantic (backend), Vue 3 + TypeScript + Tailwind v4 (frontend)
- **Language:** French for all UI labels and text
- **Ports:** Backend 8042, Frontend 5173

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| No authentication layer | Single-user personal app; network controls sufficient | — Pending |
| PWA over native app | Mobile-first web covers the use case without app store overhead | ✓ Good |
| No Pinia/Vuex | State local to each view; active fast in localStorage for offline | — Pending |
| Tailwind v4 (CSS-native) | Latest version; no `tailwind.config.js` needed | ✓ Good |

---
*Last updated: 2026-03-09 after initialization*
