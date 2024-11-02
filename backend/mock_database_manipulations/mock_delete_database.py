# Import necessary libraries
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path

# Add the path for Base to python paths
import sys

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import shared database models
from backend.shared_database.models import Base


# Load configuration
def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config_path = Path(__file__).resolve().parents[2] / "config.yaml"
config = load_config(config_path)
DATABASE_URL = config["database_dev"]["url"]

# Create async engines and sessions
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Function to drop all tables in a given engine
async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print(f"All tables dropped in {engine.url.database}")


# Main function to run the drop tables script for both databases
async def main():
    await drop_all_tables()


# Running the script
if __name__ == "__main__":
    asyncio.run(main())
