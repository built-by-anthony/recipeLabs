from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from recipeLabs.database import get_db
from recipeLabs.models import CookLog

router = APIRouter()


class CookCreate(BaseModel):
    cooked_at: date
    rating: int
    notes: Optional[str] = None
    cooked_by: str


@router.post("/recipes/{recipe_id}/cooks")
def create_cook(
    recipe_id: int, request: CookCreate, db: Session = Depends(get_db)
) -> dict:
    cook = CookLog(
        recipe_id=recipe_id,
        cooked_at=request.cooked_at,
        rating=request.rating,
        notes=request.notes,
        cooked_by=request.cooked_by,
    )
    db.add(cook)
    db.commit()
    db.refresh(cook)

    return {
        "id": cook.id,
        "recipe_id": cook.recipe_id,
        "cooked_at": cook.cooked_at,
        "rating": cook.rating,
        "notes": cook.notes,
        "cooked_by": cook.cooked_by,
    }


@router.get("/recipes/{recipe_id}/cooks")
def list_cooks(recipe_id: int, db: Session = Depends(get_db)) -> list:
    cooks = db.query(CookLog).filter_by(recipe_id=recipe_id).all()
    return [
        {
            "id": c.id,
            "recipe_id": c.recipe_id,
            "cooked_at": c.cooked_at,
            "rating": c.rating,
            "notes": c.notes,
            "cooked_by": c.cooked_by,
        }
        for c in cooks
    ]


class CookPatch(BaseModel):
    cooked_at: date
    rating: int
    notes: Optional[str] = None
    cooked_by: str


@router.patch("/recipes/{recipe_id}/cooks/{cook_id}")
def edit_cook(
    recipe_id: int, cook_id: int, request: CookPatch, db: Session = Depends(get_db)
) -> dict:
    cook = db.query(CookLog).filter_by(id=cook_id).first()

    if cook is None:
        raise HTTPException(status_code=404, detail="Cook log not found")

    cook.cooked_at = request.cooked_at
    cook.rating = request.rating
    cook.notes = request.notes
    cook.cooked_by = request.cooked_by

    db.commit()
    db.refresh(cook)

    return {
        "id": cook.id,
        "recipe_id": cook.recipe_id,
        "cooked_at": cook.cooked_at,
        "rating": cook.rating,
        "notes": cook.notes,
        "cooked_by": cook.cooked_by,
    }


@router.delete("/recipes/{recipe_id}/cooks/{cook_id}")
def delete_cook(recipe_id, cook_id, db: Session = Depends(get_db)):
    cook = db.query(CookLog).filter_by(id=cook_id).first()

    if cook is None:
        raise HTTPException(status_code=404, detail="Cook log not found")

    db.delete(cook)
    db.commit()
    return {"message": "deleted"}
