import asyncio
from domain.scooters.category import ScooterCategory
from domain.scooters.condition import ScooterCondition
from domain.shared.money import Money
from infrastructure.settings import Settings
from infrastructure.db import DatabaseHelper
from infrastructure.schemas import ScooterModel

async def seed_data():
    print("Начало заселения базы данных самокатов...")
    
    # 1. Инициализируем инфраструктуру бд
    settings = Settings()
    db_helper = DatabaseHelper(settings)
    session_factory = db_helper.session_factory

    # 2. Готовим тестовые данные (используем модель БД напрямую для сидов)
    initial_scooters = [
        ScooterModel(
            model_name="Xiaomi Mi Electric Scooter 3",
            serial_number="XIAOMI-12345-M",
            category=ScooterCategory.CITY,
            daily_rate=Money.from_major(500),  # 500 рублей/сутки
            deposit=Money.from_major(2000),
            condition=ScooterCondition.EXCELLENT
        ),
        ScooterModel(
            model_name="Ninebot KickScooter MAX",
            serial_number="NINEBOT-9988-X",
            category=ScooterCategory.MOUNTAIN,
            daily_rate=Money.from_major(800),
            deposit=Money.from_major(4000),
            condition=ScooterCondition.GOOD
        ),
        ScooterModel(
            model_name="Kugoo Kirin Mini",
            serial_number="KUGOO-MINI-001",
            category=ScooterCategory.KIDS,
            daily_rate=Money.from_major(300),
            deposit=Money.from_major(1000),
            condition=ScooterCondition.WORN
        ),
    ]

    # 3. Записываем в базу данных
    async with session_factory() as session:
        async with session.begin(): # Автоматически сделает commit, если нет ошибок
            for scooter in initial_scooters:
                # Проверяем по серийнику, чтобы случайно не продублировать при повторном запуске
                from sqlalchemy import select
                existing = await session.execute(
                    select(ScooterModel).where(ScooterModel.serial_number == scooter.serial_number)
                )
                if not existing.scalars().first():
                    session.add(scooter)
                    print(f"Добавлен самокат: {scooter.model_name} ({scooter.serial_number})")
                else:
                    print(f"Самокат {scooter.serial_number} уже существует, пропуск.")
                    
    # Закрываем пул соединений
    await db_helper.dispose()
    print("База данных успешно заселена!")

if __name__ == "__main__":
    # Запуск асинхронного сидера
    asyncio.run(seed_data())