from fastapi import APIRouter, Form
from typing import Annotated
from models import  FormData
from config import settings

router = APIRouter(
    tags=["Auth"],
    prefix=settings.url.auth,
)

# Form Data
@router.post('/login')
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}

# Model Form Data
@router.post("/form-login")
async def login_form(data: Annotated[FormData, Form()]):
    return data