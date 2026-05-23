import pytest
from datetime import datetime, date
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money


class TestRentalDomainInvariants:

    @pytest.fixture
    def reserved_rental(self) -> Rental:
        return Rental(
            id=1,
            scooter_id=42,
            user_id=100,
            period=DateRange(start=date(2026, 5, 23), end=date(2026, 5, 25)),
            price_for_period=Money.from_major(300),
            total_price=Money.from_major(300),
            deposit_amount=Money.from_major(500),
            status=RentalStatus.RESERVED,
            created_on=datetime(2026, 5, 23, 12, 0)
        )

    # --- Группа тестов для метода ACTIVATE ---

    def test_activate_success_from_reserved(self, reserved_rental):
        # Act
        reserved_rental.activate()

        # Assert
        assert reserved_rental.status == RentalStatus.ACTIVE

    @pytest.mark.parametrize("invalid_status", [
        RentalStatus.ACTIVE,
        RentalStatus.RETURNED,
        RentalStatus.CANCELLED
    ])
    def test_activate_fails_for_invalid_statuses(self, reserved_rental, invalid_status):
        # Arrange - переводим в недопустимый для активации статус
        reserved_rental.status = invalid_status

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot activate rental from status"):
            reserved_rental.activate()

    # --- Группа тестов для метода RETURN_RENTAL ---

    def test_return_rental_success_from_active(self, reserved_rental):
        # Arrange - переводим в ACTIVE, так как вернуть можно только активную аренду
        reserved_rental.activate()
        now = datetime(2026, 5, 25, 14, 0)

        # Act
        reserved_rental.return_rental(current_time=now)

        # Assert
        assert reserved_rental.status == RentalStatus.RETURNED
        assert reserved_rental.returned_on == now

    @pytest.mark.parametrize("invalid_status", [
        RentalStatus.RESERVED,
        RentalStatus.RETURNED,
        RentalStatus.CANCELLED
    ])
    def test_return_rental_fails_for_invalid_statuses(self, reserved_rental, invalid_status):
        # Arrange
        reserved_rental.status = invalid_status
        now = datetime(2026, 5, 25, 14, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot return rental from status"):
            reserved_rental.return_rental(current_time=now)

    # --- Группа тестов для метода CANCEL ---

    def test_cancel_success_from_reserved(self, reserved_rental):
        # Arrange
        now = datetime(2026, 5, 23, 13, 0)

        # Act
        reserved_rental.cancel(current_time=now)

        # Assert
        assert reserved_rental.status == RentalStatus.CANCELLED
        assert reserved_rental.cancelled_on == now

    @pytest.mark.parametrize("invalid_status", [
        RentalStatus.ACTIVE,
        RentalStatus.RETURNED,
        RentalStatus.CANCELLED
    ])
    def test_cancel_fails_for_invalid_statuses(self, reserved_rental, invalid_status):
        # Arrange
        reserved_rental.status = invalid_status
        now = datetime(2026, 5, 23, 13, 0)

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot cancel rental from status"):
            reserved_rental.cancel(current_time=now)