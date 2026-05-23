import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, date

from application.rentals.reserve_rental import ReserveRentalUseCase
from domain.rentals.rental import Rental
from domain.rentals.status import RentalStatus
from domain.rentals.date_range import DateRange
from domain.shared.money import Money
from domain.scooters.scooter import Scooter
from domain.scooters.category import ScooterCategory
from domain.scooters.condition import ScooterCondition
from domain.rentals.pricing_service import PricingDetails


@pytest.mark.anyio
class TestReserveRentalUseCase:

    @pytest.fixture
    def mock_dependencies(self):
        scooter_repo = MagicMock()
        scooter_repo.get_by_id = AsyncMock()
        
        rental_repo = MagicMock()
        rental_repo.get_active_rentals = AsyncMock()
        rental_repo.save = AsyncMock()
        
        pricing_service = MagicMock()
        
        uow = MagicMock()
        uow.commit = AsyncMock()
        
        clock = MagicMock()
        clock.now.return_value = datetime(2026, 5, 20, 12, 0)
        
        return scooter_repo, rental_repo, pricing_service, uow, clock

    async def test_reserve_success(self, mock_dependencies):
        # Arrange
        scooter_repo, rental_repo, pricing_service, uow, clock = mock_dependencies
        
        scooter_id = 1
        user_id = 99
        start_date = date(2026, 5, 22)
        end_date = date(2026, 5, 25)

        # 1. Находим самокат
        sample_scooter = Scooter(
            id=scooter_id,
            model_name="Xiaomi Pro 2",
            serial_number="X-12345",
            category=ScooterCategory.CITY,
            daily_rate=Money.from_major(100),
            deposit=Money.from_major(500),
            condition=ScooterCondition.EXCELLENT
        )
        scooter_repo.get_by_id.return_value = sample_scooter

        # 2. Активных аренд на эти даты нет
        rental_repo.get_active_rentals.return_value = []

        # 3. Доменный сервис считает цену
        expected_details = PricingDetails(
            price_for_period=Money.from_major(300),
            category_upcharge=Money.zero(),
            total_price=Money.from_major(300),
            deposit=Money.from_major(500)
        )
        pricing_service.calculate_price.return_value = expected_details

        # 4. Репозиторий при сохранении возвращает объект с проставленным ID
        expected_saved_rental = Rental(
            id=777,
            scooter_id=scooter_id,
            user_id=user_id,
            period=DateRange(start=start_date, end=end_date),
            price_for_period=expected_details.price_for_period,
            total_price=expected_details.total_price,
            deposit_amount=expected_details.deposit,
            status=RentalStatus.RESERVED,
            created_on=datetime(2026, 5, 20, 12, 0)
        )
        rental_repo.save.return_value = expected_saved_rental

        use_case = ReserveRentalUseCase(
            scooter_repository=scooter_repo,
            rental_repository=rental_repo,
            pricing_service=pricing_service,
            unit_of_work=uow,
            clock=clock
        )

        # Act
        result = await use_case.execute(scooter_id, user_id, start_date, end_date)

        # Assert
        assert result == expected_saved_rental
        assert result.id == 777
        
        # Проверяем цепочку вызовов зависимостей
        scooter_repo.get_by_id.assert_awaited_once_with(scooter_id)
        rental_repo.get_active_rentals.assert_awaited_once_with(
            scooter_id, DateRange(start=start_date, end=end_date)
        )
        pricing_service.calculate_price.assert_called_once_with(
            sample_scooter, DateRange(start=start_date, end=end_date)
        )
        uow.commit.assert_awaited_once()

    async def test_reserve_fails_when_scooter_not_found(self, mock_dependencies):
        # Arrange
        scooter_repo, rental_repo, _, _, _ = mock_dependencies
        scooter_repo.get_by_id.return_value = None  # Самокат не найден в БД

        use_case = ReserveRentalUseCase(*mock_dependencies)

        # Act & Assert
        with pytest.raises(ValueError, match="Scooter with id 404 not found."):
            await use_case.execute(404, 99, date(2026, 5, 22), date(2026, 5, 25))

        rental_repo.get_active_rentals.assert_not_awaited()
        rental_repo.save.assert_not_awaited()

    async def test_reserve_fails_when_scooter_has_active_rentals(self, mock_dependencies):
        # Arrange
        scooter_repo, rental_repo, pricing_service, _, _ = mock_dependencies
        
        scooter_id = 1
        sample_scooter = Scooter(
            id=scooter_id, model_name="M365", serial_number="123",
            category=ScooterCategory.CITY, daily_rate=Money.from_major(100),
            deposit=Money.from_major(500), condition=ScooterCondition.EXCELLENT
        )
        scooter_repo.get_by_id.return_value = sample_scooter

        # Имитируем, что на эти даты уже есть чужая бронь
        existing_rental = MagicMock(spec=Rental)
        rental_repo.get_active_rentals.return_value = [existing_rental]

        use_case = ReserveRentalUseCase(*mock_dependencies)

        # Act & Assert
        with pytest.raises(ValueError, match="has active rentals during period"):
            await use_case.execute(scooter_id, 99, date(2026, 5, 22), date(2026, 5, 25))

        # Расчет цены и сохранение не должны вызываться
        pricing_service.calculate_price.assert_not_called()
        rental_repo.save.assert_not_awaited()