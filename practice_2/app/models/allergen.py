from pydantic import BaseModel


class AllergenBase(BaseModel):
    name: str


class AllergenCreate(AllergenBase):
    pass


class AllergenUpdate(AllergenBase):
    name: str | None = None


class AllergenRead(AllergenBase):
    id: int