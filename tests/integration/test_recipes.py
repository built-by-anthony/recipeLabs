from recipeLabs.models import Recipe


def test_create_recipe(db_session):
    recipe = Recipe(name="Test Recipe")
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    assert recipe.id is not None
    assert recipe.name == "Test Recipe"
