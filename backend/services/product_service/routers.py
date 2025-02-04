from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import sys
from pathlib import Path
from schemas import BikeCreate, BikeOut

try:
    from shared_database.models import Bike, BikeImage
    from shared_database.database import get_db
except ImportError:
    import sys
    from pathlib import Path

    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from shared_database.models import Bike, BikeImage
    from shared_database.database import get_db


router = APIRouter()


@router.get("/api/bikes", response_model=list[BikeOut])
async def read_bikes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bike).where(Bike.bought == False).options(selectinload(Bike.images))
    )
    bikes = result.scalars().all()
    return bikes


@router.patch("/api/bikes/{bike_id}/mark_as_bought")
async def mark_bike_as_bought(bike_id: int, db: AsyncSession = Depends(get_db)):
    bike = await db.get(Bike, bike_id)
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    bike.bought = True
    await db.commit()
    return {"message": "Bike marked as bought"}


@router.get("/api/bikes/{bike_id}", response_model=BikeOut)
async def read_bike(bike_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Bike).where(Bike.id == bike_id).options(selectinload(Bike.images))
    )
    bike = result.scalar_one_or_none()

    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    return bike
