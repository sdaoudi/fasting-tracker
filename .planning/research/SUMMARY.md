# Project Research Summary

**Project:** Fasting Tracker — Quality Hardening Milestone
**Domain:** Personal health tracker (FastAPI + Vue 3 TypeScript) — testing, error handling, security, query optimization
**Researched:** 2026-03-09
**Confidence:** HIGH

## Executive Summary

This is an additive hardening milestone on a fully operational fasting tracker app. The app has a working FastAPI backend, Vue 3 frontend, and PostgreSQL database with live data. The research reveals six categories of known defects: silent error swallowing in Vue views, a timer lifecycle bug causing interval leaks, a production database credential committed to git, an N+1 query pattern in weekly stats (32 round-trips), a missing `avg_duration_hours` computation (always returns null), and absent weight entry edit/delete endpoints. None of these defects prevent basic use today, but each one erodes data integrity, user trust, or security in ways that compound over time.

The recommended approach is to fix defects in dependency order: security first (credential removal requires password rotation and git history scrub before any other work), then backend correctness fixes (active-fast guard, nullable predicate bug), then query optimization (N+1 rewrite), then tests (written against correct behavior, not broken behavior), then frontend error handling (requires the toast infrastructure to land before the catch blocks), and finally UI completeness (weight edit/delete, history pagination). This ordering is not arbitrary — writing tests before the N+1 fix is fixed means tests encode the buggy behavior; adding catch blocks before the toast system means inconsistent error surfaces.

The primary risk in this milestone is partial fixes that appear done but are not. The credential pitfall is the clearest example: removing the hardcoded fallback from `database.py` without rotating the password and scrubbing git history accomplishes nothing. Similarly, adding `catch(e) { console.error(e) }` blocks satisfies a code reviewer but leaves users with no feedback. Each fix has a "looks done but isn't" failure mode, and the pitfalls research provides explicit verification checklists for each one.

## Key Findings

### Recommended Stack

The existing app stack (FastAPI 0.115.0, SQLAlchemy 2.0.35, Pydantic 2.9.2, Vue 3.5.25, Vite 7.3.1, Tailwind v4) requires no changes. This milestone adds only the tooling needed for testing and security. All recommended versions are verified against official sources.

**Core new technologies:**
- `pytest-asyncio 1.3.0`: Async test support — required for FastAPI async routes; use `asyncio_mode = "auto"` in `pyproject.toml` to avoid per-test decorators
- `pytest-cov 7.0.0`: Coverage measurement — identifies untested paths; requires `coverage>=7.10.6`
- `pydantic-settings 2.13.1`: Env var management with type validation — FastAPI's official recommendation; replaces hardcoded `DATABASE_URL` fallback; raises `ValidationError` at startup if env var is absent
- `slowapi 0.1.9`: Request rate limiting — no Redis dependency, suitable for single-user personal app
- `vitest 4.0.17`: Frontend test runner — shares Vite config, zero additional configuration for Vite 7 project, dramatically faster than Jest for ESM/TypeScript
- `@vue/test-utils 2.4.6`: Vue 3 component and composable mounting — required for lifecycle testing (`useTimer` bug specifically requires mount/unmount cycle tests)
- `happy-dom`: DOM environment for Vitest — faster than jsdom, sufficient for this test suite

**Critical constraint:** Do NOT use SQLite for integration tests. The codebase uses PostgreSQL-specific features (`ARRAY(Text)`, `TIMESTAMPTZ`, `date_trunc`). Tests passing against SQLite would give false confidence while production bugs persist.

### Expected Features

The feature landscape is defined by the existing codebase audit (CONCERNS.md), not by market research — these are known gaps in a working product.

**Must have (table stakes — data integrity and trust):**
- Duplicate active fast guard — `POST /api/fasts` returns HTTP 409 if one is already active; `StartFast.vue` disables start button with clear message
- Error catch blocks in `FastDetail.vue` — `endFast`, `submitLog`, `confirmDeleteFast`, `submitMeal` currently swallow errors silently
- Weight entry edit — `PUT /api/weight/{id}` backend endpoint + inline tap-to-edit row in `WeightView.vue`
- Weight entry delete — `DELETE /api/weight/{id}` backend endpoint + delete with confirmation in `WeightView.vue`
- History pagination — "Charger plus" load-more button replacing the hard-capped `getFasts(0, 100)` call
- Fix `avg_duration_hours` always null in weekly stats — backend CRUD fix, UI already renders it when non-null

**Should have (consistency and polish):**
- Toast notification system (`useToast` composable + `ToastContainer.vue`) — unifies all error and success feedback across views
- Backend type filter for fasts list — required for pagination to work correctly alongside the existing client-side filter
- Pagination count indicator ("X sur Y") — requires a count endpoint or count-in-response

**Defer to v2+:**
- Optimistic UI on log submission — meaningful only after core reliability is resolved
- Stale localStorage TTL for offline cache — nice to have, not blocking primary flows
- Global Pinia store — explicitly deferred; per-view fetch with module-level reactive refs for shared state is sufficient

### Architecture Approach

The existing layered architecture (Vue views → composables → API client → FastAPI routes → CRUD → PostgreSQL) is sound and requires no structural changes. All changes are additions within existing files or new files placed in the correct existing directories. The build order defined in ARCHITECTURE.md (7 groups, each independent within but sequentially dependent across) is the critical output: it prevents a class of errors where a fix written in the wrong order either gets tested against broken behavior or depends on infrastructure that does not yet exist.

**Major components and their changes:**
1. `backend/database.py` — remove hardcoded credential fallback; replace with `pydantic-settings` `BaseSettings`
2. `backend/crud.py` — fix `get_weekly_summary` N+1 (32 queries → 1), fix `avg_duration_hours` computation, fix `get_current_fast` nullable predicate, replace Python-side AVG with `func.avg()` SQL aggregate
3. `backend/main.py` — add active-fast guard in `create_fast` route; add `PUT`/`DELETE` `/api/weight/{id}` routes
4. `backend/schemas.py` — add `max_length` to request-only schemas (`*Create`, `*Update`); do NOT add to response schemas
5. `frontend/src/composables/useToast.ts` (new) — module-level reactive toast state, no Pinia required
6. `frontend/src/components/ToastContainer.vue` (new) — renders active toasts; mounted in `App.vue`
7. `frontend/src/composables/useTimer.ts` — fix lifecycle issue by moving composable call to synchronous setup using `watchEffect`
8. `frontend/src/views/FastDetail.vue` — add `catch` blocks with `showToast()` calls to all async mutation functions

### Critical Pitfalls

1. **`useTimer` async lifecycle bug: fix the root cause, not the symptom** — the composable is called after an `await` inside `async onMounted`, breaking Vue's composable contract. The fix is to call `useTimer` synchronously during component setup using a `watchEffect` that reacts to the fetched fast ref. Any fix that only guards the `start()` call or adds a try/catch to `onMounted` will leave the interval leak intact.

2. **Credential removal that looks done but isn't** — removing the hardcoded fallback from `database.py` is step 1 of 3. Step 2 is rotating the production database password. Step 3 is scrubbing git history (`git filter-repo` or BFG). Skipping steps 2-3 means the credential is still accessible to anyone with repo access.

3. **Mock-only tests that pass while SQL bugs persist** — the existing test pattern in `test_meal_recommendations.py` stubs `crud.*` functions. If extended without a second real-database test layer, the N+1 bug and `avg_duration_hours` null bug will both survive a green test suite. Route handler tests (mocked) and CRUD integration tests (real Postgres test DB) are both required.

4. **N+1 fix with Python-side batching instead of SQL aggregation** — the tempting intermediate fix (batch 4 queries instead of 32) still loads all qualifying rows into Python memory. The correct fix uses `GROUP BY date_trunc('week', started)` with `func.count()` and `func.avg()` in SQLAlchemy, computing everything in one or two SQL round-trips.

5. **`max_length` added to response schemas causes 500s on existing data** — the codebase has pre-existing rows with unbounded text fields. Adding `Field(max_length=500)` to the base `Fast` schema used as `response_model` will trigger `ResponseValidationError` 500s when returning those rows. Constraints must go only on `*Create` and `*Update` request schemas, not response schemas.

## Implications for Roadmap

Based on research, the build order from ARCHITECTURE.md defines the natural phase structure. There are 7 groups; they map cleanly to 4-5 roadmap phases:

### Phase 1: Security Hardening
**Rationale:** Must be first. The credential in git history is a security issue that requires immediate action; all subsequent work on the codebase is done with the assumption that credentials are managed correctly. Password rotation must happen before any other deployment.
**Delivers:** Removed hardcoded credential, pydantic-settings startup validation, CORS methods restricted to explicit list, `max_length` on all request schemas, `seed.run()` and `create_all` calls removed from startup
**Addresses:** All security mistakes identified in PITFALLS.md
**Avoids:** Pitfall 3 (credential rotation without history scrub), Pitfall 6 (max_length on response schemas)

### Phase 2: Backend Correctness and Query Optimization
**Rationale:** Fix known bugs before writing tests — tests written against broken behavior encode the bugs. The active-fast guard, nullable predicate fix, N+1 rewrite, and avg_duration_hours fix are all pure backend changes with no frontend dependency.
**Delivers:** HTTP 409 on duplicate active fast, correct `get_current_fast` nullable filter, N+1 in `get_weekly_summary` replaced with single SQL aggregate, `avg_duration_hours` populated, Python-side AVG in `get_stats` replaced with `func.avg()`, new `PUT`/`DELETE /api/weight/{id}` endpoints
**Addresses:** All P1 backend features from FEATURES.md
**Avoids:** Pitfall 5 (N+1 partial fix), Pitfall 2 (tests written before bugs are fixed)

### Phase 3: Backend Test Coverage
**Rationale:** Tests are written after the fixes they cover, against correct behavior. Two-layer strategy: mock-based route tests (HTTP contract) + real Postgres integration tests (CRUD logic). The existing `test_meal_recommendations.py` establishes the mock pattern; new test files extend it.
**Delivers:** `test_fasts.py`, `test_stats.py`, `test_weight.py`; integration tests for `get_weekly_summary`, `get_stats`, `get_current_fast` against real Postgres test DB
**Uses:** pytest-asyncio 1.3.0, pytest-cov 7.0.0
**Avoids:** Pitfall 2 (mock-only tests that miss SQL bugs)

### Phase 4: Frontend Error Handling and Infrastructure
**Rationale:** Toast infrastructure must land before catch blocks — adding catch blocks without a toast system means inconsistent surfaces. `useTimer` lifecycle fix is independent but belongs here as a bug fix. Both frontend groups (infrastructure, then error handling) are in this phase.
**Delivers:** `useToast.ts` composable, `ToastContainer.vue` mounted in `App.vue`, catch blocks in `FastDetail.vue` (endFast, submitLog, confirmDeleteFast, submitMeal), `useTimer` lifecycle fix in Dashboard.vue and FastDetail.vue, `alert()` replacement in `WeightView.vue`
**Addresses:** All error handling features from FEATURES.md
**Avoids:** Pitfall 1 (useTimer async lifecycle), Pitfall 4 (catch blocks that reset loading state without user feedback)

### Phase 5: UI Completeness and Frontend Tests
**Rationale:** UI completeness work (weight edit/delete inline UI, history pagination) depends on Phase 2 backend endpoints. Frontend tests are written last, against the fixed behavior including the useTimer fix.
**Delivers:** Inline weight edit/delete rows in `WeightView.vue`, "Charger plus" load-more in `HistoryView.vue`, `useTimer.test.ts`, `FastDetail.test.ts`, `CircularProgress.test.ts`
**Uses:** vitest 4.0.17, @vue/test-utils 2.4.6, happy-dom
**Addresses:** History pagination and weight CRUD features from FEATURES.md

### Phase Ordering Rationale

- Security before everything: credential rotation requires a production deployment; this affects the dev environment assumptions for all subsequent work
- Backend bugs before tests: the two-layer test strategy requires correct behavior to test against; tests written before the N+1 fix is done are worse than useless — they encode wrong behavior
- Toast infrastructure before catch blocks: catch blocks that call `showToast()` require the composable to exist; landing them in the wrong order creates dead references
- Backend endpoints before frontend UI: weight edit/delete UI in Phase 5 requires the `PUT`/`DELETE /api/weight/{id}` endpoints from Phase 2

### Research Flags

Phases that follow well-documented patterns (no additional research needed):
- **Phase 1 (Security):** All issues are known and targeted; pydantic-settings and git history scrubbing are well-documented
- **Phase 2 (Backend Correctness):** SQLAlchemy GROUP BY aggregation is well-documented; the specific bugs are identified
- **Phase 3 (Backend Tests):** FastAPI testing patterns are well-documented; existing `test_meal_recommendations.py` sets the pattern
- **Phase 4 (Frontend Error Handling):** Vue 3 composable lifecycle rules are well-documented; module-level reactive refs for shared toast state is a standard pattern
- **Phase 5 (Frontend Tests):** Vitest + Vue Test Utils patterns for composable lifecycle testing are documented

One area needing validation during Phase 3: the two-layer test strategy requires a separate `fasting_test` PostgreSQL database. Confirm this can be created on `postgresql.host` before Phase 3 begins. If not, the integration test layer may need to use a test schema prefix instead.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified against PyPI and official package pages; compatibility requirements confirmed |
| Features | HIGH | Based on direct codebase audit (CONCERNS.md) — these are known defects, not speculative features |
| Architecture | HIGH | Based on direct codebase analysis; all patterns reference official FastAPI, Vue 3, and SQLAlchemy docs |
| Pitfalls | HIGH | Grounded in known codebase issues; each pitfall has a verified "looks done but isn't" failure mode |

**Overall confidence:** HIGH

### Gaps to Address

- **Test database provisioning:** The integration test strategy requires a `fasting_test` database on `postgresql.host`. This must be confirmed before Phase 3 begins. If the user cannot create a new database on that host, an alternative approach (test schema prefix, or transaction rollback per test without a separate DB) must be selected.
- **Git history scrub coordination:** Scrubbing git history requires force-pushing all branches and all collaborators re-cloning. If this is a solo project, it is straightforward. Confirm no other contributors have clones before running `git filter-repo`.
- **`slowapi` maintenance velocity:** `slowapi 0.1.9` has low release cadence (last release 2024). It is stable but should be evaluated against nginx-level rate limiting if the app ever moves to a more public deployment profile.

## Sources

### Primary (HIGH confidence)
- `.planning/codebase/CONCERNS.md` — direct codebase audit; all known defects
- [FastAPI Settings documentation](https://fastapi.tiangolo.com/advanced/settings/) — pydantic-settings recommendation
- [FastAPI Testing documentation](https://fastapi.tiangolo.com/tutorial/testing/) — dependency override pattern
- [FastAPI Error Handling](https://fastapi.tiangolo.com/tutorial/handling-errors/) — HTTPException patterns
- [pytest-asyncio 1.3.0 PyPI](https://pypi.org/project/pytest-asyncio/) — version and Python compat
- [pydantic-settings 2.13.1 PyPI](https://pypi.org/project/pydantic-settings/) — version confirmed
- [pytest-cov 7.0.0 PyPI](https://pypi.org/project/pytest-cov/) — version confirmed
- [Vitest 4.0.17 official site](https://vitest.dev/) — version confirmed, Vite >=6 requirement
- [Vue.js Testing Guide](https://vuejs.org/guide/scaling-up/testing) — Vitest + @vue/test-utils recommendation
- [Vue Test Utils Getting Started](https://test-utils.vuejs.org/guide/) — @vue/test-utils v2 for Vue 3
- [Vue 3 composables docs](https://vuejs.org/guide/reusability/composables#conventions-and-best-practices) — lifecycle rules after async
- [Pydantic official docs — Validators](https://docs.pydantic.dev/latest/concepts/validators/) — field validation
- [SQLAlchemy 2.x docs](https://docs.sqlalchemy.org/) — GROUP BY aggregation

### Secondary (MEDIUM confidence)
- [slowapi GitHub](https://github.com/laurentS/slowapi) — 0.1.9 latest, low release cadence confirmed
- [Pagination vs Infinite Scroll vs Load More](https://ashishmisal.medium.com/pagination-vs-infinite-scroll-vs-load-more-data-loading-ux-patterns-in-react-53534e23244d) — load-more pattern rationale
- [NN/g Error Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/) — inline error banner approach
- [Mastering Vue 3 Composables Testing with Vitest](https://dylanbritz.dev/writing/testing-vue-composables-lifecycle/) — lifecycle test patterns
- [Vue Mastery: Async Without Await](https://www.vuemastery.com/blog/coding-better-composables-5-of-5/) — useTimer fix approach
- [Best Practices for Error Handling in Vue Composables](https://alexop.dev/posts/best-practices-for-error-handling-in-vue-composables/) — reactive error ref pattern

---
*Research completed: 2026-03-09*
*Ready for roadmap: yes*
