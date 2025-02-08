from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path
from .load_config import load_config


config = load_config()
if config["mode"] == "deployment":
    DATABASE_URL = config["deployment"]["database_dev"]["url"]
elif config["mode"] == "local":
    DATABASE_URL = config["local"]["database_dev"]["url"]
else:
    raise ValueError("Invalid mode in config file")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
