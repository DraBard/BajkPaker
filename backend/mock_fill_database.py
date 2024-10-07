import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import yaml
from pathlib import Path

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
config_path = Path(__file__).resolve().parents[2] / 'config.yaml'
config = load_config(config_path)
DATABASE_URL = config["DATABASE_URL"]

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Declarative Base
Base = declarative_base()

# Define the Bike model
class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255))
    price = Column(Integer)

# Function to create the tables (if they don't exist)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Function to add mock data to the database
async def add_mock_bikes():
    async with AsyncSessionLocal() as session:
        mock_bikes = [
            Bike(name="Mountain Bike", description="A sturdy bike for off-road", price=599),
            Bike(name="Road Bike", description="A lightweight bike for speed", price=899),
            Bike(name="Electric Bike", description="A bike with electric assist", price=1499),
            Bike(name="Hybrid Bike", description="A versatile bike for city and trail", price=799)
        ]
        
        session.add_all(mock_bikes)
        await session.commit()
        print("Mock bikes added to the database")

# Main function to run the database setup and data population
async def main():
    await create_tables()  # Create the tables in the database
    await add_mock_bikes()  # Insert mock data into the database

# Running the script
if __name__ == "__main__":
    asyncio.run(main())
