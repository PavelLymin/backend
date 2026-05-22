import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka

from infrastructure.settings import Settings
from api.router import router as subscriptions_router
from ioc import (
    AppProvider,
    DbProvider,
    DomainProvider,
    RepositoriesProvider,
    ServicesProvider,
)


def create_app() -> FastAPI:
    container = make_async_container(
        AppProvider(),
        DbProvider(),
        DomainProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await container.close()

    settings = Settings()
    app = FastAPI(lifespan=lifespan, title="Demo")
    app.include_router(subscriptions_router, prefix=settings.url.prefix)

    setup_dishka(container=container, app=app)
    return app


main_app = create_app()


if __name__ == "__main__":
    settings = Settings()
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
