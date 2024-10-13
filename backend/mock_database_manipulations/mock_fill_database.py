import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
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

class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)  # Specify the length for VARCHAR
    price = Column(Integer, nullable=False)
    description = Column(String(2000), nullable=True)  # You can adjust the length accordingly
    image_url = Column(String(500), nullable=True)
    images = relationship("BikeImage", back_populates="bike")

class BikeImage(Base):
    __tablename__ = "bike_images"
    id = Column(Integer, primary_key=True)
    bike_id = Column(Integer, ForeignKey('bikes.id'), nullable=False)
    image_url = Column(String(500), nullable=False)
    bike = relationship("Bike", back_populates="images")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_mock_bikes():
    imgs_path = Path(__file__).resolve().parents[1] / 'images'
    description1 = "Elegancki Rower dla Konesera Porto\n\nOddaj się wyrafinowaniu tego niezwykłego roweru, stworzonego z myślą o wymagającym koneserze wina Porto. Jego eleganckie linie i design inspirowany stylem vintage oddają istotę klasy i wyrafinowania. Głęboka burgundowa rama nawiązuje do bogatych odcieni najlepszego Porto, a luksusowe skórzane siodełko i uchwyty kierownicy dodają ponadczasowego charakteru.\n\nIdealny na spokojne przejażdżki po winnicach lub brukowanych uliczkach Porto, ten rower łączy funkcjonalność z elegancją. Niezależnie od tego, czy przewozisz butelkę ulubionego rocznika, czy po prostu cieszysz się malowniczą przejażdżką, ten rower zapewnia płynną i stylową jazdę. To nie tylko środek transportu, ale także wyraz dobrego smaku i wyrafinowania."
    img_path1 = str(imgs_path / "WhatsApp Image 2024-10-01 at 10.24.06 (2).jpeg")
    async with AsyncSessionLocal() as session:
        
        mock_bikes = [
            Bike(name="Porto", description=description1, price=599, image_url=img_path1, images=[
                BikeImage(image_url=str(imgs_path / "WhatsApp Image 2024-10-01 at 10.24.06 (2).jpeg")),
                BikeImage(image_url=str(imgs_path / "WhatsApp Image 2024-10-01 at 10.24.06 (3).jpeg"))
            ]),
            Bike(name="Road Bike", description="A lightweight bike for speed", price=899, image_url="/path/to/road-bike.jpg", images=[
                BikeImage(image_url="/path/to/road-bike-1.jpg"),
                BikeImage(image_url="/path/to/road-bike-2.jpg")
            ]),
            Bike(name="Electric Bike", description="A bike with electric assist", price=1499, image_url="/path/to/electric-bike.jpg", images=[
                BikeImage(image_url="/path/to/electric-bike-1.jpg"),
                BikeImage(image_url="/path/to/electric-bike-2.jpg")
            ]),
            Bike(name="Hybrid Bike", description="A versatile bike for city and trail", price=799, image_url="/path/to/hybrid-bike.jpg", images=[
                BikeImage(image_url="/path/to/hybrid-bike-1.jpg"),
                BikeImage(image_url="/path/to/hybrid-bike-2.jpg")
            ])
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
