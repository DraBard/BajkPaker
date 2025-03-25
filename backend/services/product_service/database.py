from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator

# In production, these variables will come from Fly.io secrets/env
DB_USER = os.getenv("DB_USER", "bajkpaker")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST = os.getenv(
    "DB_HOST", "bajkpaker-mysql.internal"
)  # Will be bajkpaker-mysql.internal in prod
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# Build the database URL dynamically
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("DATABASE_URL:", DATABASE_URL)

# Create async engine
engine = create_async_engine(
    DATABASE_URL, echo=DB_ECHO, pool_pre_ping=True, pool_recycle=300
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get a database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
