from pydantic import BaseModel

class RecipeIngredientRead(BaseModel):
    id: int
    ingredient_id: int
    quantity: int
    measurement: int
    name: str 

    class Config:
        from_attributes = True

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: int
    measurement: int

