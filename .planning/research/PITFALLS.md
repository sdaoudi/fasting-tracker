# Pitfalls Research

**Domain:** Quality hardening — error handling, tests, security, and query optimization for an existing FastAPI + Vue 3 TypeScript app
**Researched:** 2026-03-09
**Confidence:** HIGH (grounded in known codebase issues from CONCERNS.md + verified patterns from official docs and community sources)

---

## Critical Pitfalls

### Pitfall 1: Fixing the Symptom, Not the Root Cause of the Timer Lifecycle Bug

**What goes wrong:**
The `useTimer` composable is called inside an `async onMounted` after an `await`, which means `onUnmounted` registered inside `useTimer` may not bind to the correct component instance. A fix that simply adds a `try/catch` around `onMounted` or guards the `start()` call does not address the underlying issue: Vue composable lifecycle functions only work when called synchronously during component setup. Calling `useTimer` after any `await` violates this contract, and the cleanup hook silently fails to register on some Vue versions.

**Why it happens:**
Async data fetching is placed in `onMounted`, and once a fast is loaded the timer is started inline. This feels natural but breaks Vue's composable contract. The symptom (interval running after unmount during rapid navigation) looks like a cleanup bug, so the fix attempt targets cleanup rather than the structural problem.

**How to avoid:**
Extract the timer start out of `async onMounted`. Instead: initialize `useTimer` synchronously during component setup with a watch-based trigger. Watch the `currentFast` ref and start/stop the timer in a `watch` callback (not a lifecycle composable call). The composable's `onUnmounted` then registers correctly during synchronous setup.

**Warning signs:**
- Console shows interval callbacks firing on a route that is no longer mounted
- Navigating quickly between Dashboard and FastDetail causes double-counting elapsed time
- Tests for `useTimer` work in isolation but fail when the component mounts after an async fetch

**Phase to address:** Error Handling / Bug Fixes phase (before adding tests — a test written against the broken pattern will encode the bug)

---

### Pitfall 2: Writing Tests Against the Mocked CRUD Layer Only, Missing the Real Query Bugs

**What goes wrong:**
The existing test pattern (in `test_meal_recommendations.py`) patches `crud.*` functions and tests only the route handler logic. If this pattern is extended to cover fasts, weight, and stats, tests will pass even though the actual SQL queries (`get_weekly_summary` N+1, `get_stats` Python-side average, `get_current_fast` nullable `completed` filter) are still broken. Mocked CRUD tests cannot catch database logic bugs.

**Why it happens:**
Mocking the DB session via `app.dependency_overrides[get_db]` is the documented FastAPI pattern and is correct for testing route handlers in isolation. The mistake is treating this as sufficient coverage for the entire application and not adding a second test layer that exercises real SQL.

**How to avoid:**
Two-layer test strategy:
1. Keep mock-based tests for route handler logic (HTTP status codes, request/response schema validation)
2. Add integration tests that use a real PostgreSQL test database (or at minimum a `psycopg2` connection to a test schema) for CRUD function tests. This is the only way to verify the N+1 fix, the `func.avg()` refactor, and the `completed` nullable filter.

Do NOT use SQLite for integration tests — this codebase uses PostgreSQL-specific features (TIMESTAMPTZ, arrays, SERIAL) and SQLite will silently accept queries that behave differently on Postgres.

**Warning signs:**
- All tests pass but `/api/stats/weekly` still returns `avg_duration_hours: null`
- The N+1 fix lands but no test covers the number of DB queries issued
- Tests use `MagicMock(spec=Fast)` for all fast-related tests

**Phase to address:** Test Coverage phase — define the two-layer strategy upfront before writing any fast lifecycle tests

---

### Pitfall 3: Rotating the Database Password Without Removing It from Git History

**What goes wrong:**
The production database password is in `backend/database.py` as a hardcoded fallback string. Removing it from the current file is necessary but insufficient — the password persists in git history and is visible to anyone who clones the repo and runs `git log -p`. Rotating the password without scrubbing history means the old credential remains accessible.

**Why it happens:**
Developers remove the secret from the current file, set the env var in production, and consider the issue resolved. Git history is out of sight and not part of the normal development workflow.

**How to avoid:**
Three steps, all required:
1. Remove the fallback from `database.py` and make startup fail fast if `DATABASE_URL` is not set
2. Rotate the production database password immediately (before or simultaneously with the code change)
3. Scrub git history using `git filter-repo --path backend/database.py --invert-paths` or BFG Repo-Cleaner, then force-push all branches

The `pydantic-settings` pattern (`BaseSettings` reading from env) is the correct replacement — it validates presence at startup rather than silently falling back to a plaintext credential.

**Warning signs:**
- The PR description says "removed hardcoded credential" but does not mention password rotation or history scrubbing
- `git log --all -p -- backend/database.py | grep 'fasting_coach'` returns results after the fix is merged

**Phase to address:** Security Hardening phase — must be the first task, not deferred

---

### Pitfall 4: Error Handling That Resets Loading State but Leaves UI in an Ambiguous State

**What goes wrong:**
The pattern in `FastDetail.vue` uses `try/finally` without `catch`. The `finally` block resets `submittingEnd = false`, which releases the loading spinner, but the user sees no error message and does not know whether their action succeeded or failed. Worse, some functions (like `endFast`) read back the updated fast inside the `try` block — if the read succeeds but the write failed earlier, the UI can show stale "success" data.

Adding a bare `catch(e) { console.error(e) }` block is the most common "fix" and still leaves the UI broken — the error is logged but the user sees nothing.

**How to avoid:**
Each async action must maintain three pieces of state: `isLoading`, `error` (reactive ref, not just console), and `success`. The component template binds to the `error` ref and renders a French-language message when non-null. The error ref is cleared at the start of the next attempt.

Pattern to follow:
```typescript
const error = ref<string | null>(null)
const isSubmitting = ref(false)

async function endFast() {
  error.value = null
  isSubmitting.value = true
  try {
    await updateFast(...)
    await getFast(...)
  } catch (e) {
    error.value = 'Erreur lors de la fin du jeûne. Veuillez réessayer.'
  } finally {
    isSubmitting.value = false
  }
}
```

**Warning signs:**
- `catch` block exists but only calls `console.error` or does nothing
- Error state is a local `let` variable instead of a reactive `ref`
- Template has no `v-if="error"` block bound to the error state

**Phase to address:** Error Handling / Bug Fixes phase

---

### Pitfall 5: Fixing the N+1 in `get_weekly_summary` with Python-Side Batching Instead of SQL

**What goes wrong:**
The natural first refactor for the N+1 pattern (4 queries × 8 weeks = 32 round-trips) is to collect all the week date ranges and issue 4 "batched" queries with `WHERE started BETWEEN ... OR started BETWEEN ...`. This reduces round-trips from 32 to 4 but keeps the aggregation in Python memory, which still loads all qualifying rows before computing counts and averages.

The correct fix is one SQL query with `GROUP BY date_trunc('week', started)` or a CTE that computes all week buckets in a single pass. SQLAlchemy's `func.date_trunc`, `func.avg`, and `func.count` support this directly.

**How to avoid:**
Use `db.query(func.date_trunc('week', models.Fast.started).label('week_start'), func.count(...), func.avg(...)).filter(...).group_by('week_start').all()`. Verify the fix with a test that asserts the number of SQL statements issued (use `sqlalchemy.event.listen` or a query counter fixture in tests).

**Warning signs:**
- The refactored function still has a `for week in weeks:` Python loop
- Performance testing shows the endpoint is still slow with many historical fasts
- The fix was eyeballed as "fewer queries" without measuring

**Phase to address:** Query Optimization phase

---

### Pitfall 6: Adding `max_length` Constraints to Response Schemas Instead of Request Schemas

**What goes wrong:**
When adding input validation (e.g., `Field(max_length=500)` to `notes`, `Field(max_length=100)` to `meal_name`), developers sometimes add constraints to the shared Pydantic model used for both input and output. On the response side, if existing database rows have notes longer than the new limit, FastAPI's response validation raises a 500 `ResponseValidationError` when returning those rows — breaking reads for data that was legitimately stored before the constraint existed.

**Why it happens:**
FastAPI encourages using the same Pydantic model for both request body and response model. When a constraint is added it naturally lands on the shared model.

**How to avoid:**
Separate request schemas (e.g., `FastCreate`, `LogCreate`) from response schemas (e.g., `FastResponse`, `LogResponse`). Apply `max_length` only to the `Create`/`Update` request schemas. The response schemas should reflect what the database can return without artificial limits.

This codebase already has `FastCreate` and `FastUpdate` in `schemas.py` — apply constraints there, not on the base `Fast` schema used for responses.

**Warning signs:**
- A single `class Fast(BaseModel)` is used as both `response_model=Fast` and the request body type
- GET endpoints return 500 for rows created before the validation was added
- The constraint is defined on the SQLAlchemy model's column rather than the Pydantic schema

**Phase to address:** Security Hardening / Input Validation phase

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `Base.metadata.create_all()` on every startup | No migration tooling needed | DDL round-trip on every restart; masks schema drift; production schema already exists, this is a no-op | Never for this project — remove it |
| `seed.run()` in startup event | Auto-populates meal recommendations | Race condition risk at startup; blocks request serving; adds DB session overhead | Move to one-time migration script |
| Mock-only tests for all endpoints | Fast CI, simple setup | Cannot catch SQL bugs, query regressions, or Postgres-specific failures | Acceptable for route handler tests only — must pair with real-DB CRUD tests |
| `try/finally` without `catch` in Vue actions | Loading state always resets | User sees no error; silent failures look like success | Never — always add catch |
| Shared request/response Pydantic models | Less code duplication | `max_length` on response schemas causes 500s for existing data; validator changes affect reads | Never for public-facing APIs; acceptable only for internal admin endpoints with no legacy data |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| PostgreSQL test database | Use SQLite in-memory for speed | Use real Postgres — TIMESTAMPTZ, array columns, SERIAL, and `date_trunc` all behave differently on SQLite |
| `get_db` dependency in tests | Override at the function level per test | Override via `app.dependency_overrides[get_db]` at fixture level and always clear in fixture teardown (`app.dependency_overrides.clear()`) |
| `app.dependency_overrides` cleanup | Fixture does not call `.clear()` after yield | Test pollution: one test's mock DB leaks into subsequent tests, causing false passes or false failures |
| FastAPI `TestClient` and async routes | Assume `async def` routes require `pytest-asyncio` | `TestClient` handles the event loop synchronously — no `pytest-asyncio` needed for route tests |
| `func.date_trunc` in SQLAlchemy | Use raw SQL strings via `text()` | Use `func.date_trunc('week', column)` — stays in ORM, benefits from parameter binding |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 in `get_weekly_summary` (32 queries) | `/api/stats/weekly` slow on every call; visible in query logs | Single `GROUP BY date_trunc('week', ...)` SQL query | Already broken at current scale; worsens with more weeks in the window |
| Python-side `AVG` in `get_stats` | Loads all completed fasts into memory to compute average | Replace with `db.query(func.avg(duration_expr)).scalar()` | Breaks at a few thousand fasts (memory pressure) |
| Dashboard firing 4 parallel API calls on every mount | Noticeable latency on mobile; chart and stats flash on every navigation | Add a simple time-based cache (60s) on `currentFast` and `stats` — even a module-level `ref` with a timestamp is sufficient without Pinia | Noticeable from day one on slow mobile connections |
| No pagination on `get_logs_for_fast` / `get_meals_for_fast` | Endpoints return all rows for a fast; a 72h fast with hourly logs returns unbounded results | Add `skip`/`limit` to these endpoints matching the pattern already on `GET /api/fasts` | Breaks silently once a fast accumulates many log entries |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Hardcoded DB password as fallback in `database.py` | Anyone with repo access has the production credential; persists in git history after file edit | Remove fallback, require env var, rotate password, scrub git history |
| CORS `allow_credentials=True` with `allow_methods=["*"]` | Credentialed cross-origin requests permitted for all HTTP methods | Restrict to `["GET", "POST", "PUT", "DELETE"]` — the actual set used by this API |
| No `max_length` on free-text Pydantic request fields | Arbitrarily large POST bodies accepted; can exhaust DB storage or cause OOM | Add `Field(max_length=500)` to `notes`, `Field(max_length=100)` to `meal_name`, `Field(max_length=200)` to description fields in all `*Create`/`*Update` schemas |
| `seed.run()` executing DDL (`create_all`) on every startup | Unintended schema changes if SQLAlchemy models diverge from the live schema | Remove both `create_all` calls; the production schema already exists |
| No startup validation that `DATABASE_URL` is set | App starts silently with the hardcoded fallback credential even after env var is "configured" | Use `pydantic-settings` `BaseSettings` — raises `ValidationError` at import time if required env vars are missing |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Silent failure when ending a fast (no catch block) | User taps "Terminer le Jeûne", nothing happens or the dialog closes with no confirmation; fast may or may not have ended | Show a French error message in the dialog: `"Erreur lors de la fin du jeûne. Veuillez réessayer."` with a retry button |
| Silent failure when submitting daily log | Log form submits, spinner disappears, no feedback — user does not know if data was saved | Show toast/alert on both success (`"Journal enregistré"`) and failure |
| Stale offline cache with no TTL | User views app offline and sees a fast that ended hours ago still shown as active | Add a `cached_at` timestamp to the localStorage object; invalidate and show a "données hors ligne" banner if cache is older than 30 minutes |
| History hard-capped at 100 entries with no warning | Users with 100+ fasts silently lose history — there is no "you've reached the limit" indicator | Either add pagination controls, or show a count: `"Affichage de 100 sur 143 jeûnes"` |
| `weight_after` prompt appears as a dialog mid-fast-end flow | On mobile, the nested prompt (end fast → enter weight) is easy to dismiss accidentally, losing the context | Pre-populate the weight field in the end-fast form with the last recorded weight; do not use a separate dialog |

---

## "Looks Done But Isn't" Checklist

- [ ] **Error handling:** `catch` block exists AND binds error to a reactive `ref` AND template renders a French message — not just `console.error`
- [ ] **Security: credential removal:** File is patched AND password rotated in production AND git history scrubbed AND startup fails fast if env var is missing
- [ ] **N+1 fix:** Query rewrite lands AND a test asserts that a single SQL statement is issued for `get_weekly_summary` (not just "it returns correct data")
- [ ] **`avg_duration_hours` fix:** Weekly stats endpoint returns a numeric value AND a test verifies this with real data (not a mock that returns a hardcoded value)
- [ ] **`useTimer` lifecycle fix:** Timer is initialized synchronously in component setup AND a test mounts/unmounts the Dashboard rapidly and asserts no interval leaks
- [ ] **Input validation:** `max_length` added to request schemas ONLY — GET endpoints for existing data do not return 500
- [ ] **Pagination on History:** "Charger plus" button or pagination controls exist AND are exercised when there are more than `limit` fasts in the DB
- [ ] **Test isolation:** Each test runs in a transaction that is rolled back; running the full suite twice produces identical results

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Credential in git history discovered post-deployment | HIGH | Rotate DB password immediately; force-push scrubbed history; audit DB access logs for unauthorized queries; notify any collaborators to re-clone |
| `ResponseValidationError` 500s after adding `max_length` to response schema | MEDIUM | Revert the constraint from the response schema; add it only to request schema; existing data is unaffected |
| Tests pass but SQL bug still present (mock-only tests) | MEDIUM | Identify which CRUD functions lack real-DB tests; add integration test layer; the N+1 and `avg_duration_hours` bugs are the highest priority targets |
| Timer interval leak causing double-counting on Dashboard | LOW | Identify where `useTimer` is called post-await; move composable init to synchronous setup; verify with a mount/unmount cycle test |
| `seed.run()` race condition seeding duplicate meals on multi-process startup | LOW | Add a unique constraint on `meal_recommendations.name` or use an advisory lock; or move seeding to a one-time migration |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `useTimer` async lifecycle bug | Error Handling / Bug Fixes | Mount/unmount Dashboard 10× rapidly; confirm no interval leaks in browser DevTools |
| `endFast`/`submitLog`/`confirmDeleteFast` missing catch | Error Handling / Bug Fixes | Simulate network failure (DevTools offline mode); confirm French error message appears |
| Credential in git history | Security Hardening | `git log --all -p -- backend/database.py | grep password` returns nothing after scrub |
| Missing `max_length` on request fields | Security Hardening | POST a 10,000-character notes field; confirm 422 validation error is returned |
| `allow_methods=["*"]` CORS config | Security Hardening | Verify only GET/POST/PUT/DELETE are listed in the CORS middleware configuration |
| N+1 in `get_weekly_summary` | Query Optimization | Query counter test asserts 1 SQL statement issued; `EXPLAIN ANALYZE` shows single scan |
| Python-side AVG in `get_stats` | Query Optimization | Code review shows `func.avg()` in query; no Python-side aggregation loop |
| Mock-only tests missing SQL bugs | Test Coverage | Integration test suite connects to real Postgres test DB; `get_weekly_summary`, `get_stats`, `get_current_fast` all covered with real queries |
| `avg_duration_hours` always None | Test Coverage (reveals it) / Query Optimization (fixes it) | Weekly stats test asserts numeric value when completed fasts exist in date range |
| Response schema `max_length` breaks GET | Security Hardening | GET `/api/fasts` succeeds for all existing rows after validation added |
| Startup `create_all` / `seed.run()` side effects | Security Hardening / Bug Fixes | App startup logs show no DDL statements; meal seeding moved to one-time migration |

---

## Sources

- Known issues: `.planning/codebase/CONCERNS.md` — direct codebase audit (HIGH confidence)
- FastAPI error handling patterns: [FastAPI official docs — Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) (HIGH confidence)
- FastAPI testing with real Postgres: [Pytest API Testing with FastAPI, SQLAlchemy, Postgres](https://pytest-with-eric.com/api-testing/pytest-api-testing-1/) (MEDIUM confidence)
- SQLite vs Postgres in tests: [FastAPI GitHub issue #3906](https://github.com/fastapi/fastapi/issues/3906) (MEDIUM confidence)
- Vue 3 composable lifecycle testing: [Mastering Vue 3 Composables Testing with Vitest](https://dylanbritz.dev/writing/testing-vue-composables-lifecycle/) (MEDIUM confidence)
- Vue 3 async composable pitfalls: [Coding Better Composables: Async Without Await — Vue Mastery](https://www.vuemastery.com/blog/coding-better-composables-5-of-5/) (MEDIUM confidence)
- Vue 3 error handling in composables: [Best Practices for Error Handling in Vue Composables](https://alexop.dev/posts/best-practices-for-error-handling-in-vue-composables/) (MEDIUM confidence)
- FastAPI secrets management: [pydantic-settings guide](https://blog.greeden.me/en/2025/11/11/no-drama-configuration-secret-management-a-practical-fastapi-x-pydantic-settings-guide-environment-variables-env-multi-env-switching-type-safety-validation-secret-operation/) (MEDIUM confidence)
- Pydantic v2 field validation: [Pydantic official docs — Validators](https://docs.pydantic.dev/latest/concepts/validators/) (HIGH confidence)
- SQLAlchemy GROUP BY aggregation: [SQLAlchemy Series Part 3](https://medium.com/@umair.qau586/sqlalchemy-seriespart-3-mastering-sqlalchemy-queries-and-aggregation-597befb46b09) (MEDIUM confidence)

---
*Pitfalls research for: FastAPI + Vue 3 TypeScript quality hardening (error handling, tests, security, query optimization)*
*Researched: 2026-03-09*
