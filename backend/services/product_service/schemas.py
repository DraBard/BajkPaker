# schemas.py (Pydantic Model)
from pydantic import BaseModel

class BikeImage(BaseModel):
    id: int
    bike_id: int
    image_url: str

    class Config:
        orm_mode = True

class BikeCreate(BaseModel):
    name: str
    price: float
    description: str | None = None
    image_url: str | None = None

class BikeOut(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    image_url: str | None = None
    images: list[BikeImage] = []

    class Config:
        orm_mode = True  # This allows Pydantic to convert from ORM (SQLAlchemy) to Pydantic models