from typing import Protocol

from domain.scooters.scooter import Scooter


class IScooterRepository(Protocol):

    async def get_by_id(self, scooter_id: int) -> Scooter | None: ...

    async def save(self, scooter: Scooter) -> None: ...
