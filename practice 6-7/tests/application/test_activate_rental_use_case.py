import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from application.rentals.activate_rental import ActivateRentalUseCase
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money


@pytest.mark.anyio
class TestActivateRentalUseCase:

    @pytest.fixture
    def mock_rental_repository(self):
        repository = MagicMock()
        repository.get_by_id = AsyncMock()
        repository.save = AsyncMock()
        return repository

    @pytest.fixture
    def mock_unit_of_work(self):
        uow = MagicMock()
        uow.commit = AsyncMock()
        return uow

    @pytest.fixture
    def sample_reserved_rental(self) -> Rental:
        return Rental(
            id=42,
            scooter_id=1,
            user_id=7,
            period=DateRange(start=date(2026, 5, 23), end=date(2026, 5, 25)),
            price_for_period=Money.from_major(300),
            total_price=Money.from_major(300),
            deposit_amount=Money.from_major(500),
            status=RentalStatus.RESERVED,
            created_on=datetime(2026, 5, 23, 12, 0)
        )

    async def test_execute_success(
        self, 
        mock_rental_repository, 
        mock_unit_of_work, 
        sample_reserved_rental
    ):
        # Arrange
        rental_id = 42
        # Настраиваем, чтобы репозиторий возвращал нашу зарезервированную аренду
        mock_rental_repository.get_by_id.return_value = sample_reserved_rental
        
        use_case = ActivateRentalUseCase(
            rental_repository=mock_rental_repository,
            unit_of_work=mock_unit_of_work
        )

        # Act
        result = await use_case.execute(rental_id)

        # Assert
        # 1. Проверяем, что вернулась именно наша аренда и её статус изменился
        assert result == sample_reserved_rental
        assert result.status == RentalStatus.ACTIVE
        
        # 2. Проверяем, что юзкейс правильно вызвал зависимости
        mock_rental_repository.get_by_id.assert_awaited_once_with(rental_id)
        mock_rental_repository.save.assert_awaited_once_with(sample_reserved_rental)
        mock_unit_of_work.commit.assert_awaited_once()

    async def test_execute_rental_not_found_raises_error(
        self, 
        mock_rental_repository, 
        mock_unit_of_work
    ):
        # Arrange
        rental_id = 999
        # Репозиторий возвращает None, если аренда не найдена
        mock_rental_repository.get_by_id.return_value = None
        
        use_case = ActivateRentalUseCase(
            rental_repository=mock_rental_repository,
            unit_of_work=mock_unit_of_work
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Rental with id 999 not found."):
            await use_case.execute(rental_id)

        # Проверяем, что поиск был, но сохранение и коммит НЕ вызывались из-за ошибки
        mock_rental_repository.get_by_id.assert_awaited_once_with(rental_id)
        mock_rental_repository.save.assert_not_awaited()
        mock_unit_of_work.commit.assert_not_awaited()