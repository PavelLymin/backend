import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import settings
from models import db_helper
from api import router as api_router
from fastapi_pagination import add_pagination


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()

app = FastAPI(lifespan=lifespan)

add_pagination(app)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.run.host, 
        port=settings.run.port, 
        reload=settings.run.reload
    )
