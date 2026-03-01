from pydantic import BaseModel, Field
from typing import Optional

class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    cooking_time: int = Field(..., gt=0, description="Время готовки должно быть > 0")
    difficulty: int = Field(
        1,
        ge=1,
        le=5,
        description="Сложность от 1 до 5"
    )


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    cooking_time: Optional[int] = Field(None, gt=0)
    difficulty: Optional[int] = Field(None, ge=1, le=5)


class RecipeRead(RecipeBase):
    id: int