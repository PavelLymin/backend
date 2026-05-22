import sqlalchemy as sa
from sqlalchemy.orm import Mapped, composite, mapped_column
from datetime import datetime, date

from domain.base import Base
from domain.rentals.date_range import DateRange
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.scooters.category import ScooterCategory
from domain.scooters.condition import ScooterCondition
from domain.scooters.scooter import Scooter
from domain.shared.money import Money


class MoneyType(sa.TypeDecorator):
    impl = sa.Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.amount_minor

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return Money(amount_minor=value)


class ScooterModel(Base):
    __tablename__ = "scooters"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    serial_number: Mapped[str] = mapped_column(sa.String(100), unique=True, nullable=False)
    category: Mapped[ScooterCategory] = mapped_column(
        sa.Enum(ScooterCategory, values_callable=lambda e: [item.value for item in e]),
        nullable=False
    )
    daily_rate: Mapped[Money] = mapped_column(MoneyType, nullable=False)
    deposit: Mapped[Money] = mapped_column(MoneyType, nullable=False)
    condition: Mapped[ScooterCondition] = mapped_column(
        sa.Enum(ScooterCondition, values_callable=lambda e: [item.value for item in e]),
        nullable=False
    )

    def to_domain(self) -> Scooter:
        return Scooter(
            id=self.id,
            model_name=self.model_name,
            serial_number=self.serial_number,
            category=self.category,
            daily_rate=self.daily_rate,
            deposit=self.deposit,
            condition=self.condition
        )

    def update_from_domain(self, scooter: Scooter) -> None:
        self.model_name = scooter.model_name
        self.serial_number = scooter.serial_number
        self.category = scooter.category
        self.daily_rate = scooter.daily_rate
        self.deposit = scooter.deposit
        self.condition = scooter.condition

    @classmethod
    def from_domain(cls, scooter: Scooter) -> "ScooterModel":
        return cls(
            id=scooter.id,
            model_name=scooter.model_name,
            serial_number=scooter.serial_number,
            category=scooter.category,
            daily_rate=scooter.daily_rate,
            deposit=scooter.deposit,
            condition=scooter.condition
        )


class RentalModel(Base):
    __tablename__ = "rentals"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    scooter_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("scooters.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    period_start: Mapped[date] = mapped_column(sa.Date)
    period_end: Mapped[date] = mapped_column(sa.Date)
    period: Mapped[DateRange] = composite("period_start", "period_end")
    price_for_period: Mapped[Money] = mapped_column(MoneyType, nullable=False)
    total_price: Mapped[Money] = mapped_column(MoneyType, nullable=False)
    deposit_amount: Mapped[Money] = mapped_column(MoneyType, nullable=False)
    status: Mapped[RentalStatus] = mapped_column(
        sa.Enum(RentalStatus, values_callable=lambda e: [item.value for item in e]),
        nullable=False
    )
    created_on: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False)
    returned_on: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)
    cancelled_on: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)

    def to_domain(self) -> Rental:
        return Rental(
            id=self.id,
            scooter_id=self.scooter_id,
            user_id=self.user_id,
            period=self.period,
            price_for_period=self.price_for_period,
            total_price=self.total_price,
            deposit_amount=self.deposit_amount,
            status=self.status,
            created_on=self.created_on,
            returned_on=self.returned_on,
            cancelled_on=self.cancelled_on
        )

    def update_from_domain(self, rental: Rental) -> None:
        self.scooter_id = rental.scooter_id
        self.user_id = rental.user_id
        self.period = rental.period
        self.price_for_period = rental.price_for_period
        self.total_price = rental.total_price
        self.deposit_amount = rental.deposit_amount
        self.status = rental.status
        self.created_on = rental.created_on
        self.returned_on = rental.returned_on
        self.cancelled_on = rental.cancelled_on

    @classmethod
    def from_domain(cls, rental: Rental) -> "RentalModel":
        return cls(
            id=rental.id,
            scooter_id=rental.scooter_id,
            user_id=rental.user_id,
            period=rental.period,
            price_for_period=rental.price_for_period,
            total_price=rental.total_price,
            deposit_amount=rental.deposit_amount,
            status=rental.status,
            created_on=rental.created_on,
            returned_on=rental.returned_on,
            cancelled_on=rental.cancelled_on
        )