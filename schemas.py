from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ---------- Users ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Calculations ----------
class OperationType(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"


class CalculationCreate(BaseModel):
    a: float
    type: OperationType
    b: float
    user_id: int

    @field_validator("b")
    @classmethod
    def no_zero_division(cls, b, info):
        if "type" in info.data and info.data["type"] == OperationType.divide and b == 0:
            raise ValueError("Cannot divide by zero")
        return b


class CalculationUpdate(BaseModel):
    a: Optional[float] = None
    b: Optional[float] = None
    type: Optional[OperationType] = None


class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: str
    result: float
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True