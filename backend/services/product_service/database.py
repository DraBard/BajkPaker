from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
import time
import logging
import pathlib

logger = logging.getLogger(__name__)

# Use SQLite for local development and deployment
# On Fly.io, use /data directory for persistent storage
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"
DATA_DIR = "/data" if IS_PRODUCTION else "."

# Create data directory if it doesn't exist (for local development)
if not IS_PRODUCTION and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# SQLite doesn't need credentials
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev.db")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# SQLite path - store in /data on Fly.io for persistence
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

# Build the database URL for SQLite with aiosqlite driver
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

print("DATABASE_URL:", DATABASE_URL)

# Create async engine with settings for SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    connect_args={"check_same_thread": False},  # Required for SQLite
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
                    await session.commit()
                    return  # Success, exit the function
                except Exception as e:
                    await session.rollback()
                    raise e
                finally:
                    await session.close()  # Explicitly close to free up resources quickly
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
