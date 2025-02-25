import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import sys
from pathlib import Path
from schemas import OrderCreate, OrderOut, CartItemCreate, CartItemOut
import os
import uuid

try:
    from shared_database.models import Order, OrderItem, CartItem, Bike
    from shared_database.database import get_db
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from shared_database.models import Order, OrderItem, CartItem, Bike
    from shared_database.database import get_db

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


from pydantic import BaseModel


class CheckoutSessionRequest(BaseModel):
    order_id: int


def get_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())  # Generate unique ID
        response.set_cookie(key="session_id", value=session_id)
    return session_id


@router.get("/api/cart", response_model=list[CartItemOut])
async def get_cart(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    session_id = get_session_id(request, response)
    result = await db.execute(
        select(CartItem)
        .where(CartItem.session_id == session_id)
        .options(selectinload(CartItem.bike))
    )
    cart_items = result.scalars().all()
    return cart_items


@router.post("/api/cart", response_model=CartItemOut)
async def add_to_cart(
    cart_item: CartItemCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    session_id = get_session_id(request, response)
    bike = await db.get(Bike, cart_item.bike_id)
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    # Check if already in session cart
    existing = await db.execute(
        select(CartItem).where(
            CartItem.bike_id == cart_item.bike_id, CartItem.session_id == session_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="This item is already in the cart")

    new_item = CartItem(
        bike_id=cart_item.bike_id, quantity=cart_item.quantity, session_id=session_id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item, attribute_names=["bike"])
    return new_item


@router.delete("/api/cart/{item_id}")
async def remove_from_cart(
    item_id: int,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    session_id = get_session_id(request, response)
    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id, CartItem.session_id == session_id
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    bike = await db.get(Bike, item.bike_id)
    if bike:
        bike.bought = False

    await db.delete(item)
    await db.commit()
    return {"message": "Item removed from cart and bike status updated"}


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

    # Eagerly load related items
    result = await db.execute(
        select(Order).where(Order.id == new_order.id).options(selectinload(Order.items))
    )
    new_order = result.scalar_one_or_none()

    return new_order


# Stripe payment
@router.post("/api/payments/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,  # Proper request model
    db: AsyncSession = Depends(get_db),
):
    print(f"Received request with order_id: {request.order_id}")  # Log the request data
    order_id = request.order_id
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Create Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "pln",
                    "product_data": {"name": "Order #" + str(order.id)},
                    "unit_amount": int(order.total_price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url="http://localhost:3000/payment-success",
        cancel_url="http://localhost:3000/payment-cancel",
    )
    return {"checkoutUrl": session.url}


@router.post("/api/payments/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Signature")

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]

        # Retrieve the order from the session's metadata
        order_id = session_obj["metadata"].get("order_id")
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = "paid"
            await db.commit()

    return {"status": "success"}
