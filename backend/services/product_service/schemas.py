# schemas.py (Pydantic Model)
from pydantic import BaseModel

class BikeCreate(BaseModel):
    name: str
    price: float
    description: str | None = None

class BikeOut(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None

    class Config:
        orm_mode = True  # This allows Pydantic to convert from ORM (SQLAlchemy) to Pydantic models
