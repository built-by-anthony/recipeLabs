from fastapi import APIRouter, Depends
from pydantic import BaseModel
import requests
from recipeLabs.adapters.themealdb import parse_meal
from recipeLabs.database import get_db
from recipeLabs.models import Recipe, RecipeSource
from sqlalchemy.orm import Session
from typing import Optional


class ImportRequest(BaseModel):
    meal_id: str


router = APIRouter()


@router.post("/recipes/import")
def recipe_import(request: ImportRequest, db: Session = Depends(get_db)) -> dict:
    existing = db.query(RecipeSource).filter_by(external_id=request.meal_id).first()
    if existing:
        found = db.query(Recipe).filter_by(id=existing.recipe_id).first()
        if found is None:
            return {"error": "recipe not found"}
        return {"id": found.id, "name": found.name, "status": "already exists"}

    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={request.meal_id}"
    response = requests.get(url).json()
    meal = response["meals"][0]
    meal_obj = parse_meal(meal)

    recipe = Recipe(
        name=meal_obj["name"],
        cuisine=meal_obj["cuisine"],
        instructions=meal_obj["instructions"],
        youtube_url=meal_obj["youtube_url"],
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    source = RecipeSource(
        recipe_id=recipe.id,
        source_type="themealdb",
        external_id=request.meal_id,
        source_url=meal_obj["source_url"],
    )
    db.add(source)
    db.commit()

    return {"id": recipe.id, "name": recipe.name}


@router.get("/recipes")
def list_recipes(db: Session = Depends(get_db)) -> list:
    recipes = db.query(Recipe).all()
    return [{"id": r.id, "name": r.name, "cuisine": r.cuisine} for r in recipes]


class RecipeCreate(BaseModel):
    name: str
    cuisine: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None


@router.post("/recipes")
def create_recipe(request: RecipeCreate, db: Session = Depends(get_db)) -> dict:
    recipe = Recipe(
        name=request.name,
        cuisine=request.cuisine,
        prep_time=request.prep_time,
        cook_time=request.cook_time,
        total_time=request.total_time,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return {
        "id": recipe.id,
        "name": recipe.name,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "total_time": recipe.total_time,
    }
