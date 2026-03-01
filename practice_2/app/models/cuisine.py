from pydantic import BaseModel


class CuisineBase(BaseModel):
    name: str


class CuisineCreate(CuisineBase):
    pass


class CuisineUpdate(CuisineBase):
    name: str | None = None


class CuisineRead(CuisineBase):
    id: int