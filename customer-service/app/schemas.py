from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    email: str
    address: str
    phone: str


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    address: str
    phone: str

    class Config:
        from_attributes = True
