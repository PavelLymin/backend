from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Annotated, Literal
from config import settings

router = APIRouter(
    tags=["Students"],
    prefix=settings.url.students,
)

@router.get('')
async def read_students(format: Annotated[Literal["json", "html"], Query()] = "json"):
    json = JSONResponse(content = {"students": [{"id": 1, "name": "Name1"}, {"id": 2, "name": "Name2"}]})
    if format == 'html':
        return  HTMLResponse(content=f"<html><body><pre>{json}</pre></body></html>")
    return json