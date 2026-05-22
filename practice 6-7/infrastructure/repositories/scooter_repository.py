from sqlalchemy.ext.asyncio import AsyncSession

from domain.scooters.scooter import Scooter
from domain.scooters.repository import IScooterRepository
from infrastructure.schemas import ScooterModel


class ScooterRepositoryImpl(IScooterRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, scooter_id: int) -> Scooter | None:
        model = await self.session.get(ScooterModel, scooter_id)
        if not model:
            return None
        return model.to_domain()

    async def save(self, scooter: Scooter) -> None:
        model = None
        if scooter.id is not None:
            model = await self.session.get(ScooterModel, scooter.id)
        if model:
            model.update_from_domain(scooter)
        else:
            model = ScooterModel.from_domain(scooter)
            self.session.add(model)
