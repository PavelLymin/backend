import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from application.rentals.return_rental import ReturnRentalUseCase
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money


@pytest.mark.anyio
class TestReturnRentalUseCase:

    @pytest.fixture
    def mock_dependencies(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        repo.save = AsyncMock()
        
        uow = MagicMock()
        uow.commit = AsyncMock()
        
        clock = MagicMock()
        clock.now.return_value = datetime(2026, 5, 25, 18, 0)
        
        return repo, uow, clock

    async def test_return_success(self, mock_dependencies):
        # Arrange
        repo, uow, clock = mock_dependencies
        rental_id = 77
        
        active_rental = Rental(
            id=rental_id,
            scooter_id=1,
            user_id=12,
            period=DateRange(start=date(2026, 5, 22), end=date(2026, 5, 25)),
            price_for_period=Money.from_major(300),
            total_price=Money.from_major(300),
            deposit_amount=Money.from_major(500),
            status=RentalStatus.ACTIVE,  # Возвращаем из статуса ACTIVE
            created_on=datetime(2026, 5, 22, 10, 0)
        )
        repo.get_by_id.return_value = active_rental
        
        use_case = ReturnRentalUseCase(rental_repository=repo, unit_of_work=uow, clock=clock)

        # Act
        result = await use_case.execute(rental_id)

        # Assert
        assert result.status == RentalStatus.RETURNED
        assert result.returned_on == datetime(2026, 5, 25, 18, 0)
        
        repo.get_by_id.assert_awaited_once_with(rental_id)
        repo.save.assert_awaited_once_with(active_rental)
        uow.commit.assert_awaited_once()
        