from pydantic import BaseModel
from fastapi import Form


class RateRequest(BaseModel):
    cargo_type: str
    declared_value: float

    class Config:
        schema_extra = {"example": {"cargo_type": "Glass", "declared_value": 1000.0}}


class RateCreateRequest(BaseModel):
    date: str
    cargo_type: str
    rate: float
    user_id: int

    @classmethod
    def as_form(
        cls,
        date: str = Form(default="2023-11-01"),
        cargo_type: str = Form(default="Glass"),
        rate: float = Form(default=0.03),
        user_id: int = Form(default=1),
    ):
        return cls(date=date, cargo_type=cargo_type, rate=rate, user_id=user_id)


class RateResponse(BaseModel):
    insurance_cost: float

    class Config:
        schema_extra = {"example": {"insurance_cost": 70.0}}
