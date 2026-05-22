from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.rentals.date_range import DateRange
from domain.rentals.rental import Rental
from domain.rentals.repository import IRentalRepository
from domain.rentals.status import RentalStatus
from infrastructure.schemas import RentalModel


class RentalRepositoryImpl(IRentalRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, rental_id: int) -> Rental | None:
        model = await self.session.get(RentalModel, rental_id)
        if not model:
            return None
        return model.to_domain()
    
    async def save(self, rental: Rental) -> Rental:
        model = None
        if rental.id is not None:
            model = await self.session.get(RentalModel, rental.id)
        if model:
            model.update_from_domain(rental)
        else:
            model = RentalModel.from_domain(rental)
            self.session.add(model)

        await self.session.flush()
        return model.to_domain()

    async def get_active_rentals(
        self, scooter_id: int, period: DateRange
    ) -> List[Rental]:
        stmt = (
        select(RentalModel)
        .where(
            RentalModel.scooter_id == scooter_id,
            RentalModel.status.in_([RentalStatus.RESERVED, RentalStatus.ACTIVE]),
            RentalModel.period_end >= period.start,
            RentalModel.period_start <= period.end,       
            )
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [model.to_domain() for model in models]
