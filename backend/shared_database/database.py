from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

config_path = Path(__file__).resolve().parent / "config.yaml"
config = load_config(config_path)
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
