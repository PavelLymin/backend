import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

from config import settings
from models import db_helper, Base
from api import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await db_helper.dispose()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.run.host, 
        port=settings.run.port, 
        reload=settings.run.reload
    )
