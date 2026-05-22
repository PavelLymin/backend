from datetime import date

from application.protocols.clock import Clock
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.rentals.repository import IRentalRepository
from domain.scooters.repository import IScooterRepository
from application.protocols.unit_of_work import UnitOfWork
from domain.rentals.pricing_service import PricingService


class ReserveRentalUseCase:

    def __init__(
        self,
        scooter_repository: IScooterRepository,
        rental_repository: IRentalRepository,
        pricing_service: PricingService,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ) -> None:
        self.scooter_repository = scooter_repository
        self.rental_repository = rental_repository
        self.pricing_service = pricing_service
        self.unit_of_work = unit_of_work
        self.clock = clock

    async def execute(
        self,
        scooter_id: int,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> Rental:
        scooter = await self.scooter_repository.get_by_id(scooter_id)

        if scooter is None:
            raise ValueError(f"Scooter with id {scooter_id} not found.")

        period = DateRange(start=start_date, end=end_date)

        active_rentals = await self.rental_repository.get_active_rentals(
            scooter_id, period
        )
        if active_rentals:
            raise ValueError(
                f"Scooter {scooter_id} has active rentals during period {period}"
            )

        pricing_details = self.pricing_service.calculate_price(scooter, period)

        rental = Rental(
            id=None,
            scooter_id=scooter_id,
            user_id=user_id,
            period=period,
            total_price=pricing_details.total_price,
            price_for_period=pricing_details.price_for_period,
            deposit_amount=pricing_details.deposit,
            status=RentalStatus.RESERVED,
            created_on=self.clock.now(),
        )

        saved_rental = await self.rental_repository.save(rental)
        await self.unit_of_work.commit()

        return saved_rental
