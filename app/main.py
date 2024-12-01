import os
from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import endpoints
from app.database import engine, Base

# Загружаем переменные окружения
load_dotenv()

# Получаем JWT параметры из переменных окружения
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()

# Подключение маршрутов
app.include_router(endpoints.router)


@app.on_event("startup")
async def startup():
    # Создание таблиц, если они еще не существуют
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
