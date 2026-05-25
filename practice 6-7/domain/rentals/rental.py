from datetime import datetime
from dataclasses import dataclass
from domain.rentals.pricing_service import PricingService
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.scooters.scooter import Scooter
from domain.shared.money import Money


@dataclass
class Rental:
    id: int | None
    scooter_id: int
    user_id: int
    period: DateRange
    price_for_period: Money
    total_price: Money
    deposit_amount: Money
    status: RentalStatus
    created_on: datetime
    returned_on: datetime | None = None
    cancelled_on: datetime | None = None

    @classmethod
    def create(
        cls,
        scooter: Scooter,
        user_id: int,
        period: DateRange,
        pricing_service: PricingService,
        current_time: datetime,
    ) -> "Rental":
        pricing_details = pricing_service.calculate_price(scooter, period)
        
        return cls(
            id=None,
            scooter_id=scooter.id,
            user_id=user_id,
            period=period,
            total_price=pricing_details.total_price,
            price_for_period=pricing_details.price_for_period,
            deposit_amount=pricing_details.deposit,
            status=RentalStatus.RESERVED,
            created_on=current_time,
        )

    def activate(self) -> None:
        if self.status != RentalStatus.RESERVED:
            raise ValueError(f"Cannot activate rental from status {self.status}. Only RESERVED is allowed.")
        self.status = RentalStatus.ACTIVE

    def return_rental(self, current_time: datetime) -> None:
        if self.status != RentalStatus.ACTIVE:
            raise ValueError(f"Cannot return rental from status {self.status}. Only ACTIVE is allowed.")
        self.status = RentalStatus.RETURNED
        self.returned_on = current_time

    def cancel(self, current_time: datetime) -> None:
        if self.status != RentalStatus.RESERVED:
            raise ValueError(f"Cannot cancel rental from status {self.status}. Only RESERVED is allowed.")
        self.status = RentalStatus.CANCELLED
        self.cancelled_on = current_time