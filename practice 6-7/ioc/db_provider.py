from typing import AsyncIterable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from dishka import Provider, Scope, provide

from application.protocols.unit_of_work import UnitOfWork
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork


class DbProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    @provide
    def get_uow(self, session: AsyncSession) -> UnitOfWork:
        return SqlAlchemyUnitOfWork(session)
