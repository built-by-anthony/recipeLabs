from datetime import date
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from recipeLabs.adapters.themealdb import parse_meal
from recipeLabs.database import get_db
from recipeLabs.models import CookLog, Recipe, RecipeSource


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
def list_recipes(
    min_rating: Optional[int] = None,
    last_cooked_date: Optional[date] = None,
    source: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list:
    if min_rating is None and last_cooked_date is None and source is None:
        recipes = db.query(Recipe).all()
        return [{"id": r.id, "name": r.name, "cuisine": r.cuisine} for r in recipes]

    query = db.query(Recipe).join(CookLog, CookLog.recipe_id == Recipe.id)

    if min_rating is not None:
        query = query.filter(CookLog.rating >= min_rating)

    if last_cooked_date is not None:
        query = query.filter(CookLog.cooked_at >= last_cooked_date)

    if source is not None:
        query = query.join(RecipeSource, RecipeSource.recipe_id == Recipe.id).filter(
            RecipeSource.source_url == source
        )

    return [{"id": r.id, "name": r.name, "cuisine": r.cuisine} for r in query]


@router.get("/recipes/{recipe_id}")
def get_single_recipe(recipe_id: int, db: Session = Depends(get_db)) -> dict:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": recipe.id,
        "name": recipe.name,
        "cuisine": recipe.cuisine,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "total_time": recipe.total_time,
        "instructions": recipe.instructions,
        "youtube_url": recipe.youtube_url,
    }


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


@router.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter_by(id=recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()
    return {"message": "deleted"}


class RecipePatch(BaseModel):
    name: Optional[str] = None
    cuisine: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    instructions: Optional[str] = None
    youtube_url: Optional[str] = None


@router.patch("/recipes/{recipe_id}")
def edit_recipe(
    recipe_id: int, request: RecipePatch, db: Session = Depends(get_db)
) -> dict:
    recipe = db.query(Recipe).filter_by(id=recipe_id).first()

    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    if request.name is not None:
        recipe.name = request.name

    if request.cuisine is not None:
        recipe.cuisine = request.cuisine

    if request.prep_time is not None:
        recipe.prep_time = request.prep_time

    if request.cook_time is not None:
        recipe.cook_time = request.cook_time

    if request.total_time is not None:
        recipe.total_time = request.total_time

    if request.instructions is not None:
        recipe.instructions = request.instructions

    if request.youtube_url is not None:
        recipe.youtube_url = request.youtube_url

    db.commit()
    db.refresh(recipe)

    return {  # pyright: ignore[reportUnknownVariableType]
        "id": recipe.id,
        "name": recipe.name,
        "cuisine": recipe.cuisine,
        "prep_time": recipe.prep_time,
        "cook_time": recipe.cook_time,
        "total_time": recipe.total_time,
        "instructions": recipe.instructions,
        "youtube_url": recipe.youtube_url,
    }
