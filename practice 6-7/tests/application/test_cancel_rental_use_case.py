import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from application.rentals.cancel_rental import CancelRentalUseCase
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money


@pytest.mark.anyio
class TestCancelRentalUseCase:

    @pytest.fixture
    def mock_dependencies(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        repo.save = AsyncMock()
        
        uow = MagicMock()
        uow.commit = AsyncMock()
        
        clock = MagicMock()

        clock.now.return_value = datetime(2026, 5, 23, 15, 0)
        
        return repo, uow, clock

    @pytest.fixture
    def sample_reserved_rental(self) -> Rental:
        return Rental(
            id=10,
            scooter_id=1,
            user_id=7,
            period=DateRange(start=date(2026, 5, 23), end=date(2026, 5, 25)),
            price_for_period=Money.from_major(300),
            total_price=Money.from_major(300),
            deposit_amount=Money.from_major(500),
            status=RentalStatus.RESERVED,
            created_on=datetime(2026, 5, 23, 12, 0)
        )

    async def test_cancel_success(self, mock_dependencies, sample_reserved_rental):
        # Arrange
        repo, uow, clock = mock_dependencies
        rental_id = 10
        repo.get_by_id.return_value = sample_reserved_rental
        
        use_case = CancelRentalUseCase(rental_repository=repo, unit_of_work=uow, clock=clock)

        # Act
        result = await use_case.execute(rental_id)

        # Assert
        # Проверяем изменение состояния сущности
        assert result.status == RentalStatus.CANCELLED
        assert result.cancelled_on == datetime(2026, 5, 23, 15, 0)
        
        # Проверяем вызовы моков
        clock.now.assert_called_once()
        repo.get_by_id.assert_awaited_once_with(rental_id)
        repo.save.assert_awaited_once_with(sample_reserved_rental)
        uow.commit.assert_awaited_once()

    async def test_cancel_rental_not_found_raises_error(self, mock_dependencies):
        # Arrange
        repo, uow, clock = mock_dependencies
        rental_id = 999
        repo.get_by_id.return_value = None
        
        use_case = CancelRentalUseCase(rental_repository=repo, unit_of_work=uow, clock=clock)

        # Act & Assert
        with pytest.raises(ValueError, match="Rental with id 999 not found."):
            await use_case.execute(rental_id)

        # Сохранение и коммит не должны вызываться
        repo.save.assert_not_awaited()
        uow.commit.assert_not_awaited()
