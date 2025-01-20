from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared_database.database import get_db
from shared_database.models import User  # Add a “User” model in models.py
from schemas import UserCreate, UserOut, UserLogin  # Create these schemas as needed

router = APIRouter()


@router.post("/api/users", response_model=UserOut)
async def create_user(user_input: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(User).where(User.username == user_input.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user_input.username,
        password=user_input.password,
        email=user_input.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/api/users/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/api/users/login")
async def login_user(user_input: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_input.username))
    user = result.scalar_one_or_none()
    if not user or user.password != user_input.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
    }
