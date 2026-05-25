from datetime import date
from pydantic import BaseModel, Field

from application.protocols.clock import Clock
from domain.rentals.rental import Rental
from domain.rentals.date_range import DateRange
from domain.rentals.repository import IRentalRepository
from domain.scooters.repository import IScooterRepository
from application.protocols.unit_of_work import UnitOfWork
from domain.rentals.pricing_service import PricingService

class ReserveRentalCommand(BaseModel):
    scooter_id: int = Field(..., description="ID самоката для бронирования")
    user_id: int = Field(..., description="ID пользователя, который арендует")
    start_date: date = Field(..., description="Дата начала аренды")
    end_date: date = Field(..., description="Дата окончания аренды")


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
        command: ReserveRentalCommand,
    ) -> Rental:
        scooter = await self.scooter_repository.get_by_id(command.scooter_id)

        if scooter is None:
            raise ValueError(f"Scooter with id {command.scooter_id} not found.")

        period = DateRange(start=command.start_date, end=command.end_date)

        if await self.rental_repository.get_active_rentals(
            command.scooter_id, period
        ):
            raise ValueError(
                f"Scooter {command.scooter_id} has active rentals during period {period}"
            )

        rental = Rental.create(
            scooter=scooter,
            user_id=command.user_id,
            period=period,
            pricing_service=self.pricing_service,
            current_time=self.clock.now(),
        )

        saved_rental = await self.rental_repository.save(rental)
        await self.unit_of_work.commit()

        return saved_rental
