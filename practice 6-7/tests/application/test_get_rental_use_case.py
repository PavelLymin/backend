import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from application.rentals.get_rental import GetRentalUseCase
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money


@pytest.mark.anyio
class TestGetRentalUseCase:

    @pytest.fixture
    def mock_rental_repository(self):
        repo = MagicMock()
        repo.get_by_id = AsyncMock()
        return repo

    async def test_get_rental_success(self, mock_rental_repository):
        # Arrange
        rental_id = 42
        expected_rental = Rental(
            id=rental_id,
            scooter_id=2,
            user_id=3,
            period=DateRange(start=date(2026, 5, 23), end=date(2026, 5, 24)),
            price_for_period=Money.from_major(150),
            total_price=Money.from_major(150),
            deposit_amount=Money.from_major(300),
            status=RentalStatus.ACTIVE,
            created_on=datetime(2026, 5, 23, 12, 0)
        )
        mock_rental_repository.get_by_id.return_value = expected_rental
        
        use_case = GetRentalUseCase(rental_repository=mock_rental_repository)

        # Act
        result = await use_case.execute(rental_id)

        # Assert
        assert result == expected_rental
        mock_rental_repository.get_by_id.assert_awaited_once_with(rental_id)

    async def test_get_rental_not_found_raises_error(self, mock_rental_repository):
        # Arrange
        rental_id = 999
        mock_rental_repository.get_by_id.return_value = None
        
        use_case = GetRentalUseCase(rental_repository=mock_rental_repository)

        # Act & Assert
        with pytest.raises(ValueError, match="Rental with id 999 not found."):
            await use_case.execute(rental_id)
            
        mock_rental_repository.get_by_id.assert_awaited_once_with(rental_id)