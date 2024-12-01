from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


# Модель для хранения тарифов
class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)  # Дата действия тарифа
    cargo_type = Column(String, nullable=False)  # Тип груза
    rate = Column(Float, nullable=False)  # Значение тарифа, в долях

    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Время создания тариф
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),  # Время обновления тарифа
    )


# Модель для логирования изменений
class RateChangeLog(Base):
    __tablename__ = "rate_change_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, nullable=True
    )  # ID пользователя, инициировавшего изменение
    action = Column(String, nullable=False)  # Тип действия (create, update, delete)
    rate_id = Column(Integer, nullable=False)  # ID тарифа, с которым работали
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Время события
