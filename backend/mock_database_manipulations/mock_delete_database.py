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
DATABASE_URL = config["DATABASE_URL"]

# Create async engine and session
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Declarative Base
Base = declarative_base()

# Function to drop all tables
async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped")

# Main function to run the drop tables script
async def main():
    await drop_all_tables()

# Running the script
if __name__ == "__main__":
    asyncio.run(main())