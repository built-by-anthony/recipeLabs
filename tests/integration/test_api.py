from fastapi.testclient import TestClient
from recipeLabs.main import app
from unittest.mock import patch, MagicMock
import json
from recipeLabs.database import get_db

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_import_recipe(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with open("tests/fixtures/themealdb_carbinara.json") as f:
        fixture_data = json.load(f)
    with patch("recipeLabs.api.recipes.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = fixture_data
        mock_get.return_value = mock_response
        response = client.post("/recipes/import", json={"meal_id": "52982"})
        assert response.status_code == 200
    app.dependency_overrides.clear()
