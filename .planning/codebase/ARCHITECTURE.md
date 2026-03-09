# Architecture

**Analysis Date:** 2026-03-09

## Pattern Overview

**Overall:** Client-server SPA with REST API

**Key Characteristics:**
- Decoupled frontend (Vue 3 SPA) and backend (FastAPI) communicating over HTTP REST
- Backend follows a layered architecture: routes → crud → models → database
- Frontend follows a composables pattern: views call API client and composables for logic
- PWA-capable frontend with offline fallback via localStorage

## Layers

**HTTP/Route Layer (Backend):**
- Purpose: Accept HTTP requests, validate input, delegate to CRUD, return responses
- Location: `backend/main.py`
- Contains: FastAPI route handlers, HTTP exception handling, CORS middleware
- Depends on: `crud.py`, `schemas.py`, `database.py`
- Used by: Frontend API client over HTTP

**Schema/Validation Layer (Backend):**
- Purpose: Define request/response shapes and validate input
- Location: `backend/schemas.py`
- Contains: Pydantic `BaseModel` classes for Create, Update, and Response variants of each entity
- Depends on: Nothing (pure Pydantic)
- Used by: Route handlers in `main.py`, CRUD functions in `crud.py`

**CRUD Layer (Backend):**
- Purpose: All database read/write operations
- Location: `backend/crud.py`
- Contains: Functions that accept a SQLAlchemy `Session` and model/schema objects
- Depends on: `models.py`, `schemas.py`
- Used by: Route handlers in `main.py`

**ORM Model Layer (Backend):**
- Purpose: Define database table mappings
- Location: `backend/models.py`
- Contains: SQLAlchemy `Base` subclasses for `Fast`, `DailyLog`, `Meal`, `MealRecommendation`, `WeightLog`
- Depends on: `database.py` (for `Base`)
- Used by: `crud.py` for queries

**Database Connection Layer (Backend):**
- Purpose: Manage database engine and session lifecycle
- Location: `backend/database.py`
- Contains: SQLAlchemy engine, `SessionLocal`, `Base`, `get_db()` dependency
- Depends on: `DATABASE_URL` env var (falls back to hardcoded default)
- Used by: `main.py` (for `engine`, `Base`), route handlers (for `get_db` dependency injection)

**API Client Layer (Frontend):**
- Purpose: Single point of communication with backend
- Location: `frontend/src/api/client.ts`
- Contains: Typed fetch wrapper `request<T>()`, one exported function per API endpoint
- Depends on: `frontend/src/types/index.ts`
- Used by: All view components and composables

**Types Layer (Frontend):**
- Purpose: Shared TypeScript interfaces mirroring backend Pydantic response schemas
- Location: `frontend/src/types/index.ts`
- Contains: `Fast`, `DailyLog`, `Meal`, `WeightEntry`, `WeightTrend`, `Stats`, `WeeklySummary`, `MealRecommendation`, `CategoryCount`
- Depends on: Nothing
- Used by: API client, views, composables, components

**Composables Layer (Frontend):**
- Purpose: Encapsulate reusable reactive logic separate from view components
- Location: `frontend/src/composables/`
- Contains:
  - `useTimer.ts` — live elapsed/remaining time computation, phase logic
  - `useBodyState.ts` — fasting phase body state descriptions
  - `useDark.ts` — dark mode toggle
  - `useOfflineStorage.ts` — localStorage persistence for active fast
  - `useOnlineStatus.ts` — network online/offline detection
  - `useMealRecommendations.ts` — meal recommendation fetching logic
- Depends on: API client, types
- Used by: View components

**View Layer (Frontend):**
- Purpose: Page-level components, each corresponding to a route
- Location: `frontend/src/views/`
- Contains: `Dashboard.vue`, `StartFast.vue`, `FastDetail.vue`, `History.vue`, `StatsView.vue`, `WeightView.vue`, `MealsView.vue`
- Depends on: API client, composables, reusable components
- Used by: Vue Router

**Component Layer (Frontend):**
- Purpose: Reusable UI building blocks
- Location: `frontend/src/components/`
- Contains: `CircularProgress.vue`, `FastCard.vue`, `PhaseIndicator.vue`, `StatCard.vue`, `WeightChart.vue`, `MoodSelector.vue`, `SliderInput.vue`, `NavBar.vue`, `BodyStateCard.vue`, `MealDetailModal.vue`, `MealRecommendationCard.vue`, `MealRecommendationsList.vue`
- Depends on: Types, composables (some)
- Used by: Views

## Data Flow

**Active Fast Display:**

1. `Dashboard.vue` mounts and calls `getCurrentFast()`, `getStats()`, `getWeightTrend()`, `getFasts()` in parallel via `frontend/src/api/client.ts`
2. API client sends `GET /api/fasts/current` to `backend/main.py`
3. Route handler calls `crud.get_current_fast(db)` in `backend/crud.py`
4. CRUD queries `models.Fast` where `ended IS NULL AND completed IS FALSE`
5. Response serialized via `FastResponse` Pydantic schema in `backend/schemas.py`
6. Dashboard stores fast in `ref<Fast>`, calls `useTimer(fast.started, fast.target_hours)` from `frontend/src/composables/useTimer.ts`
7. Timer uses `setInterval` every 1s to update `now.value`, driving computed `elapsed`, `remaining`, `progress`
8. `CircularProgress.vue` and `PhaseIndicator.vue` reactively update from timer values

**Offline Fallback:**

1. If API call fails (network error), Dashboard catches exception
2. Calls `loadActiveFast()` from `frontend/src/composables/useOfflineStorage.ts`
3. Retrieves fast from `localStorage` key `fasting_active_fast`
4. Timer continues running from cached fast data
5. Offline banner shown via `useOnlineStatus.ts` in `App.vue`

**State Management:**
- No global state store (no Pinia/Vuex)
- State is local to each view component using Vue `ref()`/`computed()`
- Active fast persisted to `localStorage` for offline use
- All other data fetched fresh on each view mount

## Key Abstractions

**Fast (Entity):**
- Purpose: Core tracking unit — a single fasting period
- Examples: `backend/models.py` (`Fast`), `backend/schemas.py` (`FastCreate`, `FastUpdate`, `FastResponse`), `frontend/src/types/index.ts` (`Fast`)
- Pattern: Model → Schema → TypeScript interface mirrors the same shape through all layers

**CRUD Functions:**
- Purpose: All DB operations isolated from route logic
- Examples: `backend/crud.py` — `get_current_fast()`, `create_fast()`, `update_fast()`
- Pattern: Each function accepts `db: Session` as first arg, model/schema objects as subsequent args; returns ORM instance or None

**Composables:**
- Purpose: Reusable reactive logic for timer, body state, offline, dark mode
- Examples: `frontend/src/composables/useTimer.ts`, `frontend/src/composables/useBodyState.ts`
- Pattern: Functions prefixed `use`, returning reactive refs/computed values

**API Client Functions:**
- Purpose: Typed wrappers for every backend endpoint
- Examples: `frontend/src/api/client.ts` — `getCurrentFast()`, `createFast()`, `updateFast()`
- Pattern: Named exports, each returning a `Promise<T>` where T is a type from `frontend/src/types/index.ts`

## Entry Points

**Backend:**
- Location: `backend/main.py`
- Triggers: `uvicorn main:app --host 0.0.0.0 --port 8042`
- Responsibilities: Creates FastAPI app, registers CORS middleware, calls `Base.metadata.create_all()`, runs `seed.run()`, defines all route handlers

**Frontend:**
- Location: `frontend/src/main.ts`
- Triggers: Vite dev server or built static assets served by Nginx
- Responsibilities: Creates Vue app, mounts router, mounts to `#app` in `frontend/index.html`

**Router:**
- Location: `frontend/src/router/index.ts`
- Triggers: Vue Router on navigation events
- Responsibilities: Maps 7 URL paths to lazy-loaded view components

**App Shell:**
- Location: `frontend/src/App.vue`
- Triggers: Always rendered as root component
- Responsibilities: Renders `<router-view>`, `<NavBar>`, offline banner

## Error Handling

**Strategy:** HTTP exceptions in backend, try/catch with offline fallback in frontend

**Patterns:**
- Backend: `raise HTTPException(status_code=404, detail="...")` for not-found entities; no global exception handler
- Backend: Pydantic validation errors automatically return 422 from FastAPI
- Frontend API client: Non-OK responses throw `new Error(\`\${status}: \${detail}\`)` in `frontend/src/api/client.ts`
- Frontend views: `try/catch` around `onMounted` data fetching; `Dashboard.vue` falls back to localStorage on any fetch failure
- No structured error boundary or toast notification system

## Cross-Cutting Concerns

**Logging:** None — no structured logging in backend or frontend
**Validation:** Pydantic models on backend; no client-side form validation library (HTML5 constraints + manual checks)
**Authentication:** None — the application has no auth layer; all endpoints are public

---

*Architecture analysis: 2026-03-09*
