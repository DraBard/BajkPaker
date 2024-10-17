# Import necessary libraries
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import yaml
from pathlib import Path

# Load configuration
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

config_path = Path(__file__).resolve().parents[2] / 'config.yaml'
config = load_config(config_path)
DATABASE_URL_PRODUCT = config["database_product_dev"]["url"]
DATABASE_URL_ORDER = config["database_order_dev"]["url"]

# Create async engines and sessions
engine_product = create_async_engine(DATABASE_URL_PRODUCT, echo=True)
AsyncSessionLocalProduct = sessionmaker(engine_product, class_=AsyncSession, expire_on_commit=False)

engine_order = create_async_engine(DATABASE_URL_ORDER, echo=True)
AsyncSessionLocalOrder = sessionmaker(engine_order, class_=AsyncSession, expire_on_commit=False)

# Declarative Base
Base = declarative_base()

# Function to drop all tables in a given engine
async def drop_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print(f"All tables dropped in {engine.url.database}")

# Main function to run the drop tables script for both databases
async def main():
    await drop_all_tables(engine_product)
    await drop_all_tables(engine_order)

# Running the script
if __name__ == "__main__":
    asyncio.run(main())