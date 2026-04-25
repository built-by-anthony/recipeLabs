from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey, Date, Text
from typing import Optional


class Base(DeclarativeBase):
    pass


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    cuisine: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    prep_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cook_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    youtube_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unit: Mapped[str] = mapped_column(String, nullable=False)


class RecipeSource(Base):
    __tablename__ = "recipe_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class CookLog(Base):
    __tablename__ = "cook_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), nullable=False
    )
    cooked_at: Mapped[Date] = mapped_column(Date, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cooked_by: Mapped[str] = mapped_column(String, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class RecipeTag(Base):
    __tablename__ = "recipe_tags"

    recipe_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("recipes.id"), nullable=False, primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id"), nullable=False, primary_key=True
    )
