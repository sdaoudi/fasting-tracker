# Stack Research

**Domain:** Quality hardening — testing, error handling, security for FastAPI + Vue 3 TypeScript
**Researched:** 2026-03-09
**Confidence:** HIGH (all versions verified against PyPI and official sources)

## Context

This is an additive hardening milestone on an existing, working app. The stack is already locked:
- Backend: FastAPI 0.115.0 + SQLAlchemy 2.0.35 + Pydantic 2.9.2 + Python 3.12
- Frontend: Vue 3.5.25 + Vite 7.3.1 + TypeScript + Tailwind v4

This research covers only the NEW libraries needed for quality and security — not the existing app stack.

---

## Recommended Stack

### Backend Testing

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| pytest | 8.3.3 (already installed) | Test runner | Already in requirements.txt; no change needed |
| pytest-asyncio | 1.3.0 | Async test support | FastAPI routes are async; without this, async test functions silently don't run properly. Use `asyncio_mode = "auto"` in `pyproject.toml` to avoid per-test decorators |
| httpx | 0.27.2 (already installed) | HTTP client for TestClient | Already in requirements.txt; FastAPI's `TestClient` wraps httpx under the hood |
| pytest-cov | 7.0.0 | Coverage measurement | The standard pytest coverage plugin; generates HTML reports identifying untested paths. Requires `coverage>=7.10.6` |

**Why pytest-asyncio and not anyio:** The existing app uses plain asyncio (no trio). `anyio` adds complexity without benefit here. `asyncio_mode = "auto"` in pytest config is the simplest path for a single-async-library project (confirmed in pytest-asyncio 1.3.0 docs).

**Why TestClient over AsyncClient for most tests:** FastAPI's `TestClient` runs the ASGI app in a thread with synchronous test functions — simpler fixtures, no `await` boilerplate. Use `httpx.AsyncClient` only for tests that explicitly need async context (e.g., testing WebSocket routes — not present here).

### Backend Security

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| pydantic-settings | 2.13.1 | Env var management with type validation | FastAPI's official recommendation for settings. Replaces hardcoded `DATABASE_URL` fallback in `database.py`. `BaseSettings` reads env vars at startup, validates types, raises `ValidationError` if required vars are absent — better than a silent wrong default |
| slowapi | 0.1.9 | Request rate limiting | Directly ports `flask-limiter` semantics to FastAPI/Starlette. Single decorator per route. In-memory store is sufficient for a single-process personal app. No Redis dependency needed |

**Why pydantic-settings over python-dotenv directly:** `python-dotenv` just loads a `.env` file into `os.environ`; you still call `os.getenv()` with no type checking. `pydantic-settings` wraps dotenv AND validates types AND raises clear startup errors. It is a first-class FastAPI recommendation.

**Why slowapi over fastapi-limiter:** `fastapi-limiter` requires Redis, which is overkill for a single-user personal app. `slowapi` works with in-memory state and needs zero infrastructure. The tradeoff: `slowapi` doesn't persist rate counts across restarts, which is acceptable here.

### Frontend Testing

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| vitest | 4.0.17 | Test runner | Shares Vite config — zero additional config for a Vite 7 project. Requires Vite >=6 (satisfied). Dramatically faster than Jest for ESM/TypeScript because it skips the Babel transform step |
| @vue/test-utils | 2.4.6 | Vue component and composable mounting | Official Vue 3 testing library. Required for mounting components, triggering events, inspecting props, and testing lifecycle hooks (the `useTimer` bug specifically requires lifecycle testing) |
| happy-dom | latest (vitest peer) | DOM environment for tests | Faster than jsdom; sufficient for DOM interactions in a component test suite. No browser binary needed. Vitest recommends it as the default environment |

**Why vitest over jest:** The existing project uses Vite 7 with native ESM. Jest requires `babel-jest` + `jest-environment-jsdom` + transform config for `.vue` files — a large configuration surface. Vitest picks up the existing `vite.config.ts` plugins automatically. The Vue team recommends Vitest for Vite-based projects.

**Why @vue/test-utils and NOT @testing-library/vue:** `@testing-library/vue` is built on top of `@vue/test-utils` and adds opinionated query helpers. It has known issues with async Suspense components and adds a layer of indirection. For testing composables directly (the primary need here: `useTimer`, `useOfflineStorage`), `@vue/test-utils` `withSetup` pattern is simpler and more explicit.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| coverage | >=7.10.6 | Coverage engine (pytest-cov dependency) | Install alongside pytest-cov; generates `.coverage` data file |

---

## Installation

### Backend additions

```bash
cd backend
pip install pytest-asyncio==1.3.0 pytest-cov==7.0.0 pydantic-settings==2.13.1 slowapi==0.1.9
```

Add to `backend/requirements.txt`:
```
pytest-asyncio==1.3.0
pytest-cov==7.0.0
pydantic-settings==2.13.1
slowapi==0.1.9
```

Add `backend/pytest.ini` or `backend/pyproject.toml` section:
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Frontend additions

```bash
cd frontend
npm install -D vitest@^4.0.17 @vue/test-utils@^2.4.6 happy-dom
```

Add to `vite.config.ts` (under existing `defineConfig`):
```ts
test: {
  environment: 'happy-dom',
  globals: true,
}
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| pydantic-settings | python-dotenv only | Never for a FastAPI app — dotenv lacks type validation and startup failure guarantees |
| slowapi | fastapi-limiter | Only if you already have Redis in the stack (e.g., for caching or queues) |
| slowapi | nginx-level rate limiting | Better for high-traffic public services; nginx config is outside this app's control (Dokploy manages it) |
| pytest-asyncio | anyio / pytest-anyio | Only if adding trio or other async backends alongside asyncio |
| vitest | jest | Never for a Vite-based Vue project — config overhead is not worth it |
| @vue/test-utils | @testing-library/vue | Acceptable if team prefers user-centric query semantics; avoid for composable unit tests |
| happy-dom | jsdom | jsdom is more battle-tested but 3-5x slower; acceptable if tests fail in happy-dom |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| SQLite in-memory for tests | The existing app uses PostgreSQL-specific types: `ARRAY(Text)` and `JSONB` (in `meal_recommendations`). SQLite does not support these. Tests against SQLite would pass but production code would fail | Use the actual PostgreSQL database with a test schema prefix, or override the DB URL to a separate test DB via `DATABASE_URL` env var in test config |
| `python-decouple` | Adds a third config-reading library when `pydantic-settings` already does the same job with type validation baked in | `pydantic-settings` |
| `pytest-mock` / `unittest.mock` as primary strategy | Mocking the database hides real SQL bugs (the N+1 issue and `avg_duration_hours` None bug would both survive a mocked test suite) | Real database fixtures with transaction rollback per test |
| `bandit` (security linter) for this milestone | Useful for CI pipelines on large codebases; the specific security issues here (hardcoded credentials, missing field length validators) are known and targeted — a linter scan adds noise without resolving the identified issues | Fix the specific known issues directly |

---

## Stack Patterns by Variant

**For backend tests that need database isolation:**
- Use `app.dependency_overrides[get_db]` to inject a test session
- Wrap each test in a transaction that is rolled back on teardown
- Point `DATABASE_URL` at a dedicated `fasting_test` database (same PostgreSQL server, separate DB)
- Do NOT use SQLite — `ARRAY(Text)` and `JSONB` columns will break

**For testing the `useTimer` composable lifecycle bug:**
- Use `@vue/test-utils` `mount()` with a wrapper component (not direct composable call)
- Test rapid mount/unmount via `wrapper.unmount()` + re-mount cycle
- Assert no interval leaks via `vi.useFakeTimers()` + `vi.runAllTimers()`

**For the `endFast` / `submitLog` error handling fixes:**
- Add try/catch blocks that set a reactive `error` ref and display it in the template
- Test error paths by mocking the API module with `vi.mock('../api/client')`

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| pytest-asyncio 1.3.0 | pytest 8.x, Python 3.10-3.14 | Confirmed — requires Python >=3.10; the project uses 3.12 |
| pydantic-settings 2.13.1 | Pydantic 2.x | Must be Pydantic v2 (the project already uses 2.9.2) — do NOT use pydantic-settings 1.x |
| vitest 4.0.17 | Vite >=6.0, Node >=20 | Project uses Vite 7.3.1 and Node 22 — both satisfied |
| @vue/test-utils 2.4.6 | Vue 3.x | Targets Vue 3 only; not compatible with Vue 2 |
| slowapi 0.1.9 | FastAPI / Starlette any recent version | Low maintenance velocity (last release 2024) but stable API; no breaking changes expected |

---

## Sources

- [FastAPI Settings documentation](https://fastapi.tiangolo.com/advanced/settings/) — pydantic-settings recommendation (HIGH confidence, official)
- [pytest-asyncio 1.3.0 PyPI](https://pypi.org/project/pytest-asyncio/) — version and Python compat confirmed (HIGH confidence, official)
- [pydantic-settings 2.13.1 PyPI](https://pypi.org/project/pydantic-settings/) — version confirmed (HIGH confidence, official)
- [pytest-cov 7.0.0 PyPI](https://pypi.org/project/pytest-cov/) — version confirmed, coverage >=7.10.6 requirement (HIGH confidence, official)
- [Vitest 4.0.17 official site](https://vitest.dev/) — version confirmed, Vite >=6 requirement (HIGH confidence, official)
- [Vue.js Testing Guide](https://vuejs.org/guide/scaling-up/testing) — Vitest + @vue/test-utils recommendation for Vite projects (HIGH confidence, official)
- [Vue Test Utils Getting Started](https://test-utils.vuejs.org/guide/) — @vue/test-utils v2 for Vue 3 (HIGH confidence, official)
- [slowapi GitHub](https://github.com/laurentS/slowapi) — 0.1.9 latest, low release cadence confirmed (MEDIUM confidence — library is stable but maintenance-light)
- [FastAPI Testing Database docs](https://fastapi.tiangolo.com/advanced/testing-database/) — dependency override pattern (HIGH confidence, official)
- [pytest-asyncio auto mode docs](https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html) — `asyncio_mode = "auto"` recommended for single-async-library projects (HIGH confidence, official)

---
*Stack research for: FastAPI + Vue 3 quality hardening (testing, error handling, security)*
*Researched: 2026-03-09*
