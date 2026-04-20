from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class MeasurementType(str, Enum):
    GRAMS = "GRAMS"
    PIECES = "PIECES"
    MILLILITERS = "MILLILITERS"


class IngredientForGeneration(BaseModel):
    name: str = Field(..., description="Название ингредиента")
    quantity: int = Field(..., gt=0, description="Количество ингредиента")
    measurement: MeasurementType = Field(..., description="Единица измерения")


class GeneratedRecipeSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Название рецепта")
    description: str = Field(..., min_length=1, description="Описание и инструкции по приготовлению")
    cooking_time: int = Field(..., gt=0, description="Время готовки в минутах")
    difficulty: int = Field(default=2, ge=1, le=5, description="Сложность рецепта от 1 до 5")
    cuisine_name: str = Field(..., description="Название кухни (например, итальянская, русская)")
    ingredients: List[IngredientForGeneration] = Field(..., description="Список ингредиентов")
    allergens: List[str] = Field(default=[], description="Список потенциальных аллергенов")


class RecipeGenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Описание желаемого рецепта")


class RecipeGenerationResponse(BaseModel):
    status: str = Field(default="Генерация началась", description="Статус генерации")
