from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from dishka import Provider, Scope, provide

from infrastructure.settings import Settings
from infrastructure.db import DatabaseHelper


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def get_settings(self) -> Settings:
        return Settings()

    @provide
    async def get_db_helper(
        self, settings: Settings
    ) -> AsyncIterable[DatabaseHelper]:
        helper = DatabaseHelper(settings)
        yield helper
        await helper.dispose()

    @provide
    def get_engine(self, helper: DatabaseHelper) -> AsyncEngine:
        return helper.engine

    @provide
    def get_session_factory(
        self, helper: DatabaseHelper
    ) -> async_sessionmaker[AsyncSession]:
        return helper.session_factory
