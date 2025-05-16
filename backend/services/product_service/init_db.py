import asyncio
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, TEXT
from sqlalchemy.orm import relationship

# Base class for all models
Base = declarative_base()


# Define models (can be replaced with your actual models import)
class Bike(Base):
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(TEXT)
    price = Column(Float, nullable=False)
    type = Column(String(50))
    size = Column(String(20))
    brand = Column(String(50))
    is_electric = Column(Boolean, default=False)
    bought = Column(Boolean, default=False)

    images = relationship(
        "BikeImage", back_populates="bike", cascade="all, delete-orphan"
    )


class BikeImage(Base):
    __tablename__ = "bike_images"

    id = Column(Integer, primary_key=True)
    bike_id = Column(Integer, ForeignKey("bikes.id"), nullable=False)
    image_url = Column(String(255), nullable=False)
    is_main = Column(Boolean, default=False)

    bike = relationship("Bike", back_populates="images")


# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# SQLite database path configuration
if ENVIRONMENT == "production":
    # Use the mounted volume path in fly.io
    DB_PATH = "/data/bajkpaker.db"
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
else:
    # Local development path
    DB_PATH = os.path.join(Path(__file__).parent.absolute(), "bajkpaker.db")

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
