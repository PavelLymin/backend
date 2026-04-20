from pydantic import BaseModel, Field
from typing import Optional, List

from models.users import AuthorRead
from .allergen import AllergenRead
from .recipe_ingredients import RecipeIngredientCreate, RecipeIngredientRead
from .cuisine import CuisineRead

class RecipeBase(BaseModel):
    cuisine_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    cooking_time: int = Field(..., gt=0, description="Время готовки должно быть > 0")
    difficulty: int = Field(1, ge=1, le=5, description="Сложность от 1 до 5")


class RecipeRead(RecipeBase):
    id: int


class RecipeFullRead(RecipeRead):
    cuisine: Optional["CuisineRead"] = None
    ingredients: List["RecipeIngredientRead"] = []
    allergens: List["AllergenRead"] = []
    author: Optional[AuthorRead] = None


class RecipeCreate(RecipeBase):
    allergen_ids: list[int]
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(RecipeBase):
    pass