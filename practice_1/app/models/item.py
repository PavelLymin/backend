from pydantic import BaseModel, Field, HttpUrl
from typing import Literal

# Image
class Image(BaseModel):
    url: HttpUrl
    name: str

# Item 
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None 
    tags: set[str] = set()
    images: list[Image] | None = None

# Query Parameter Model
class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []