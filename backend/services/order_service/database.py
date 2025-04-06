from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from typing import AsyncGenerator
import time
import logging

logger = logging.getLogger(__name__)

# In production, these variables will come from Fly.io secrets/env
DB_USER = os.getenv("DB_USER", "bajkpaker")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST = os.getenv("DB_HOST", "bajkpaker-mysql.internal")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# Build the database URL dynamically
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine with extremely optimized settings for very low memory
engine = create_async_engine(
    DATABASE_URL, 
    echo=DB_ECHO, 
    pool_pre_ping=True, 
    pool_recycle=30,  # Recycle connections more frequently
    pool_size=1,      # Absolute minimum pool size
    max_overflow=1,   # Minimum overflow connections
    pool_timeout=20,  # Shorter timeout
    connect_args={
        "connect_timeout": 10,  # MySQL connection timeout in seconds
        "client_flag": 0,       # Disable unnecessary client flags
    }
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
                logger.warning(f"Database connection attempt {retries} failed. Retrying in {wait_time}s. Error: {str(e)}")
                time.sleep(wait_time)
            else:
                logger.error(f"All database connection attempts failed. Last error: {str(e)}")
                raise last_error
