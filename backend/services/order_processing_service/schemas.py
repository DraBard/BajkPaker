from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BikeOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    bought: bool = False

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


class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    phone: str


class OrderCreate(BaseModel):
    total_price: float
    items: List[OrderItemCreate]
    customer: CustomerInfo


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
    status: str
    items: List[OrderItemOut]
    customer: Optional[CustomerInfo]

    class Config:
        orm_mode = True


class BikeDetails(BaseModel):
    frameType: str
    frameSize: Optional[str] = None
    color: Optional[str] = None
    components: Optional[str] = None
    budget: Optional[str] = None
    additionalInfo: Optional[str] = None


class CustomBikeOrder(BaseModel):
    customer: CustomerInfo
    bikeDetails: BikeDetails
