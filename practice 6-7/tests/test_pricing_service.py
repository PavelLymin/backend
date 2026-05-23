import pytest
from datetime import date

from domain.rentals.date_range import DateRange
from domain.rentals.pricing_service import PricingService
from domain.scooters.condition import ScooterCondition
from domain.shared.money import Money
from domain.scooters.scooter import Scooter
from domain.scooters.category import ScooterCategory


class TestPricingService:
    
    @pytest.fixture
    def service(self) -> PricingService:
        return PricingService()

    def test_calculate_price_for_city_scooter_has_no_upcharge(self, service):
        # Arrange
        scooter = Scooter(
            id=1,
            daily_rate=Money.from_major(100),
            category=ScooterCategory.CITY,
            deposit=Money.from_major(500),
            model_name="City Scooter",
            serial_number="CS12345",
            condition=ScooterCondition.GOOD
        )
        # Аренда на 3 дня (с 22 по 25 мая)
        period = DateRange(start=date(2026, 5, 22), end=date(2026, 5, 25))

        # Act
        details = service.calculate_price(scooter, period)

        # Assert
        # 100 * 3 дня = 300
        assert details.price_for_period == Money.from_major(300)
        # Для CITY наценка 0%
        assert details.category_upcharge == Money.zero()
        # Итоговая цена: 300 + 0 = 300
        assert details.total_price == Money.from_major(300)
        # Депозит возвращается без изменений
        assert details.deposit == Money.from_major(500)

    def test_calculate_price_for_mountain_scooter_applies_twenty_percent_upcharge(self, service):
        # Arrange
        scooter = Scooter(
            id=2,
            daily_rate=Money.from_major(200),
            category=ScooterCategory.MOUNTAIN,
            deposit=Money.from_major(1000),
            model_name="City Scooter",
            serial_number="CS12345",
            condition=ScooterCondition.GOOD
        )
        period = DateRange(start=date(2026, 5, 22), end=date(2026, 5, 24))  # 2 дня

        # Act
        details = service.calculate_price(scooter, period)

        # Assert
        # 200 * 2 дня = 400
        assert details.price_for_period == Money.from_major(400)
        # Наценка 20% от 400 = 80
        assert details.category_upcharge == Money.from_major(80)
        # Итоговая цена: 400 + 80 = 480
        assert details.total_price == Money.from_major(480)

    def test_calculate_price_for_zero_days_is_zero(self, service):
        # Arrange
        scooter = Scooter(
            id=3,
            daily_rate=Money.from_major(150),
            category=ScooterCategory.KIDS,  # Наценка 10%
            deposit=Money.from_major(300),
            model_name="City Scooter",
            serial_number="CS12345",
            condition=ScooterCondition.GOOD
        )
        # Аренда "день в день" дает length_in_days == 0
        period = DateRange(start=date(2026, 5, 22), end=date(2026, 5, 22))

        # Act
        details = service.calculate_price(scooter, period)

        # Assert
        assert details.price_for_period == Money.zero()
        assert details.category_upcharge == Money.zero()
        assert details.total_price == Money.zero()
        # Даже при нулевых днях залога депозит должен быть зафиксирован
        assert details.deposit == Money.from_major(300)