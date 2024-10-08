from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from models import Bike
from schemas import BikeCreate, BikeOut
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.database import get_db

router = APIRouter()

@router.get("/api/bikes", response_model=list[BikeOut])
async def read_bikes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bike))
    bikes = result.scalars().all()
    return bikes

@router.post("/api/bikes", response_model=BikeCreate)
async def create_bike(bike: BikeCreate, db: AsyncSession = Depends(get_db)):
    new_bike = Bike(name=bike.name, price=bike.price, description=bike.description)
    db.add(new_bike)
    await db.commit()
    await db.refresh(new_bike)
    return new_bike

