from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Bike, BikeImage
from schemas import BikeCreate, BikeOut
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared.database import get_db

router = APIRouter()

@router.get("/api/bikes", response_model=list[BikeOut])
async def read_bikes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bike).options(selectinload(Bike.images)))
    bikes = result.scalars().all()
    return bikes

@router.get("/api/bikes/{bike_id}", response_model=BikeOut)
async def read_bike(bike_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bike).where(Bike.id == bike_id).options(selectinload(Bike.images)))
    bike = result.scalar_one_or_none()
    if bike is None:
        raise HTTPException(status_code=404, detail="Bike not found")
    return bike

@router.post("/api/bikes", response_model=BikeCreate)
async def create_bike(bike: BikeCreate, db: AsyncSession = Depends(get_db)):
    new_bike = Bike(name=bike.name, price=bike.price, description=bike.description, image_url=bike.image_url)
    db.add(new_bike)
    await db.commit()
    await db.refresh(new_bike)
    return new_bike

