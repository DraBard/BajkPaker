import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# Import shared database models
from backend.shared_database.models import Base, Bike, BikeImage


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config_path = Path(__file__).resolve().parents[2] / "config.yaml"
config = load_config(config_path)
DATABASE_URL = config["database_dev"]["url"]

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_mock_bikes():
    imgs_path = Path("static/images")
    description1 = "Elegancki Rower dla Konesera Porto\n\nOddaj się wyrafinowaniu tego niezwykłego roweru, stworzonego z myślą o wymagającym koneserze wina Porto. Jego eleganckie linie i design inspirowany stylem vintage oddają istotę klasy i wyrafinowania. Głęboka burgundowa rama nawiązuje do bogatych odcieni najlepszego Porto, a luksusowe skórzane siodełko i uchwyty kierownicy dodają ponadczasowego charakteru.\n\nIdealny na spokojne przejażdżki po winnicach lub brukowanych uliczkach Porto, ten rower łączy funkcjonalność z elegancją. Niezależnie od tego, czy przewozisz butelkę ulubionego rocznika, czy po prostu cieszysz się malowniczą przejażdżką, ten rower zapewnia płynną i stylową jazdę. To nie tylko środek transportu, ale także wyraz dobrego smaku i wyrafinowania."
    img_path11 = str(imgs_path / "PortoMain.jpg")
    img_path12 = str(imgs_path / "WhatsApp Image 2024-10-01 at 10.24.06.jpeg")
    img_path13 = str(imgs_path / "WhatsApp Image 2024-10-01 at 11.18.10 (1).jpeg")

    mock_bikes = [
        {
            "name": "Porto",
            "description": description1,
            "price": 599,
            "images": [
                {"image_url": f"/{img_path11}", "is_main": True},
                {"image_url": f"/{img_path12}"},
                {"image_url": f"/{img_path13}"},
            ],
        },
        {
            "name": "Road Bike",
            "description": "A lightweight bike for speed",
            "price": 899,
            "images": [
                {"image_url": "/static/images/road-bike-main.jpg", "is_main": True},
                {"image_url": "/static/images/road-bike-1.jpg"},
                {"image_url": "/static/images/road-bike-2.jpg"},
            ],
        },
        {
            "name": "Electric Bike",
            "description": "A bike with electric assist",
            "price": 1499,
            "images": [
                {"image_url": "/static/images/electric-bike-main.jpg", "is_main": True},
                {"image_url": "/static/images/electric-bike-1.jpg"},
                {"image_url": "/static/images/electric-bike-2.jpg"},
            ],
        },
        {
            "name": "Hybrid Bike",
            "description": "A versatile bike for city and trail",
            "price": 799,
            "images": [
                {"image_url": "/static/images/hybrid-bike-main.jpg", "is_main": True},
                {"image_url": "/static/images/hybrid-bike-1.jpg"},
                {"image_url": "/static/images/hybrid-bike-2.jpg"},
            ],
        },
    ]

    async with AsyncSessionLocal() as session:
        bikes = []
        for bike_data in mock_bikes:
            bike = Bike(
                name=bike_data["name"],
                description=bike_data["description"],
                price=bike_data["price"],
                images=[
                    BikeImage(
                        image_url=image["image_url"],
                        is_main=image.get("is_main", False),
                    )
                    for image in bike_data["images"]
                ],
            )
            bikes.append(bike)

        session.add_all(bikes)
        await session.commit()
        print("Mock bikes added to database")


async def main():
    await create_tables()  # Create the tables in the single database
    await add_mock_bikes()  # Insert mock data into the database


if __name__ == "__main__":
    asyncio.run(main())
