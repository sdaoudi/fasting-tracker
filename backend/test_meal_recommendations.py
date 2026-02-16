"""Tests for the meal recommendations API endpoints."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from database import get_db
from models import MealRecommendation, Fast


# ── Fixtures ──

def make_recommendation(**overrides):
    defaults = {
        "id": 1,
        "name": "Bouillon d'os",
        "category": "rupture_jeune",
        "fast_duration": "48h",
        "phase": None,
        "description": "Bouillon d'os léger",
        "ingredients": ["os de boeuf", "eau", "sel"],
        "macros": {"calories": 40, "protein": 6, "carbs": 0, "fat": 1},
        "preparation_time": 15,
        "difficulty": "facile",
        "tips": "Boire tiède",
        "digestibility": "très_facile",
        "meal_timing": "dejeuner",
        "created_at": datetime(2026, 1, 1),
    }
    defaults.update(overrides)
    rec = MagicMock(spec=MealRecommendation)
    for k, v in defaults.items():
        setattr(rec, k, v)
    return rec


def make_fast(**overrides):
    defaults = {
        "id": 1, "type": "48h", "started": datetime(2026, 2, 14),
        "ended": None, "target_hours": 48, "completed": False,
    }
    defaults.update(overrides)
    fast = MagicMock(spec=Fast)
    for k, v in defaults.items():
        setattr(fast, k, v)
    return fast


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Tests: GET /api/meal-recommendations/suggest ──

class TestSuggestMeals:
    def test_suggest_returns_list(self, client, mock_db):
        rec = make_recommendation()
        with patch("crud.get_meal_suggestions", return_value=[rec]):
            resp = client.get("/api/meal-recommendations/suggest?fast_duration=48h")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "Bouillon d'os"
        assert data[0]["category"] == "rupture_jeune"

    def test_suggest_with_fast_id(self, client, mock_db):
        rec = make_recommendation(id=2, name="Soupe légère")
        with patch("crud.get_meal_suggestions", return_value=[rec]) as mock_fn:
            resp = client.get("/api/meal-recommendations/suggest?fast_id=1")
        assert resp.status_code == 200
        mock_fn.assert_called_once()
        call_kwargs = mock_fn.call_args
        assert call_kwargs.kwargs.get("fast_id") == 1 or call_kwargs[1].get("fast_id") == 1

    def test_suggest_with_meal_timing(self, client, mock_db):
        rec = make_recommendation(meal_timing="petit_dejeuner")
        with patch("crud.get_meal_suggestions", return_value=[rec]):
            resp = client.get("/api/meal-recommendations/suggest?meal_timing=petit_dejeuner")
        assert resp.status_code == 200
        assert resp.json()[0]["meal_timing"] == "petit_dejeuner"

    def test_suggest_empty(self, client, mock_db):
        with patch("crud.get_meal_suggestions", return_value=[]):
            resp = client.get("/api/meal-recommendations/suggest")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_suggest_with_phase(self, client, mock_db):
        rec = make_recommendation(phase="jour_1", category="reprise_progressive")
        with patch("crud.get_meal_suggestions", return_value=[rec]):
            resp = client.get("/api/meal-recommendations/suggest?phase=jour_1")
        assert resp.status_code == 200
        assert resp.json()[0]["phase"] == "jour_1"


# ── Tests: GET /api/meal-recommendations/categories ──

class TestCategories:
    def test_returns_categories(self, client, mock_db):
        cats = [{"category": "rupture_jeune", "count": 8}, {"category": "repas_fenetre", "count": 5}]
        with patch("crud.get_meal_recommendation_categories", return_value=cats):
            resp = client.get("/api/meal-recommendations/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["category"] == "rupture_jeune"
        assert data[0]["count"] == 8


# ── Tests: GET /api/meal-recommendations/{id} ──

class TestGetRecommendation:
    def test_returns_recommendation(self, client, mock_db):
        rec = make_recommendation()
        with patch("crud.get_meal_recommendation", return_value=rec):
            resp = client.get("/api/meal-recommendations/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["macros"]["calories"] == 40
        assert data["ingredients"] == ["os de boeuf", "eau", "sel"]

    def test_not_found(self, client, mock_db):
        with patch("crud.get_meal_recommendation", return_value=None):
            resp = client.get("/api/meal-recommendations/999")
        assert resp.status_code == 404


# ── Tests: Smart recommendation logic ──

class TestRecommendationLogic:
    def test_parse_duration_hours(self):
        from crud import _parse_duration_hours
        assert _parse_duration_hours("16h") == 16
        assert _parse_duration_hours("48h") == 48
        assert _parse_duration_hours("72h") == 72
        assert _parse_duration_hours("16:8") == 16
        assert _parse_duration_hours("OMAD") == 23
        assert _parse_duration_hours("7j+") == 168
        assert _parse_duration_hours("unknown") is None

    def test_digestibility_sort_order(self):
        from crud import DIGESTIBILITY_ORDER
        assert DIGESTIBILITY_ORDER["très_facile"] < DIGESTIBILITY_ORDER["facile"]
        assert DIGESTIBILITY_ORDER["facile"] < DIGESTIBILITY_ORDER["moyen"]
