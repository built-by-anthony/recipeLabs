import json

from recipeLabs.adapters.themealdb import parse_meal


def test_parse_meal():
    with open("tests/fixtures/themealdb_carbinara.json", "r") as file:
        data = json.load(file)

    test_meal = data["meals"][0]
    result = parse_meal(test_meal)

    assert result["name"] == "Spaghetti alla Carbonara"
    assert result["cuisine"] == "Italian"
    assert len(result["ingredients"]) == 6  # carbonara has 6 non-empty ingredients
    assert result["ingredients"][0]["name"] == "Spaghetti"
    assert result["ingredients"][0]["quantity"] == "320g"
    assert isinstance(result["instructions"], str)
    assert len(result["instructions"]) > 0
