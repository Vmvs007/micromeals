from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int


class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    items: List[OrderItemRequest]


class OrderStatusUpdate(BaseModel):
    status: str


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    name: str
    unit_price: float
    quantity: int
    subtotal: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
