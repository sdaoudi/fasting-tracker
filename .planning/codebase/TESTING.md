# Testing Patterns

**Analysis Date:** 2026-03-09

## Test Framework

**Backend Runner:**
- pytest 8.3.3
- Config: no `pytest.ini` or `pyproject.toml` — pytest uses defaults
- HTTP test client: `fastapi.testclient.TestClient` (synchronous WSGI wrapper)
- HTTP client library: `httpx 0.27.2` (required by FastAPI TestClient)

**Frontend Runner:**
- Not configured. No `vitest.config.*`, `jest.config.*`, or test-related dev dependencies exist in `frontend/package.json`.
- Frontend is untested.

**Run Commands:**
```bash
# Backend tests (from /backend directory)
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest test_meal_recommendations.py   # Run specific file
pytest -k "TestSuggestMeals"    # Run specific class
```

## Test File Organization

**Location:**
- Co-located with source in `backend/` directory
- Single test file: `backend/test_meal_recommendations.py`
- No dedicated `tests/` subdirectory

**Naming:**
- File: `test_<feature>.py` — `test_meal_recommendations.py`
- Classes: `Test<Feature>` — `TestSuggestMeals`, `TestCategories`, `TestGetRecommendation`, `TestRecommendationLogic`
- Methods: `test_<scenario>` — `test_suggest_returns_list`, `test_not_found`, `test_parse_duration_hours`

**Structure:**
```
backend/
├── test_meal_recommendations.py   # Only test file
└── ... (source files)
```

## Test Structure

**Suite Organization:**
```python
# Helper factories at module level (not fixtures)
def make_recommendation(**overrides): ...
def make_fast(**overrides): ...

# pytest fixtures
@pytest.fixture
def mock_db(): ...

@pytest.fixture
def client(mock_db): ...

# Test classes group by endpoint
class TestSuggestMeals:
    def test_suggest_returns_list(self, client, mock_db): ...
    def test_suggest_with_fast_id(self, client, mock_db): ...

class TestRecommendationLogic:
    def test_parse_duration_hours(self): ...  # pure unit tests, no fixtures needed
```

**Patterns:**
- Setup via pytest fixtures with dependency injection
- `client` fixture depends on `mock_db` fixture
- Pure logic tests (no HTTP) use no fixtures — direct function import
- Each test is self-contained: arrange objects, patch crud, call endpoint, assert response

## Mocking

**Framework:** `unittest.mock` — `MagicMock`, `patch`

**Patterns:**
```python
# Dependency override for DB (injected at fixture level)
@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()   # Always cleaned up

# CRUD function patching per-test with context manager
with patch("crud.get_meal_suggestions", return_value=[rec]):
    resp = client.get("/api/meal-recommendations/suggest?fast_duration=48h")
```

**Model mocking with factory functions:**
```python
def make_recommendation(**overrides):
    defaults = {
        "id": 1,
        "name": "Bouillon d'os",
        "category": "rupture_jeune",
        # ... all fields
    }
    defaults.update(overrides)
    rec = MagicMock(spec=MealRecommendation)   # spec constrains to actual model attrs
    for k, v in defaults.items():
        setattr(rec, k, v)
    return rec
```

**What to Mock:**
- Database session (`get_db` dependency)
- CRUD layer functions (`crud.*`) when testing route handlers
- SQLAlchemy model instances via `MagicMock(spec=ModelClass)`

**What NOT to Mock:**
- Pure utility functions tested directly (e.g., `_parse_duration_hours`, `DIGESTIBILITY_ORDER`)
- FastAPI routing and request/response serialization — those are tested via TestClient

## Fixtures and Factories

**Test Data:**
```python
# Factory functions (not pytest fixtures) — overrideable defaults pattern
def make_recommendation(**overrides):
    defaults = { "id": 1, "name": "Bouillon d'os", ... }
    defaults.update(overrides)
    rec = MagicMock(spec=MealRecommendation)
    for k, v in defaults.items():
        setattr(rec, k, v)
    return rec

# Usage with override
rec = make_recommendation(id=2, name="Soupe légère")
rec = make_recommendation(phase="jour_1", category="reprise_progressive")
```

**Location:**
- Factory functions defined at module level in the same test file (no shared fixtures directory)

## Coverage

**Requirements:** None enforced — no coverage configuration or thresholds.

**View Coverage:**
```bash
# Install coverage if needed
pip install pytest-cov

pytest --cov=. --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- `TestRecommendationLogic` tests pure functions directly (no HTTP, no DB)
- Imports internal symbols: `from crud import _parse_duration_hours`, `from crud import DIGESTIBILITY_ORDER`
- Asserts return values with `assert func(input) == expected`

**Integration Tests:**
- `TestSuggestMeals`, `TestCategories`, `TestGetRecommendation` test full HTTP request/response cycle
- Use `TestClient` against the real FastAPI app with mocked DB and CRUD layer
- Assert HTTP status codes and JSON response shape

**E2E Tests:**
- Not used.

**Frontend Tests:**
- Not used — no test framework installed.

## Common Patterns

**Async Testing:**
- Not applicable — all backend tests are synchronous via `TestClient`
- FastAPI async routes are tested synchronously via TestClient (it handles the event loop)

**Error Testing:**
```python
def test_not_found(self, client, mock_db):
    with patch("crud.get_meal_recommendation", return_value=None):
        resp = client.get("/api/meal-recommendations/999")
    assert resp.status_code == 404
```

**Successful response testing:**
```python
def test_suggest_returns_list(self, client, mock_db):
    rec = make_recommendation()
    with patch("crud.get_meal_suggestions", return_value=[rec]):
        resp = client.get("/api/meal-recommendations/suggest?fast_duration=48h")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Bouillon d'os"
```

**Asserting function call args:**
```python
def test_suggest_with_fast_id(self, client, mock_db):
    rec = make_recommendation(id=2, name="Soupe légère")
    with patch("crud.get_meal_suggestions", return_value=[rec]) as mock_fn:
        resp = client.get("/api/meal-recommendations/suggest?fast_id=1")
    assert resp.status_code == 200
    mock_fn.assert_called_once()
    call_kwargs = mock_fn.call_args
    assert call_kwargs.kwargs.get("fast_id") == 1 or call_kwargs[1].get("fast_id") == 1
```

## Coverage Gaps

**Untested endpoints (no tests exist for):**
- All fasts CRUD: `GET /api/fasts`, `GET /api/fasts/current`, `POST /api/fasts`, `PUT /api/fasts/{id}`, `DELETE /api/fasts/{id}`
- Daily logs: `GET /api/fasts/{id}/logs`, `POST /api/fasts/{id}/logs`
- Meals: `GET /api/fasts/{id}/meals`, `POST /api/fasts/{id}/meals`, `GET /api/meals/recent`
- Weight: `GET /api/weight`, `POST /api/weight`, `GET /api/weight/trend`
- Stats: `GET /api/stats`, `GET /api/stats/weekly`

**Untested CRUD logic:**
- `crud.py` functions: `get_fasts`, `get_fast`, `get_current_fast`, `create_fast`, `update_fast`, `delete_fast`
- `crud.py`: `get_weight_history`, `create_weight` (upsert logic untested)
- `crud.py`: `get_stats` (complex aggregation), `get_weekly_summary`

**Frontend:**
- Zero test coverage across all Vue components, composables, and the API client (`frontend/src/api/client.ts`)

---

*Testing analysis: 2026-03-09*
