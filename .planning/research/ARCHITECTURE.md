# Architecture Research

**Domain:** Quality hardening of an existing FastAPI + Vue 3 client-server SPA
**Researched:** 2026-03-09
**Confidence:** HIGH (based on direct codebase analysis, well-established FastAPI and Vue 3 patterns)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Vue 3 SPA)                        │
│                                                                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Dashboard  │  │  FastDetail  │  │  WeightView  │  │  History  │  │
│  │  .vue      │  │  .vue        │  │  .vue        │  │  .vue     │  │
│  └─────┬──────┘  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘  │
│        │                │                  │                │        │
│  ┌─────▼────────────────▼──────────────────▼────────────────▼─────┐  │
│  │               Composables Layer                                  │  │
│  │  useTimer  useOfflineStorage  useDark  useOnlineStatus           │  │
│  └─────────────────────────┬────────────────────────────────────────┘  │
│                            │                                           │
│  ┌─────────────────────────▼────────────────────────────────────────┐  │
│  │               API Client (client.ts)                              │  │
│  │  request<T>()  getCurrentFast()  updateFast()  getStats() ...    │  │
│  └─────────────────────────┬────────────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────────────┘
                             │ HTTP REST (port 8042)
┌────────────────────────────┼────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
│                                                                          │
│  ┌─────────────────────────▼────────────────────────────────────────┐   │
│  │               Route Handlers (main.py)                            │   │
│  │  /api/fasts  /api/fasts/current  /api/stats  /api/weight  ...    │   │
│  └─────────────────────────┬────────────────────────────────────────┘   │
│                            │                                             │
│  ┌─────────────────────────▼────────────────────────────────────────┐   │
│  │               CRUD Layer (crud.py)                                │   │
│  │  get_fasts()  create_fast()  get_weekly_summary()  get_stats()   │   │
│  └─────────────────────────┬────────────────────────────────────────┘   │
│                            │                                             │
│  ┌─────────────────────────▼────────────────────────────────────────┐   │
│  │               ORM Models (models.py) + Pydantic Schemas           │   │
│  │  Fast  DailyLog  Meal  WeightLog  MealRecommendation              │   │
│  └─────────────────────────┬────────────────────────────────────────┘   │
└────────────────────────────┼────────────────────────────────────────────┘
                             │ SQLAlchemy / psycopg2
                    ┌────────▼────────┐
                    │   PostgreSQL    │
                    │   fasting_db   │
                    └─────────────────┘
```

### Component Boundaries for Error Handling

The following table identifies the exact boundary where each category of error should be caught and surfaced. This directly informs which files need changes.

| Boundary | Error Category | Catch Location | Surface To User |
|----------|---------------|----------------|-----------------|
| `crud.py` functions | DB constraint violations, integrity errors | Route handler in `main.py` | HTTP 409/400 with structured `detail` |
| `main.py` route handlers | Missing entity (None return from crud) | Already handled — `raise HTTPException(404)` | Response body `{"detail": "..."}` |
| `main.py` route handlers | Active fast guard (start second fast) | `create_fast` route, before calling crud | HTTP 409 with French message |
| `frontend/src/api/client.ts` `request<T>()` | Non-OK HTTP responses | Already throws `Error` — needs structured error type | Propagate typed error to views |
| `frontend/src/views/FastDetail.vue` `endFast()` | Network failure, 4xx/5xx from updateFast/getFast | Add `catch` block — currently missing | Toast notification + reset loading state |
| `frontend/src/views/FastDetail.vue` `submitLog()` | Network failure, 4xx/5xx | Add `catch` block — currently missing | Toast notification |
| `frontend/src/views/FastDetail.vue` `confirmDeleteFast()` | Network failure, 4xx/5xx | Add `catch` block — currently missing | Toast notification + do not navigate away |
| `frontend/src/views/StartFast.vue` | Starting fast when one active | Backend returns 409 — needs catch + display | Toast or inline error message |
| `frontend/src/App.vue` | Global unhandled promise rejections | `window.addEventListener('unhandledrejection')` as safety net | Silent log only |

### Toast Notification Architecture

There is currently no toast system. The recommended pattern for a no-Pinia Vue 3 app is a lightweight composable + single mount point:

```
App.vue
  └── <ToastContainer />  (renders active toasts)

useToast.ts (composable — shared via module-level reactive state)
  ├── toasts: ref([])     (module-level, not per-component)
  ├── showToast(msg, type, duration)
  └── dismissToast(id)

Views / composables call:
  import { useToast } from '@/composables/useToast'
  const { showToast } = useToast()
  showToast('Erreur réseau', 'error')
```

This avoids Pinia while sharing state across components via module-level reactive refs — a standard Vue 3 pattern that does not require a store.

### Test Architecture (Backend)

The existing test in `backend/test_meal_recommendations.py` establishes the correct pattern. It uses:
- `fastapi.testclient.TestClient` wrapping the real FastAPI app
- `app.dependency_overrides[get_db]` to inject a mock session
- `unittest.mock.patch` to stub `crud.*` functions at the route level
- `pytest` fixtures for client setup/teardown

This pattern should be applied consistently to all new tests. The test isolation level is at the **route handler**, not the database. This means:
- Routes are tested end-to-end (HTTP method, URL, status code, response shape)
- CRUD logic is stubbed — no real database needed
- Schema validation is exercised (Pydantic coerces the mock returns)

**Test file layout for core lifecycle:**

```
backend/
├── test_meal_recommendations.py   (existing)
├── test_fasts.py                  (add: CRUD lifecycle)
├── test_stats.py                  (add: stats + weekly summary)
└── test_weight.py                 (add: weight CRUD + upsert behavior)
```

**What each test file covers:**

| File | Tests |
|------|-------|
| `test_fasts.py` | `POST /api/fasts` (create), `GET /api/fasts/current` (active fast), `PUT /api/fasts/{id}` (end fast), `DELETE /api/fasts/{id}`, active-fast guard (409 on second active fast), route ordering (`/current` before `/{id}`) |
| `test_stats.py` | `GET /api/stats` (avg duration, weight lost edge cases), `GET /api/stats/weekly` (avg_duration_hours populated, correct week bucketing) |
| `test_weight.py` | `POST /api/weight` (create new, upsert existing — returns 201 either way), `GET /api/weight/trend` |

**Unit tests for CRUD functions (no HTTP layer):**

Some logic is better tested at the CRUD level directly against a real test database or a constructed session:

| Function | Test focus |
|----------|------------|
| `get_weekly_summary()` | Single SQL query returns same shape as 4-per-week loop; `avg_duration_hours` is now populated |
| `get_stats()` | `avg_hours` computation; `total_weight_lost` when only one weight entry (returns None) |
| `get_current_fast()` | Returns None when no active fast; returns correct fast when `completed IS NULL` (nullable edge case) |

**Frontend test architecture (Vitest + Vue Test Utils):**

The frontend has no tests. The recommended toolchain is Vitest (native Vite integration, faster than Jest) + `@vue/test-utils` for component mounting.

```
frontend/src/
├── composables/
│   └── __tests__/
│       ├── useTimer.test.ts       (interval lifecycle, formatDuration, getPhase)
│       └── useOfflineStorage.test.ts  (save/load/TTL)
├── views/
│   └── __tests__/
│       └── FastDetail.test.ts     (endFast error handling with mocked API)
└── components/
    └── __tests__/
        └── CircularProgress.test.ts  (progress prop → rendered arc)
```

Priority order for frontend tests: composables first (pure logic, no DOM), then views (error path coverage), then components (visual regression last).

## Recommended Project Structure

No structural changes are needed. The existing layout is correct. Changes are additions within existing files and new test files.

```
backend/
├── main.py              (add: active-fast guard in create_fast route)
├── crud.py              (fix: N+1 in get_weekly_summary, avg_duration_hours, get_stats SQL AVG)
├── database.py          (fix: remove hardcoded credential fallback)
├── schemas.py           (fix: add max_length to text fields)
├── test_fasts.py        (new)
├── test_stats.py        (new)
└── test_weight.py       (new)

frontend/src/
├── composables/
│   ├── useTimer.ts      (fix: lifecycle issue when called after await)
│   └── useToast.ts      (new: shared toast state)
├── components/
│   └── ToastContainer.vue  (new: renders active toasts)
└── views/
    └── FastDetail.vue   (fix: add catch blocks to endFast, submitLog, confirmDeleteFast)
```

## Architectural Patterns

### Pattern 1: Route-Level Guard for Business Rules

**What:** Add a check in the `POST /api/fasts` route handler — before calling `crud.create_fast()` — that calls `crud.get_current_fast(db)`. If it returns a fast, raise `HTTPException(status_code=409, detail="Un jeûne est déjà en cours")`.

**When to use:** Any endpoint where a business rule must be enforced before a write. Keep guard logic in the route handler, not the CRUD layer, so CRUD functions remain composable.

**Trade-offs:** Routes become slightly longer, but CRUD stays pure. The alternative (guard in CRUD) couples business rules to database functions.

```python
@app.post("/api/fasts", response_model=FastResponse, status_code=201)
def create_fast(fast: FastCreate, db: Session = Depends(get_db)):
    active = crud.get_current_fast(db)
    if active:
        raise HTTPException(status_code=409, detail="Un jeûne est déjà en cours")
    return crud.create_fast(db, fast)
```

### Pattern 2: Single SQL Aggregation to Replace Python Loops

**What:** Replace the `get_weekly_summary` loop (4 queries × N weeks = up to 32 round-trips) with a single `GROUP BY date_trunc('week', ...)` query using SQLAlchemy's `func` helpers.

**When to use:** Any Python loop that issues DB queries per iteration. The fix boundary is entirely within `crud.py` — route handler and schema are unchanged.

**Trade-offs:** More complex SQL but dramatically fewer round-trips. For an 8-week window: 32 queries → 1-2 queries.

```python
# Sketch — compute all week stats in one pass
from sqlalchemy import func, case

results = db.query(
    func.date_trunc('week', models.Fast.started).label('week_start'),
    func.count(models.Fast.id).label('fasts_started'),
    func.count(case((models.Fast.completed == True, 1))).label('fasts_completed'),
    func.avg(
        case((
            models.Fast.completed == True,
            func.extract('epoch', models.Fast.ended - models.Fast.started) / 3600
        ))
    ).label('avg_duration_hours'),
).group_by('week_start').order_by(desc('week_start')).limit(weeks).all()
```

`avg_duration_hours` is populated as part of the same query, fixing the always-`None` bug simultaneously.

### Pattern 3: try/catch/finally with Toast in Vue 3 Views

**What:** Wrap all async mutation functions in view components with explicit `catch` blocks that call `showToast()`. The `finally` block always resets loading state. Errors must never silently swallow.

**When to use:** Every async function in a view that calls the API client and mutates state (end fast, submit log, delete fast, log weight).

**Trade-offs:** Slightly more verbose per function, but the pattern is uniform and easy to audit. The alternative (a global error handler) hides context.

```typescript
async function endFast() {
  submittingEnd.value = true
  try {
    await updateFast(fast.value!.id, { ended: new Date().toISOString(), ... })
    await getFast(fast.value!.id)
  } catch (err) {
    showToast('Erreur lors de la fin du jeûne', 'error')
  } finally {
    submittingEnd.value = false
  }
}
```

### Pattern 4: Composable Lifecycle Safety (useTimer Fix)

**What:** Move the `start()` call and `onUnmounted(stop)` registration out of the composable body. The composable should return `start`/`stop` and let the view control the lifecycle explicitly from within synchronous setup or a `watchEffect`.

**When to use:** Any composable that registers lifecycle hooks (`onMounted`, `onUnmounted`) — they must be called synchronously during component setup. Calling them inside an `async onMounted` after an `await` breaks the component instance binding in Vue 3.

**Trade-offs:** Views must explicitly call `start()` after the async data fetch. This is more verbose but correct and testable.

```typescript
// In the view — after the await, manage lifecycle manually:
onMounted(async () => {
  const fast = await getCurrentFast()
  if (fast) {
    const timer = useTimer(fast.started, fast.target_hours)
    // timer.start() is NOT called automatically — call explicitly
    timer.start()
    // register cleanup manually since we're past async boundary
    onUnmounted(() => timer.stop())
  }
})
```

Alternatively, restructure `Dashboard.vue` to call `useTimer` synchronously at setup time using a `watchEffect` that reacts to the fetched fast ref:

```typescript
// Preferred: call useTimer at setup time; let it react to the fast ref
const fastRef = ref<Fast | null>(null)
// useTimer accepts a computed startedAt that is null until fast loads
const timer = useTimer(computed(() => fastRef.value?.started ?? null), ...)
```

This keeps `useTimer` called synchronously during component setup, making `onUnmounted` registration valid.

## Data Flow

### Request Flow (Mutation — End Fast)

```
User taps "Terminer le Jeûne"
    |
FastDetail.vue  endFast()
    |
    ├── submittingEnd.value = true
    |
    ├── try:
    |     client.ts  updateFast(id, { ended, weight_after })
    |         |
    |         └── PUT /api/fasts/{id}  →  main.py  update_fast()
    |                 |
    |                 └── crud.update_fast(db, id, payload)
    |                         |
    |                         └── db.query(Fast).filter(id).first()
    |                             fast.ended = now
    |                             db.commit()
    |                             return FastResponse
    |
    ├── catch (err):
    |     showToast('Erreur ...', 'error')   ← currently missing
    |
    └── finally:
          submittingEnd.value = false
```

### N+1 Fix Data Flow (Weekly Summary)

```
BEFORE (32 round-trips for 8 weeks):
    GET /api/stats/weekly
        |
        crud.get_weekly_summary(db, weeks=8)
            |
            for i in range(8):           ← Python loop
                db.query(count fasts_started)   → round-trip 1
                db.query(count fasts_completed) → round-trip 2
                db.query(first weight)          → round-trip 3
                db.query(last weight)           → round-trip 4

AFTER (2 round-trips regardless of weeks):
    GET /api/stats/weekly
        |
        crud.get_weekly_summary(db, weeks=8)
            |
            db.query(...GROUP BY week_start...)  → 1 round-trip (fasts)
            db.query(...GROUP BY week...)         → 1 round-trip (weights)
            Python: merge results by week
```

### State Management (Current Pattern — No Pinia)

```
View mounts
    |
    └── onMounted: fetch from API → local ref (e.g., fast = ref<Fast>())
                          |
                          └── child components receive via props
                          └── composables receive via arguments

User action
    |
    └── async handler → API call → update local ref → Vue reactivity propagates
```

No global state store is required for error handling or the current fixes. Module-level reactive refs (for `useToast`) provide the only cross-component shared state needed.

## Scaling Considerations

This is a single-user personal app. Scaling is not a concern. The following notes apply only to correctness and performance at current scale.

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 1 user (current) | N+1 fix needed — 32 queries per stats load is perceptibly slow even for one user |
| 1 user (future: years of data) | `get_stats` loads all completed fasts into Python — replace with `func.avg()` SQL aggregate |
| Multi-user (out of scope) | Add authentication layer, per-user data scoping |

### Scaling Priorities

1. **First bottleneck (now):** N+1 in `get_weekly_summary` — fix with GROUP BY query. This is the only current performance issue that would be noticeable in normal use.
2. **Second bottleneck (future):** Python-side averaging in `get_stats` — replace with `db.query(func.avg(...)).scalar()`. Low urgency until fast count grows large.

## Anti-Patterns

### Anti-Pattern 1: Silent Error Swallowing in try/finally

**What people do:** Write `try { ... } finally { loading = false }` with no `catch` block. In JavaScript/TypeScript, an uncaught error in a `try` block with only `finally` will still propagate up — but since the callers (Vue lifecycle hooks like `onMounted`) do not re-throw, the error disappears silently and the user sees nothing.

**Why it's wrong:** The user cannot tell if their action succeeded or failed. The loading spinner resets but no feedback appears. This is the exact pattern in `endFast`, `submitLog`, `confirmDeleteFast` in `FastDetail.vue`.

**Do this instead:** Always include `catch (err)` between `try` and `finally`. At minimum log the error; for user-facing mutations, always show a toast.

### Anti-Pattern 2: Composable Lifecycle Hooks Called After Async Await

**What people do:** Call `useTimer(...)` inside an `async onMounted` callback, after an `await` for data. Vue's `onUnmounted` registered inside `useTimer` uses Vue's `getCurrentInstance()` internally; after `await`, the component instance context is no longer active.

**Why it's wrong:** `onUnmounted` may not fire when the component unmounts, causing the `setInterval` in `useTimer` to continue running after the component is destroyed. This leaks timers and causes `now.value` updates on unmounted components, producing Vue warnings in dev mode and subtle bugs in production.

**Do this instead:** Call composables synchronously during component setup, before any `await`. Use a `watchEffect` or `watch` to react to async data after it loads, rather than calling composables inside async callbacks.

### Anti-Pattern 3: N+1 Queries in a Python Loop

**What people do:** Write a `for` loop in Python that issues multiple `db.query()` calls per iteration to gather aggregated data for each time bucket.

**Why it's wrong:** Each `db.query()` is a synchronous network round-trip to PostgreSQL. For 8 weeks × 4 queries = 32 round-trips, each with network latency. SQLAlchemy's ORM makes this easy to write accidentally because queries look like Python function calls.

**Do this instead:** Use SQL aggregation (`GROUP BY`, `func.count()`, `func.avg()`, `func.sum()`) to compute all buckets in a single query. Move the bucketing logic into SQL, not Python.

### Anti-Pattern 4: Hardcoded Credentials with Environment Variable Override

**What people do:** Write `DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host/db")` thinking the default is only a "development convenience" that will always be overridden in production.

**Why it's wrong:** The default is committed to git history permanently, even after removal. The production password is now in every clone of the repository. If the env var is ever accidentally missing in production (e.g., after a redeploy), the hardcoded password silently takes over rather than failing loudly.

**Do this instead:** Remove the default entirely. `DATABASE_URL = os.environ["DATABASE_URL"]` — raises `KeyError` at startup if missing. This is a loud, obvious failure that prevents silent use of wrong credentials.

## Integration Points

### Internal Boundaries

| Boundary | Communication | Change Impact |
|----------|---------------|---------------|
| `main.py` route → `crud.py` | Direct function call with `db: Session` | Adding active-fast guard: only `main.py` changes |
| `crud.py` → PostgreSQL | SQLAlchemy ORM queries | N+1 fix: only `crud.py` changes; schema and routes unchanged |
| `frontend/src/api/client.ts` → backend | `fetch()` over HTTP | Error type changes propagate to all views that call the API |
| `useTimer.ts` → Dashboard/FastDetail views | Composable return values | Lifecycle fix changes call site in both views |
| `useToast.ts` → all views | Module-level reactive ref | New file; views import and call `showToast()` |

### Build Order (Fix Dependencies)

The following order minimizes risk of one fix interfering with another. Each group is independent from other groups; within a group, order matters.

**Group 1 — Backend correctness (no frontend changes needed, no test dependency):**
1. Remove hardcoded credentials from `database.py` (unblocks everything; credential rotation needed)
2. Fix active-fast guard in `create_fast` route in `main.py`
3. Fix `get_current_fast` nullable predicate in `crud.py`

**Group 2 — Backend performance + data correctness (depends on Group 1 for stable DB connection):**
4. Rewrite `get_weekly_summary` in `crud.py` (fixes N+1 and `avg_duration_hours` simultaneously)
5. Replace Python averaging in `get_stats` with `func.avg()` SQL aggregate

**Group 3 — Backend tests (depends on Groups 1-2 to test correct behavior):**
6. Write `test_fasts.py` (covers active-fast guard, route ordering, CRUD lifecycle)
7. Write `test_stats.py` (covers fixed avg_duration_hours, weekly summary shape)
8. Write `test_weight.py` (covers upsert behavior, trend endpoint)

**Group 4 — Frontend infrastructure (independent of backend groups):**
9. Create `useToast.ts` composable and `ToastContainer.vue`
10. Mount `<ToastContainer />` in `App.vue`

**Group 5 — Frontend error handling (depends on Group 4 for toast system):**
11. Add `catch` blocks to `endFast`, `submitLog`, `confirmDeleteFast` in `FastDetail.vue`
12. Fix `useTimer` lifecycle issue (call site changes in `Dashboard.vue` and `FastDetail.vue`)

**Group 6 — Frontend tests (depends on Groups 4-5 to test fixed behavior):**
13. Write `useTimer.test.ts` (interval lifecycle, formatDuration, getPhase)
14. Write `FastDetail.test.ts` (error handling paths)

**Group 7 — UI completeness (independent of all above, no dependencies):**
15. Add weight entry edit/delete (new backend endpoints + UI)
16. Add pagination to History view
17. Add "load more" or infinite scroll

## Sources

- Direct codebase analysis: `backend/crud.py`, `backend/main.py`, `frontend/src/composables/useTimer.ts`, `frontend/src/views/FastDetail.vue`, `backend/test_meal_recommendations.py` — HIGH confidence
- FastAPI dependency injection and `TestClient` patterns: official FastAPI docs (https://fastapi.tiangolo.com/tutorial/testing/) — HIGH confidence
- Vue 3 composable lifecycle rules (`getCurrentInstance` behavior after async): Vue 3 docs on composables (https://vuejs.org/guide/reusability/composables#conventions-and-best-practices) — HIGH confidence
- SQLAlchemy GROUP BY aggregation: SQLAlchemy 2.x docs — HIGH confidence
- Module-level reactive refs for cross-component state (no Pinia): Vue 3 reactivity docs (https://vuejs.org/guide/scaling-up/state-management#simple-state-management-with-reactivity-api) — HIGH confidence

---
*Architecture research for: FastAPI + Vue 3 quality hardening*
*Researched: 2026-03-09*
