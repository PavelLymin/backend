import pytest
from unittest.mock import AsyncMock, MagicMock

from domain.scooters.scooter import Scooter
from domain.scooters.category import ScooterCategory
from domain.scooters.condition import ScooterCondition
from domain.shared.money import Money
from application.scooters.get_scooter import GetScooterUseCase


@pytest.mark.anyio
class TestGetScooterUseCase:

    @pytest.fixture
    def mock_scooter_repository(self):
        repository = MagicMock()
        repository.get_by_id = AsyncMock()
        return repository

    async def test_execute_returns_scooter_when_found(self, mock_scooter_repository):
        # Arrange
        scooter_id = 42
        expected_scooter = Scooter(
            id=scooter_id,
            model_name="Ninebot Max G30",
            serial_number="NB-998877",
            category=ScooterCategory.CITY,
            daily_rate=Money.from_major(120),
            deposit=Money.from_major(400),
            condition=ScooterCondition.EXCELLENT
        )
        mock_scooter_repository.get_by_id.return_value = expected_scooter
        
        use_case = GetScooterUseCase(scooter_repository=mock_scooter_repository)

        # Act
        result = await use_case.execute(scooter_id)

        # Assert
        assert result == expected_scooter
        mock_scooter_repository.get_by_id.assert_awaited_once_with(scooter_id)

    async def test_execute_returns_none_when_scooter_not_found(self, mock_scooter_repository):
        # Arrange
        scooter_id = 404
        mock_scooter_repository.get_by_id.return_value = None
        
        use_case = GetScooterUseCase(scooter_repository=mock_scooter_repository)

        # Act
        result = await use_case.execute(scooter_id)

        # Assert
        assert result is None
        mock_scooter_repository.get_by_id.assert_awaited_once_with(scooter_id)