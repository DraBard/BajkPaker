from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config_path = Path(__file__).resolve().parents[3] / 'config.yaml'
config = load_config(config_path)
DATABASE_URL = config["database_order_dev"]["url"]

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session