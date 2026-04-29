import json
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from recipeLabs.database import get_db
from recipeLabs.main import app
from recipeLabs.models import CookLog, Recipe

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


def test_list_recipes(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    recipe = Recipe(name="Test Pasta")
    db_session.add(recipe)
    db_session.commit()

    response = client.get("/recipes")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Pasta"
    app.dependency_overrides.clear()


def test_list_recipes_filter_by_rating(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    recipe_1 = Recipe(name="Test Pasta")
    db_session.add(recipe_1)
    db_session.commit()

    cook_1 = CookLog(
        recipe_id=recipe_1.id, cooked_at="2024-01-02", rating=4, cooked_by="Test User"
    )
    db_session.add(cook_1)
    db_session.commit()

    recipe_2 = Recipe(name="Test Potato")
    db_session.add(recipe_2)
    db_session.commit()

    cook_2 = CookLog(
        recipe_id=recipe_2.id, cooked_at="2024-01-02", rating=2, cooked_by="Test User"
    )
    db_session.add(cook_2)
    db_session.commit()

    response = client.get("/recipes", params={"min_rating": 3})

    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Pasta"
    app.dependency_overrides.clear()


def test_list_recipes_filter_by_last_cooked_date(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    recipe_1 = Recipe(name="Test Pasta")
    db_session.add(recipe_1)
    db_session.commit()

    cook_1 = CookLog(
        recipe_id=recipe_1.id, cooked_at="2025-01-02", rating=4, cooked_by="Test User"
    )
    db_session.add(cook_1)
    db_session.commit()

    recipe_2 = Recipe(name="Test Potato")
    db_session.add(recipe_2)
    db_session.commit()

    cook_2 = CookLog(
        recipe_id=recipe_2.id, cooked_at="2024-01-02", rating=2, cooked_by="Test User"
    )
    db_session.add(cook_2)
    db_session.commit()

    response = client.get("/recipes", params={"last_cooked_date": "2025-01-01"})

    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Pasta"
    app.dependency_overrides.clear()


def test_get_single_recipe(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    recipe_1 = Recipe(name="Test Pasta")
    db_session.add(recipe_1)
    db_session.commit()

    recipe_2 = Recipe(name="Test Potato")
    db_session.add(recipe_2)
    db_session.commit()

    response = client.get(f"/recipes/{recipe_1.id}")
    assert response.json()["name"] == "Test Pasta"
    app.dependency_overrides.clear()


def test_manual_recipe_import(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    response = client.post(
        "/recipes",
        json={
            "name": "Homemade Pizza",
            "cuisine": "Italian",
            "prep_time": 20,
            "cook_time": 15,
            "total_time": 35,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Homemade Pizza"
    assert response.json()["prep_time"] == 20
    assert response.json()["cook_time"] == 15
    assert response.json()["total_time"] == 35
    app.dependency_overrides.clear()


def test_delete_recipe(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    # create a recipe first
    recipe = Recipe(name="Test Recipe")
    db_session.add(recipe)
    db_session.commit()

    # create a cook log for that recipe
    cook = CookLog(
        recipe_id=recipe.id, cooked_at="2024-01-02", rating=4, cooked_by="Test User"
    )

    db_session.add(cook)
    db_session.commit()

    cook_id = cook.id

    response = client.delete(f"/recipes/{recipe.id}")
    deleted_recipe = db_session.query(Recipe).filter_by(id=recipe.id).first()
    deleted_cook = db_session.query(CookLog).filter_by(id=cook_id).first()

    assert deleted_recipe is None
    assert deleted_cook is None
    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_cook_log(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    recipe = Recipe(name="Test Pasta")
    db_session.add(recipe)
    db_session.commit()

    response = client.post(
        f"/recipes/{recipe.id}/cooks",
        json={
            "cooked_at": "2024-01-02",
            "rating": 3,
            "notes": "more salt",
            "cooked_by": "Test User",
        },
    )

    assert response.status_code == 200
    app.dependency_overrides.clear()


def test_list_cooks(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    # create a recipe first
    recipe = Recipe(name="Test Recipe")
    db_session.add(recipe)
    db_session.commit()

    # create a cook log for that recipe
    cook = CookLog(
        recipe_id=recipe.id, cooked_at="2024-01-02", rating=4, cooked_by="Test User"
    )
    db_session.add(cook)
    db_session.commit()

    response = client.get(f"/recipes/{recipe.id}/cooks")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["rating"] == 4
    app.dependency_overrides.clear()


def test_edit_cook(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    # create a recipe first
    recipe = Recipe(name="Test Recipe")
    db_session.add(recipe)
    db_session.commit()

    # create a cook log for that recipe
    cook = CookLog(
        recipe_id=recipe.id, cooked_at="2024-01-02", rating=4, cooked_by="Test User"
    )

    db_session.add(cook)
    db_session.commit()

    response = client.patch(
        f"/recipes/{recipe.id}/cooks/{cook.id}",
        json={
            "recipe_id": recipe.id,
            "cooked_at": "2024-03-03",
            "rating": 2,
            "cooked_by": "Test User 2",
        },
    )

    assert response.status_code == 200
    assert response.json()["cooked_at"] == "2024-03-03"
    assert response.json()["rating"] == 2
    assert response.json()["cooked_by"] == "Test User 2"
    app.dependency_overrides.clear()


def test_delete_cook(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    # create a recipe first
    recipe = Recipe(name="Test Recipe")
    db_session.add(recipe)
    db_session.commit()

    # create a cook log for that recipe
    cook = CookLog(
        recipe_id=recipe.id, cooked_at="2024-01-02", rating=4, cooked_by="Test User"
    )

    db_session.add(cook)
    db_session.commit()

    response = client.delete(f"/recipes/{recipe.id}/cooks/{cook.id}")
    deleted = db_session.query(CookLog).filter_by(id=cook.id).first()
    assert deleted is None
    assert response.status_code == 200
    app.dependency_overrides.clear()
