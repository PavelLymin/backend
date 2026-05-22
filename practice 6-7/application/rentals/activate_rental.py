from domain.rentals.rental import Rental
from domain.rentals.repository import IRentalRepository
from application.protocols.unit_of_work import UnitOfWork


class ActivateRentalUseCase:

    def __init__(
        self,
        rental_repository: IRentalRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self.rental_repository = rental_repository
        self.unit_of_work = unit_of_work

    async def execute(self, rental_id: int) -> Rental:
        rental = await self.rental_repository.get_by_id(rental_id)
        if rental is None:
            raise ValueError(f"Rental with id {rental_id} not found.")
        rental.activate()
        await self.rental_repository.save(rental)
        await self.unit_of_work.commit()
        return rental
