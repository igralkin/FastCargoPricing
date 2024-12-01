import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from app.database import get_db
from app.crud import get_rate, create_rate, update_rate, delete_rate
from app.schemas import RateCreateRequest, RateResponse


# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

router = APIRouter()


@router.get("/calculate/", response_model=RateResponse)
async def calculate_insurance_cost(
    cargo_type: str = Query(default="Glass", description="Тип груза"),
    declared_value: float = Query(default=100.0, description="Объявленная стоимость"),
    db: AsyncSession = Depends(get_db),
):
    """
    Рассчитать стоимость страхования.
    """
    # Получаем тариф для указанного типа груза
    rate = await get_rate(db, cargo_type=cargo_type)
    if not rate:
        raise HTTPException(status_code=404, detail="Rate not found")

    # Рассчитываем стоимость
    insurance_cost = declared_value * rate.rate
    logger.info(
        f"Calculated insurance cost: {insurance_cost} (Declared Value: {declared_value}, Rate: {rate.rate})"
    )
    return RateResponse(insurance_cost=insurance_cost)


@router.post("/rates/")
async def create_new_rate(
    request: RateCreateRequest = Depends(RateCreateRequest.as_form),
    db: AsyncSession = Depends(get_db),
):
    """
    Создать новый тариф.
    """
    new_rate = await create_rate(
        db, request.date, request.cargo_type, request.rate, request.user_id
    )
    return {
        "message": f"Rate {new_rate.id} for {request.cargo_type} has been created by user {request.user_id}",
        "rate": new_rate.id,
    }


@router.put("/rates/{rate_id}")
async def update_existing_rate(
    rate_id: int, new_rate: float, user_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Обновить существующий тариф.
    """
    try:
        message = await update_rate(db, rate_id, new_rate, user_id)
        return {"message": message}
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/rates/{rate_id}")
async def delete_existing_rate(
    rate_id: int, user_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Удалить тариф.
    """
    try:
        message = await delete_rate(db, rate_id, user_id)
        return {"message": message}
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail=str(e))
