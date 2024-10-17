# backend/services/order_service/routers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from models import Order, OrderItem, CartItem, Bike
from schemas import OrderCreate, OrderOut, CartItemCreate, CartItemOut
import sys
from pathlib import Path
import httpx

sys.path.append(str(Path(__file__).resolve().parents[2]))
from database import get_db

router = APIRouter()

PRODUCT_SERVICE_URL = "http://localhost:8001/api"

@router.post("/api/orders", response_model=OrderOut)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    new_order = Order(total_price=order.total_price)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    async with httpx.AsyncClient() as client:
        for item in order.items:
            new_order_item = OrderItem(order_id=new_order.id, bike_id=item.bike_id, quantity=item.quantity)
            db.add(new_order_item)
            # Call product service to mark the bike as bought
            response = await client.patch(f"{PRODUCT_SERVICE_URL}/bikes/{item.bike_id}/mark_as_bought")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to mark bike as bought")
    await db.commit()

    return new_order

@router.get("/api/orders/{order_id}", response_model=OrderOut)
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/api/cart", response_model=CartItemOut)
async def add_to_cart(cart_item: CartItemCreate, db: AsyncSession = Depends(get_db)):
    new_cart_item = CartItem(bike_id=cart_item.bike_id, quantity=cart_item.quantity)
    db.add(new_cart_item)
    await db.commit()
    await db.refresh(new_cart_item)
    return new_cart_item

@router.get("/api/cart", response_model=list[CartItemOut])
async def get_cart(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).options(selectinload(CartItem.bike)))
    cart_items = result.scalars().all()
    return cart_items