from typing import Protocol, List

from domain.rentals.date_range import DateRange
from domain.rentals.rental import Rental


class IRentalRepository(Protocol):
    
    async def get_by_id(self, rental_id: int) -> Rental | None: ...

    async def save(self, rental: Rental) -> Rental: ...

    async def get_active_rentals(
        self, scooter_id: int, period: DateRange
    ) -> List[Rental]: ...