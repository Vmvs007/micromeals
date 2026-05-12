from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str  # MBWAY, CARD, CASH


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    payment_method: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
