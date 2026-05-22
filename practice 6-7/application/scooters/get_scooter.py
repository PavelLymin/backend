from domain.scooters.scooter import Scooter
from domain.scooters.repository import IScooterRepository


class GetScooterUseCase:

    def __init__(self, scooter_repository: IScooterRepository) -> None:
        self.scooter_repository = scooter_repository

    async def execute(self, scooter_id: int) -> Scooter:
        return await self.scooter_repository.get_by_id(scooter_id)
