import uvicorn
from config import settings
from api import router as api_router
from fastapi_pagination import add_pagination

from contextlib import asynccontextmanager
from fastapi import FastAPI

from task_queue.broker import broker
from models import db_helper



@asynccontextmanager
async def lifespan(app: FastAPI):
    if not broker.is_worker_process:
        await broker.startup()

    yield

    await db_helper.dispose()

    if not broker.is_worker_process:
        await broker.shutdown()

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
