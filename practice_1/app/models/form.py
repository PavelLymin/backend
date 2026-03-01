from pydantic import BaseModel

# Form Data
class FormData(BaseModel):
    model_config = {"extra": "forbid"}

    username: str
    password: str