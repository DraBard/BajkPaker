# backend/services/order_service/schemas.py

from pydantic import BaseModel
from typing import List

class BikeOut(BaseModel):
    id: int
    name: str
    price: float
    description: str

    class Config:
        orm_mode = True

class CartItemCreate(BaseModel):
    bike_id: int
    quantity: int

class CartItemOut(BaseModel):
    id: int
    bike_id: int
    quantity: int
    bike: BikeOut

    class Config:
        orm_mode = True

class OrderItemCreate(BaseModel):
    bike_id: int
    quantity: int

class OrderCreate(BaseModel):
    total_price: float
    items: List[OrderItemCreate]

class OrderItemOut(BaseModel):
    id: int
    bike_id: int
    quantity: int
    bike: BikeOut

    class Config:
        orm_mode = True

class OrderOut(BaseModel):
    id: int
    total_price: float
    items: List[OrderItemOut]

    class Config:
        orm_mode = True
