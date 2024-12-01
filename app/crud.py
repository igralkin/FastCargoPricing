import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func, desc, text
from sqlalchemy.exc import NoResultFound
from app.models import Rate, RateChangeLog
from app.kafka.manager import KafkaManager
from datetime import datetime

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Экземпляр KafkaManager
kafka_manager = KafkaManager()


async def log_change_to_db(
    session: AsyncSession, user_id: int, action: str, rate_id: int
):
    """
    Логирование изменений в таблицу rate_change_logs
    """
    new_log = RateChangeLog(
        user_id=user_id,
        action=action,
        rate_id=rate_id,
        timestamp=func.now(),
    )
    session.add(new_log)
    await session.commit()
    logger.info(f"Logged change to DB: {action} for rate_id={rate_id}")


# Получение тарифа
async def get_rate(session: AsyncSession, cargo_type: str):
    query = (
        select(Rate)
        .where(
            Rate.cargo_type == cargo_type,
            Rate.date < func.current_date() + text("INTERVAL '1 day'"),
        )
        .order_by(desc(Rate.date), desc(Rate.id))
        .limit(1)
    )
    result = await session.execute(query)
    rate = result.scalars().first()

    if rate:
        logger.info(f"Rate fetched from DB: {rate}")
    else:
        logger.warning(f"No valid rates found for cargo_type: {cargo_type}")

    return rate


# Создание нового тарифа
async def create_rate(
    session: AsyncSession, date: str, cargo_type: str, rate: float, user_id: int = None
):
    await kafka_manager.start()
    action: str = "create"
    try:
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()

        new_rate = Rate(date=date, cargo_type=cargo_type, rate=rate)
        session.add(new_rate)
        await session.commit()

        # Логирование в Kafka
        await kafka_manager.log_action(
            action=action,
            user_id=user_id,
            rate_id=new_rate.id,
            date=date.isoformat(),
            cargo_type=cargo_type,
            rate=rate,
        )

        # Логирование в базу данных
        await log_change_to_db(
            session=session,
            user_id=user_id,
            action=action,
            rate_id=new_rate.id,
        )

        return new_rate
    finally:
        await kafka_manager.stop()


async def update_rate(
    session: AsyncSession, rate_id: int, new_rate: float, user_id: int = None
):
    await kafka_manager.start()
    action: str = "update"
    try:
        # Проверяем, существует ли тариф
        query_check = select(Rate).where(Rate.id == rate_id)
        result = await session.execute(query_check)
        rate = result.scalar_one_or_none()

        if not rate:
            raise NoResultFound(f"Rate with ID {rate_id} not found.")

        # Обновляем тариф
        query = update(Rate).where(Rate.id == rate_id).values(rate=new_rate)
        await session.execute(query)
        await session.commit()

        # Логирование в Kafka
        await kafka_manager.log_action(
            action=action,
            user_id=user_id,
            rate_id=rate_id,
            new_rate=new_rate,
        )

        # Логирование в базу данных
        await log_change_to_db(
            session=session,
            user_id=user_id,
            action=action,
            rate_id=rate_id,
        )

        # Возвращаем сообщение для отображения
        return f"Rate {rate_id} successfully updated to {new_rate} by user {user_id}."
    finally:
        await kafka_manager.stop()


async def delete_rate(session: AsyncSession, rate_id: int, user_id: int = None):
    await kafka_manager.start()
    action: str = "delete"
    try:
        # Проверяем, существует ли тариф
        query_check = select(Rate).where(Rate.id == rate_id)
        result = await session.execute(query_check)
        rate = result.scalar_one_or_none()

        if not rate:
            raise NoResultFound(f"Rate with ID {rate_id} not found.")

        # Удаляем тариф
        query = delete(Rate).where(Rate.id == rate_id)
        await session.execute(query)
        await session.commit()

        # Логирование в Kafka
        await kafka_manager.log_action(action=action, user_id=user_id, rate_id=rate_id)

        # Логирование в базу данных
        await log_change_to_db(
            session=session,
            user_id=user_id,
            action=action,
            rate_id=rate_id,
        )

        # Возвращаем сообщение для отображения
        return f"Rate {rate_id} successfully deleted by user {user_id}."
    finally:
        await kafka_manager.stop()
