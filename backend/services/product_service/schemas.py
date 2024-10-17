# schemas.py (Pydantic Model)
from pydantic import BaseModel
from typing import List, Optional

class BikeImage(BaseModel):
    id: int
    bike_id: int
    image_url: str
    is_main: bool

    class Config:
        orm_mode = True

class BikeCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    images: List[BikeImage] = []

class BikeOut(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    images: List[BikeImage] = []

    class Config:
        orm_mode = True