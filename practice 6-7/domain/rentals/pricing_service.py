from dataclasses import dataclass

from domain.rentals.date_range import DateRange
from domain.shared.money import Money
from domain.scooters.scooter import Scooter
from domain.scooters.category import ScooterCategory


@dataclass(frozen=True)
class PricingDetails:
    price_for_period: Money
    category_upcharge: Money
    total_price: Money
    deposit: Money


class PricingService:
    
    def calculate_price(self, scooter: Scooter, period: DateRange) -> PricingDetails:
        price_for_period = scooter.daily_rate * period.length_in_days

        percentage_upcharge = self._get_category_upcharge_percentage(scooter.category)
        category_upcharge = Money(
            amount_minor=int(price_for_period.amount_minor * percentage_upcharge)
        )

        total_price = price_for_period + category_upcharge

        return PricingDetails(
            price_for_period=price_for_period,
            category_upcharge=category_upcharge,
            total_price=total_price,
            deposit=scooter.deposit,
        )

    @staticmethod
    def _get_category_upcharge_percentage(category: ScooterCategory) -> float:
        if category == ScooterCategory.CITY:
            return 0.0
        elif category == ScooterCategory.MOUNTAIN:
            return 0.2
        elif category == ScooterCategory.KIDS:
            return 0.1
        else:
            raise ValueError(f"Unknown category: {category}")
