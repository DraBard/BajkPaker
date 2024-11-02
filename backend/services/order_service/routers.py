# backend/services/order_service/routers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
from shared_database.models import Order, OrderItem, CartItem, Bike
from shared_database.database import get_db
from schemas import OrderCreate, OrderOut, CartItemCreate, CartItemOut

router = APIRouter()


@router.get("/api/cart", response_model=list[CartItemOut])
async def get_cart(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).options(selectinload(CartItem.bike)))
    cart_items = result.scalars().all()
    return cart_items


@router.post("/api/cart", response_model=CartItemOut)
async def add_to_cart(cart_item: CartItemCreate, db: AsyncSession = Depends(get_db)):
    bike = await db.get(Bike, cart_item.bike_id)
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    new_cart_item = CartItem(bike_id=cart_item.bike_id, quantity=cart_item.quantity)
    db.add(new_cart_item)
    await db.commit()
    await db.refresh(new_cart_item, attribute_names=["bike"])
    return new_cart_item


@router.delete("/api/cart/{item_id}")
async def remove_from_cart(item_id: int, db: AsyncSession = Depends(get_db)):
    cart_item = await db.get(CartItem, item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    await db.delete(cart_item)
    await db.commit()
    return {"message": "Item removed from cart"}


@router.post("/api/orders", response_model=OrderOut)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    new_order = Order(total_price=order.total_price)
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    for item in order.items:
        bike = await db.get(Bike, item.bike_id)
        if not bike:
            raise HTTPException(status_code=404, detail="Bike not found")

        new_order_item = OrderItem(
            order_id=new_order.id, bike_id=item.bike_id, quantity=item.quantity
        )
        db.add(new_order_item)
        bike.bought = True

    await db.commit()
    return new_order
