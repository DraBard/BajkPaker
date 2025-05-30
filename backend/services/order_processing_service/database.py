from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
import time
import logging
import pathlib

logger = logging.getLogger(__name__)

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# SQLite database path configuration
if ENVIRONMENT == "production":
    DB_PATH = "/data/order_processing_service.db"
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
else:
    DB_PATH = os.path.join(
        pathlib.Path(__file__).parent.absolute(), "order_processing_service.db"
    )

# Build the SQLite database URL
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Create async engine with optimized settings for very low memory
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args={"check_same_thread": False},  # Allow multithreaded access
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Connection retry mechanism
async def get_db(max_retries=3, retry_delay=1) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get a database session with retry mechanism.
    """
    retries = 0
    last_error = None

    while retries <= max_retries:
        try:
            async with AsyncSessionLocal() as session:
                try:
                    yield session
                    # Do not commit or return here; let FastAPI handle session cleanup
                except Exception as e:
                    await session.rollback()
                    raise e
                break  # Exit the retry loop after successful yield
        except Exception as e:
            last_error = e
            retries += 1
            if retries <= max_retries:
                wait_time = retry_delay * (2 ** (retries - 1))  # Exponential backoff
                logger.warning(
                    f"Database connection attempt {retries} failed. Retrying in {wait_time}s. Error: {str(e)}"
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"All database connection attempts failed. Last error: {str(e)}"
                )
                raise last_error


# Auto-create all tables at import (development only)
if ENVIRONMENT != "production":
    import asyncio
    from models import Base
    from sqlalchemy import text

    async def _init_tables():
        async with engine.begin() as conn:
            # create missing tables
            await conn.run_sync(Base.metadata.create_all)
            # add customer_info column if it doesn't exist
            # check existing columns in orders
            pragma = await conn.execute(text("PRAGMA table_info('orders')"))
            cols = [row[1] for row in pragma.fetchall()]
            if "customer_info" not in cols:
                await conn.execute(
                    text("ALTER TABLE orders ADD COLUMN customer_info JSON")
                )

    # Synchronous kick-off of the async table creation + migration
    asyncio.run(_init_tables())
