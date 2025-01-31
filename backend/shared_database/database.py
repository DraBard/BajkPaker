from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import yaml


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config_path = Path(__file__).resolve().parents[2] / "config.yaml"
config = load_config(config_path)
# TODO define model for local and deployment for now has to change manually
DATABASE_URL = config["local"]["database_dev"]["url"]

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
