from dataclasses import dataclass
from domain.shared.money import Money
from domain.scooters.category import ScooterCategory
from domain.scooters.condition import ScooterCondition


@dataclass
class Scooter:
    id: int | None
    model_name: str
    serial_number: str
    category: ScooterCategory
    daily_rate: Money
    deposit: Money
    condition: ScooterCondition
    