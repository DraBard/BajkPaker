import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models import Base, Order, OrderItem, CartItem, Bike

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# SQLite database path configuration
if ENVIRONMENT == "production":
    DB_PATH = "/data/order_processing_service.db"
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
else:
    DB_PATH = os.path.join(Path(__file__).parent.absolute(), "order_processing_service.db")

# Build the SQLite database URL
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


async def init_db():
    print(f"Initializing order service database at: {DB_PATH}")

    # Create engine
    engine = create_async_engine(
        DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )

    # Create all tables and handle migrations
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Add customer_info column if it doesn't exist (migration)
        try:
            pragma = await conn.execute(text("PRAGMA table_info('orders')"))
            cols = [row[1] for row in pragma.fetchall()]
            if "customer_info" not in cols:
                await conn.execute(
                    text("ALTER TABLE orders ADD COLUMN customer_info JSON")
                )
                print("Added customer_info column to orders table")
        except Exception as e:
            print(f"Migration note: {e}")

    print("Order service database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
