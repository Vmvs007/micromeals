from pydantic import BaseModel
from typing import Optional, List


class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str
    address: str


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    cuisine_type: Optional[str] = None
    address: Optional[str] = None
    active: Optional[bool] = None


class RestaurantResponse(BaseModel):
    id: int
    name: str
    cuisine_type: str
    address: str
    active: bool

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str]
    price: float
    available: bool

    class Config:
        from_attributes = True
