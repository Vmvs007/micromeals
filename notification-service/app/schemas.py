from pydantic import BaseModel
from datetime import datetime


class NotificationCreate(BaseModel):
    customer_id: int
    type: str  # EMAIL, SMS, APP
    subject: str
    message: str


class NotificationResponse(BaseModel):
    id: int
    customer_id: int
    type: str
    subject: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
