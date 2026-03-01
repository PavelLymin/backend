from pydantic import BaseModel, Field
from typing import Optional
from .allergen import AllergenRead
from .ingredient import IngredientRead
from .recipe_ingredients import RecipeIngredientCreate, RecipeIngredientRead

class RecipeBase(BaseModel):
    cuisine_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    cooking_time: int = Field(..., gt=0, description="Время готовки должно быть > 0")
    difficulty: int = Field(1, ge=1, le=5, description="Сложность от 1 до 5")


class RecipeCreate(RecipeBase):
    allergen_ids: list[int]
    ingredients: list[RecipeIngredientCreate]


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    cuisine_id: Optional[int] = Field(None)


class RecipeRead(RecipeBase):
    id: int
    allergens: list[AllergenRead]
    ingredients: list[RecipeIngredientRead]