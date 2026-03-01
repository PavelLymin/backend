from pydantic import BaseModel
from .ingredient import IngredientRead

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int

class RecipeIngredientRead(BaseModel):
    id: int
    quantity: int
    measurement: int
    name: str 