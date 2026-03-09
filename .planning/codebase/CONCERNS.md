# Codebase Concerns

**Analysis Date:** 2026-03-09

## Tech Debt

**Hardcoded database credentials in source:**
- Issue: `backend/database.py` line 6-8 contains a fallback `DATABASE_URL` with a literal password (`fasting_coach:***REMOVED***@postgresql.host`) checked into the codebase
- Files: `backend/database.py`
- Impact: Any developer who clones the repo has the production database password in their local copy. It will also appear in git history indefinitely.
- Fix approach: Remove the fallback default entirely; require `DATABASE_URL` env var to be set explicitly. Raise an error at startup if missing.

**`seed.run()` called unconditionally on every startup:**
- Issue: `main.py` line 23 calls `seed.run()` synchronously on every FastAPI startup, which opens a separate DB session, queries `meal_recommendations`, and performs a full table scan before the server is ready to serve requests.
- Files: `backend/main.py`, `backend/seed.py`
- Impact: Adds latency to cold starts; the extra session is redundant since `get_db()` already manages sessions. Under high concurrency at startup, two processes could both race past the `count > 0` guard before either commits.
- Fix approach: Move seeding to a one-time migration script or use an `on_startup` FastAPI lifespan event with a proper advisory lock or a migration tool (Alembic).

**`Base.metadata.create_all()` called both in `main.py` and `seed.py`:**
- Issue: `create_all` is called in `main.py` (line 22) and again inside `seed.run()` in `seed.py` (line 42). Running DDL on every startup is fragile and redundant.
- Files: `backend/main.py`, `backend/seed.py`
- Impact: Unnecessary DB round-trips on startup; in production the schema is pre-existing (CLAUDE.md explicitly prohibits dropping/recreating tables), so these calls are no-ops but still hit the database.
- Fix approach: Remove `create_all` from both startup paths and rely on the existing schema. If schema management is needed, adopt Alembic migrations.

**`get_current_fast` filters on `completed.is_(False)` but the field is nullable:**
- Issue: `crud.py` line 23-25 — the query for the active fast filters `completed.is_(False)`. If a fast row has `completed = NULL` (database default is `FALSE` but not enforced as NOT NULL in the schema), the row would not be returned.
- Files: `backend/crud.py`
- Impact: Edge case where a fast could go missing from the "current fast" view.
- Fix approach: Use `models.Fast.completed != True` or `models.Fast.ended.is_(None)` alone as the sole active-fast predicate.

**History view hard-caps at 100 fasts with no pagination UI:**
- Issue: `frontend/src/views/History.vue` line 23 calls `getFasts(0, 100)` with a fixed limit and no load-more or pagination controls.
- Files: `frontend/src/views/History.vue`
- Impact: Users with more than 100 fasts will silently lose history. The backend supports `skip`/`limit` but the UI never advances the page.
- Fix approach: Add a "Charger plus" button or infinite scroll with incrementing `skip`.

**`avg_duration_hours` is always `None` in weekly stats:**
- Issue: `crud.py` line 329 always sets `avg_duration_hours=None` in the `WeeklySummary` objects returned by `get_weekly_summary`. The field is never populated.
- Files: `backend/crud.py`
- Impact: The weekly stats endpoint returns incomplete data; any frontend consuming `avg_duration_hours` from weekly stats will always display a dash or null.
- Fix approach: Compute the average duration for fasts completed within each week's range, similar to the logic in `get_stats`.

**N+1 query pattern in `get_weekly_summary`:**
- Issue: `crud.py` lines 291-331 issues 4 separate DB queries per week in a Python loop (`weeks` iterations × 4 queries = up to 32 queries for the default 8-week window).
- Files: `backend/crud.py`
- Impact: Performance degrades linearly with `weeks` parameter. A single user hitting `/api/stats/weekly` triggers up to 32 round-trips.
- Fix approach: Rewrite using a single SQL query with `GROUP BY date_trunc('week', ...)` or use a CTE to compute all week buckets in one pass.

## Known Bugs

**`useTimer` starts immediately on composable instantiation without guard:**
- Symptoms: `useTimer` calls `start()` at the end of its definition body (line 30), meaning an interval begins even if the component is unmounting synchronously. In practice `onUnmounted(stop)` cleans it up, but calling `start()` again after `stop()` leaves the interval `null` check bypassed if `start` is ever called externally after unmount.
- Files: `frontend/src/composables/useTimer.ts`
- Trigger: Rapid mount/unmount cycles of the Dashboard or FastDetail views.
- Workaround: None currently.

**`create_weight` returns HTTP 201 even on upsert (update existing):**
- Symptoms: `crud.py` lines 131-148 — if an entry for today already exists, the function updates it silently and returns it. The route `POST /api/weight` is declared with `status_code=201` in `main.py` line 129, so a 201 is returned even when no new resource was created.
- Files: `backend/crud.py`, `backend/main.py`
- Trigger: Logging weight twice on the same day.
- Workaround: Functionally benign (data is correct), but violates HTTP semantics.

**`endFast` does not catch errors; failure leaves UI in broken state:**
- Symptoms: `frontend/src/views/FastDetail.vue` lines 94-111 — the `endFast` function has no `catch` block. If the `updateFast` or `getFast` call fails, `submittingEnd` is reset but the form remains open with no error message shown to the user.
- Files: `frontend/src/views/FastDetail.vue`
- Trigger: Network error or 4xx/5xx response while ending a fast.
- Workaround: None.

**`submitLog` and `confirmDeleteFast` also lack error handling:**
- Symptoms: Same pattern as `endFast` — `submitLog` (lines 113-130) and `confirmDeleteFast` (lines 152-161) use try/finally with no catch. Errors are silently swallowed.
- Files: `frontend/src/views/FastDetail.vue`
- Trigger: Any API failure during log submission or fast deletion.
- Workaround: None.

**Offline cached fast can show stale data indefinitely:**
- Symptoms: `useOfflineStorage.ts` saves the fast to `localStorage` on every successful load, but never updates it if the fast is modified from another device or browser tab. The cache has no TTL.
- Files: `frontend/src/composables/useOfflineStorage.ts`, `frontend/src/views/Dashboard.vue`
- Trigger: User edits a fast on one device, then views the app offline on another.
- Workaround: None.

## Security Considerations

**Hardcoded credentials in `database.py`:**
- Risk: Production database password is embedded in source code as a default fallback. Even if the environment variable is used in production, the password is stored in git history and accessible to anyone with repo access.
- Files: `backend/database.py`
- Current mitigation: The `DATABASE_URL` env var can override the default.
- Recommendations: Remove the fallback immediately. Rotate the production database password. Audit git history.

**No authentication on any API endpoint:**
- Risk: All API endpoints (`/api/fasts`, `/api/weight`, `/api/stats`, etc.) are publicly accessible without any authentication or authorization. Anyone who can reach the backend port can read and write all data.
- Files: `backend/main.py`
- Current mitigation: The backend is presumably protected by network-level controls (not exposed publicly except via the frontend nginx proxy). The CORS origin whitelist provides minimal browser-level restriction but not API-level security.
- Recommendations: Add API key authentication or session-based auth if the service is ever exposed publicly or multi-user.

**CORS `allow_credentials=True` with broad `allow_methods=["*"]`:**
- Risk: `main.py` lines 25-34 — allowing credentials alongside wildcard methods means a cross-origin request with cookies or auth headers from either whitelisted origin can call any HTTP method.
- Files: `backend/main.py`
- Current mitigation: Origin whitelist limits this to `localhost:5173` and `openclaw.host`.
- Recommendations: Restrict allowed methods to the actual set used (`GET`, `POST`, `PUT`, `DELETE`).

**No input length limits on text fields:**
- Risk: `schemas.py` — `notes`, `meal_name`, `tips`, `description` fields have no `max_length` validators. An attacker could POST arbitrarily large payloads to exhaust database storage or trigger OOM in the Python process.
- Files: `backend/schemas.py`
- Current mitigation: None.
- Recommendations: Add `Field(max_length=...)` constraints to all free-text Pydantic fields.

**No rate limiting:**
- Risk: The FastAPI backend has no rate limiting. The `/api/fasts`, `/api/weight`, and `/api/stats` endpoints can be called at arbitrary rates.
- Files: `backend/main.py`
- Current mitigation: None at the application layer.
- Recommendations: Add `slowapi` or nginx-level rate limiting.

## Performance Bottlenecks

**N+1 queries in `get_weekly_summary`:**
- Problem: Up to 32 database round-trips per request.
- Files: `backend/crud.py` lines 291-331
- Cause: Python loop iterating `weeks` times, each with 4 separate `db.query()` calls.
- Improvement path: Single SQL query with `GROUP BY week_start`; or batch all date ranges into `IN` clauses.

**Stats endpoint loads all completed fasts into Python memory:**
- Problem: `get_stats` (lines 160-193) fetches all completed fasts via `db.query(...).all()` to compute `avg_hours` in Python rather than using SQL `AVG()`.
- Files: `backend/crud.py` lines 165-172
- Cause: Manual Python average instead of `func.avg()`.
- Improvement path: Replace with `db.query(func.avg(...)).scalar()`.

**Dashboard fetches 4 API calls in parallel on every mount:**
- Problem: `Dashboard.vue` fires `getCurrentFast`, `getStats`, `getWeightTrend(30)`, and `getFasts(0, 5)` concurrently on every page load with no caching layer.
- Files: `frontend/src/views/Dashboard.vue` lines 28-36
- Cause: No frontend data cache or stale-while-revalidate strategy.
- Improvement path: Add a lightweight store (Pinia) with time-based invalidation so re-navigating to the dashboard doesn't refetch all data.

## Fragile Areas

**Route ordering: `/api/fasts/current` vs `/api/fasts/{fast_id}`:**
- Files: `backend/main.py` lines 44-54
- Why fragile: FastAPI resolves routes in declaration order. `/api/fasts/current` must appear before `/api/fasts/{fast_id}` or the string "current" will be interpreted as an integer fast_id, producing a 422 validation error. The current order is correct but the dependency is invisible.
- Safe modification: Never insert a new `/api/fasts/{something}` route above line 44 without verifying it doesn't shadow `/api/fasts/current`.
- Test coverage: No test covers the `/api/fasts/current` endpoint directly.

**Similarly, `/api/meal-recommendations/suggest` and `/api/meal-recommendations/categories` must stay above `/{rec_id}`:**
- Files: `backend/main.py` lines 154-178
- Why fragile: Same pattern — `suggest` and `categories` are literal path segments that would be swallowed by the `{rec_id}` integer parameter if reordered.
- Safe modification: Keep all literal-segment routes for meal recommendations above the `{rec_id}` route.

**`useTimer` composable called inside `shallowRef` lifecycle:**
- Files: `frontend/src/views/Dashboard.vue` line 40, `frontend/src/views/FastDetail.vue` line 79
- Why fragile: `useTimer` is called inside an `onMounted` async callback after an `await`. Vue's composable lifecycle functions (`onUnmounted`) registered inside `useTimer` only work correctly when called synchronously during component setup. Calling `useTimer` inside an `async onMounted` — after the `await` — means `onUnmounted` registered inside `useTimer` may not be bound to the correct component instance in some Vue versions.
- Safe modification: Use `watch` on the timer ref and clean up the interval manually rather than relying on `onUnmounted` inside a dynamically-called composable.
- Test coverage: No tests.

**`seed_meals.json` must exist at the path relative to `seed.py`:**
- Files: `backend/seed.py` line 17
- Why fragile: `seed.py` uses `os.path.dirname(__file__)` to locate `seed_meals.json`. If `seed.py` is ever executed from a different working directory or moved without moving the JSON file, it raises `FileNotFoundError` and prevents server startup.
- Safe modification: Always keep `seed_meals.json` co-located with `seed.py` in `backend/`.

## Test Coverage Gaps

**No tests for core fast lifecycle (CRUD endpoints):**
- What's not tested: `POST /api/fasts`, `PUT /api/fasts/{id}`, `GET /api/fasts/current`, `DELETE /api/fasts/{id}`, daily logs, meals, weight, and stats endpoints.
- Files: `backend/test_meal_recommendations.py` (only meal recommendation tests exist)
- Risk: Regressions in the primary application flow (start fast, end fast, log weight) would not be caught automatically.
- Priority: High

**No frontend tests of any kind:**
- What's not tested: All Vue components and composables, including `useTimer`, `useOfflineStorage`, `useBodyState`, and all view logic.
- Files: All files under `frontend/src/`
- Risk: UI regressions, broken timer display, offline fallback failures, and chart rendering issues are invisible until manual testing.
- Priority: High

**`get_stats` average duration logic not tested:**
- What's not tested: The Python-side duration averaging in `get_stats`; the edge case where `first_weight.id == last_weight.id` (single weight entry returns `None` for `total_weight_lost`).
- Files: `backend/crud.py` lines 160-193
- Risk: Silent wrong values in stats display.
- Priority: Medium

**`get_current_fast` with multiple concurrent active fasts not tested:**
- What's not tested: Behavior when the database has more than one fast with `ended IS NULL` and `completed = FALSE`.
- Files: `backend/crud.py` lines 21-25
- Risk: Silently returns only the most recently started fast; no constraint prevents creating a second active fast via `POST /api/fasts`.
- Priority: Medium

## Missing Critical Features

**No guard against starting a second fast while one is already active:**
- Problem: `POST /api/fasts` has no check for an existing active fast. A user can accidentally create duplicate active fasts.
- Blocks: Data integrity; the current fast endpoint only returns the most recent one, silently hiding any previous active fasts.

**No edit or delete capability for weight entries in the UI:**
- Problem: `WeightView.vue` shows the weight history table but provides no way to edit or delete an entry. There is no `DELETE /api/weight/{id}` or `PUT /api/weight/{id}` backend endpoint.
- Blocks: Correcting accidentally logged weight values.

**No pagination on daily logs or meals:**
- Problem: `get_logs_for_fast` and `get_meals_for_fast` in `crud.py` return all rows for a fast with no limit. A very long fast with many daily log entries would return an unbounded result.
- Files: `backend/crud.py` lines 66-69, 91-95

---

*Concerns audit: 2026-03-09*
