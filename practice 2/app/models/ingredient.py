from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(IngredientBase):
    name: str | None = None


class IngredientRead(IngredientBase):
    id: int