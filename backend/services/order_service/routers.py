from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import os
import uuid
import logging
from fastapi.middleware.cors import CORSMiddleware
import sib_api_v3_sdk
from sib_api_v3_sdk.api import transactional_emails_api
from sib_api_v3_sdk.models import SendSmtpEmail

from database import get_db
from models import Order, OrderItem, CartItem, Bike
from schemas import OrderCreate, OrderOut, CartItemCreate, CartItemOut, OrderStatus
from product_client import ProductServiceClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
router = APIRouter()


# Updated CORS configuration function
def configure_cors(app):
    # Get environment - development or production
    env = os.environ.get("ENV", "development")

    # Define allowed origins based on environment
    if env == "development":
        # In development, allow localhost origins with different ports
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://localhost:8001",
            "http://localhost:8002",
            "http://localhost:8003",
            # Add any other development origins as needed
        ]
    else:
        # In production, use specific domains
        origins = [
            "https://bajkpaker.fly.dev",
            # Add other production domains as needed
        ]

    # Configure the CORS middleware with more comprehensive settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],  # Allow all headers for development simplicity
        max_age=86400,  # Cache preflight requests for 24 hours
    )

    logger.info(f"CORS configured with origins: {origins}")


def get_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())  # Generate unique ID
        response.set_cookie(key="session_id", value=session_id)
    return session_id


async def get_product_client() -> ProductServiceClient:
    return ProductServiceClient()


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
    product_client: ProductServiceClient = Depends(get_product_client),
):
    """Add bike to cart, first fetching current data from product service"""
    logger.info(f"Received request to add to cart: {cart_item}")
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request cookies: {request.cookies}")

    session_id = get_session_id(request, response)
    logger.info(f"Session ID for cart operation: {session_id}")

    # Fetch bike from product service to ensure it exists and get current data
    logger.info(
        f"Fetching bike data for bike_id: {cart_item.bike_id} from product service."
    )
    bike_data = await product_client.get_bike(cart_item.bike_id)
    if not bike_data:
        logger.error(
            f"Bike not found in product service for bike_id: {cart_item.bike_id}"
        )
        raise HTTPException(status_code=404, detail="Bike not found in product service")
    logger.info(f"Successfully fetched bike data: {bike_data}")

    # Check if already in cart
    existing = await db.execute(
        select(CartItem).where(
            CartItem.bike_id == cart_item.bike_id, CartItem.session_id == session_id
        )
    )
    if existing.scalar_one_or_none():
        logger.warning(
            f"Item {cart_item.bike_id} already in cart for session {session_id}"
        )
        raise HTTPException(status_code=400, detail="This item is already in the cart")

    # Check if bike exists in our local database
    logger.info(f"Checking local database for bike_id: {cart_item.bike_id}")
    bike = await db.get(Bike, cart_item.bike_id)
    if not bike:
        # Create a new local copy of the bike
        logger.info(f"Bike {cart_item.bike_id} not found locally, creating new entry.")
        bike = Bike(
            id=bike_data["id"],
            name=bike_data["name"],
            price=bike_data["price"],
            description=bike_data.get("description"),
            bought=bike_data.get("bought", False),
        )
        db.add(bike)
        logger.info(f"Created local copy of bike {bike_data['id']}")
    else:
        # Update local bike data to match product service
        logger.info(f"Bike {cart_item.bike_id} found locally, updating entry.")
        bike.name = bike_data["name"]
        bike.price = bike_data["price"]
        bike.description = bike_data.get("description")
        bike.bought = bike_data.get("bought", False)
        logger.info(f"Updated local copy of bike {bike_data['id']}")

    # Create cart item
    logger.info(
        f"Creating cart item for bike_id: {cart_item.bike_id}, quantity: {cart_item.quantity}, session_id: {session_id}"
    )
    new_item = CartItem(
        bike_id=cart_item.bike_id, quantity=cart_item.quantity, session_id=session_id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item, attribute_names=["bike"])
    logger.info(f"Successfully added item to cart: {new_item.id}")
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

    await db.delete(item)
    await db.commit()
    return {"message": "Item removed from cart"}


load_dotenv()
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")
BREVO_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "BajkPaker")
NOTIFICATION_EMAIL = "bajkpaker@gmail.com"


def send_order_notification(order, customer):
    """Send notification emails via Brevo (Sendinblue): one to internal address, one to client."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = BREVO_API_KEY
    api_client = sib_api_v3_sdk.ApiClient(configuration)
    api_instance = transactional_emails_api.TransactionalEmailsApi(api_client)

    internal_email = SendSmtpEmail(
        sender={"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
        to=[{"email": NOTIFICATION_EMAIL}],
        subject=f"Nowe zamówienie #{order.id}",
        html_content=(
            f"<h3>Nowe zamówienie #{order.id}</h3>"
            f"<p>Wartość: {order.total_price} PLN</p>"
            f"<h4>Dane klienta:</h4>"
            f"<p>Imię i nazwisko: {customer['name']}<br>"
            f"Email: {customer['email']}<br>"
            f"Telefon: {customer['phone']}</p>"
        ),
    )
    try:
        response = api_instance.send_transac_email(internal_email)
        logger.info("Brevo internal email sent, id: %s", response.message_id)
    except Exception as e:
        logger.error("Failed to send internal email via Brevo: %s", e)

    # send confirmation to client
    client_email = SendSmtpEmail(
        sender={"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
        to=[{"email": customer["email"]}],
        subject=f"Twoje zamówienie #{order.id} zostało zarejestrowane",
        html_content=(
            f"<h3>Dziękujemy za złożenie zamówienia #{order.id}</h3>"
            f"<p>Twoje zamówienie zostało pomyślnie zarejestrowane. </p>"
            f"<p>Wartość zamówienia: {order.total_price} PLN</p>"
            f"<p>Skontaktujemy się z Tobą wkrótce w celu potwierdzenia szczegółów.</p>"
        ),
    )
    try:
        response2 = api_instance.send_transac_email(client_email)
        logger.info("Brevo client email sent, id: %s", response2.message_id)
    except Exception as e:
        logger.error("Failed to send client email via Brevo: %s", e)
    return True


@router.post("/api/orders")
async def create_order(
    order: OrderCreate,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    product_client: ProductServiceClient = Depends(get_product_client),
):
    """Create a new order and send notification email"""
    session_id = get_session_id(request, response)

    logger.info("Creating order with total_price: %s", order.total_price)
    new_order = Order(
        total_price=order.total_price,
        status=OrderStatus.PENDING,
        customer_info=order.customer.dict(),  # Store customer info
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    # Process each ordered item
    for item in order.items:
        # Verify bike exists in product service
        bike_data = await product_client.get_bike(item.bike_id)
        if not bike_data:
            logger.error(f"Bike {item.bike_id} not found in product service")
            await db.delete(new_order)
            await db.commit()
            raise HTTPException(
                status_code=404, detail=f"Bike {item.bike_id} not found"
            )

        # Get or create local bike record
        bike = await db.get(Bike, item.bike_id)
        if not bike:
            bike = Bike(
                id=bike_data["id"],
                name=bike_data["name"],
                price=bike_data["price"],
                description=bike_data.get("description"),
                bought=bike_data.get(
                    "bought", False
                ),  # Use existing value, don't set to True
            )
            db.add(bike)

        # Create order item
        new_order_item = OrderItem(
            order_id=new_order.id, bike_id=item.bike_id, quantity=item.quantity
        )
        db.add(new_order_item)

    # Remove items from cart after successful order
    await db.execute(select(CartItem).where(CartItem.session_id == session_id))
    cart_items = await db.execute(
        select(CartItem).where(CartItem.session_id == session_id)
    )
    for item in cart_items.scalars().all():
        await db.delete(item)

    await db.commit()

    # use Brevo to notify
    send_order_notification(new_order, order.customer.dict())

    return {
        "order_id": new_order.id,
        "message": "Order created successfully. Payment on delivery only.",
    }


@router.get("/api/orders/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    """Get details of a specific order"""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.bike))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/api/orders", response_model=list[OrderOut])
async def list_orders(db: AsyncSession = Depends(get_db)):
    """List all orders (typically you'd want authentication here)"""
    result = await db.execute(
        select(Order).options(selectinload(Order.items).selectinload(OrderItem.bike))
    )
    orders = result.scalars().all()
    return orders
