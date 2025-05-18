import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, Bike, BikeImage

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# SQLite database path configuration
if ENVIRONMENT == "production":
    DB_PATH = "/app/product_service.db"
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
else:
    DB_PATH = os.path.join(Path(__file__).parent.absolute(), "product_service.db")

# Build the SQLite database URL
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


async def init_db():
    print(f"Initializing database at: {DB_PATH}")

    # Create engine
    engine = create_async_engine(
        DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
