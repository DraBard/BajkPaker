import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
import yaml
from pathlib import Path
import sys
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
from backend.services.product_service.models import Bike, BikeImage, Base  # Import models


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)
config_path = Path(__file__).resolve().parents[2] / 'config.yaml'
config = load_config(config_path)
DATABASE_URL = config["DATABASE_URL"]

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def add_mock_bikes():
    imgs_path = Path('static/images')
    description1 = "Elegancki Rower dla Konesera Porto\n\nOddaj się wyrafinowaniu tego niezwykłego roweru, stworzonego z myślą o wymagającym koneserze wina Porto. Jego eleganckie linie i design inspirowany stylem vintage oddają istotę klasy i wyrafinowania. Głęboka burgundowa rama nawiązuje do bogatych odcieni najlepszego Porto, a luksusowe skórzane siodełko i uchwyty kierownicy dodają ponadczasowego charakteru.\n\nIdealny na spokojne przejażdżki po winnicach lub brukowanych uliczkach Porto, ten rower łączy funkcjonalność z elegancją. Niezależnie od tego, czy przewozisz butelkę ulubionego rocznika, czy po prostu cieszysz się malowniczą przejażdżką, ten rower zapewnia płynną i stylową jazdę. To nie tylko środek transportu, ale także wyraz dobrego smaku i wyrafinowania."
    img_path11 = str(imgs_path / "PortoMain.jpg")
    img_path12 = str(imgs_path / "WhatsApp Image 2024-10-01 at 10.24.06.jpeg")
    img_path13 = str(imgs_path / "WhatsApp Image 2024-10-01 at 11.18.10 (1).jpeg")
    async with AsyncSessionLocal() as session:
        
        mock_bikes = [
            Bike(name="Porto", description=description1, price=599, images=[
                BikeImage(image_url=f"/{img_path11}", is_main=True),
                BikeImage(image_url=f"/{img_path12}"),
                BikeImage(image_url=f"/{img_path13}")
            ]),
            Bike(name="Road Bike", description="A lightweight bike for speed", price=899, images=[
                BikeImage(image_url="/static/images/road-bike-main.jpg", is_main=True),
                BikeImage(image_url="/static/images/road-bike-1.jpg"),
                BikeImage(image_url="/static/images/road-bike-2.jpg")
            ]),
            Bike(name="Electric Bike", description="A bike with electric assist", price=1499, images=[
                BikeImage(image_url="/static/images/electric-bike-main.jpg", is_main=True),
                BikeImage(image_url="/static/images/electric-bike-1.jpg"),
                BikeImage(image_url="/static/images/electric-bike-2.jpg")
            ]),
            Bike(name="Hybrid Bike", description="A versatile bike for city and trail", price=799, images=[
                BikeImage(image_url="/static/images/hybrid-bike-main.jpg", is_main=True),
                BikeImage(image_url="/static/images/hybrid-bike-1.jpg"),
                BikeImage(image_url="/static/images/hybrid-bike-2.jpg")
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
