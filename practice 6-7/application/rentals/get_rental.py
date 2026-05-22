from domain.rentals.rental import Rental
from domain.rentals.repository import IRentalRepository


class GetRentalUseCase:

    def __init__(self, rental_repository: IRentalRepository) -> None:
        self.rental_repository = rental_repository

    async def execute(self, rental_id: int) -> Rental:
        rental = await self.rental_repository.get_by_id(rental_id)
        if rental is None:
            raise ValueError(f"Rental with id {rental_id} not found.")
        return rental
