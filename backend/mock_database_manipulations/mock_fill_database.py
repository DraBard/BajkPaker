import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import yaml
from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
from backend.services.product_service.models import (
    Bike as ProductBike,
    BikeImage as ProductBikeImage,
    Base as ProductBase,
)  # Import models from product_service
from backend.services.order_service.models import (
    Bike as OrderBike,
    BikeImage as OrderBikeImage,
    Base as OrderBase,
)  # Import models from order_service


def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


config_path = Path(__file__).resolve().parents[2] / "config.yaml"
config = load_config(config_path)
DATABASE_URL_PRODUCT = config["database_product_dev"]["url"]
DATABASE_URL_ORDER = config["database_order_dev"]["url"]

engine_product = create_async_engine(DATABASE_URL_PRODUCT, echo=True)
AsyncSessionLocalProduct = sessionmaker(
    engine_product, class_=AsyncSession, expire_on_commit=False
)

engine_order = create_async_engine(DATABASE_URL_ORDER, echo=True)
AsyncSessionLocalOrder = sessionmaker(
    engine_order, class_=AsyncSession, expire_on_commit=False
)


async def create_tables(engine, Base):
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

    async with AsyncSessionLocalProduct() as session_product, AsyncSessionLocalOrder() as session_order:
        product_bikes = []
        order_bikes = []

        for bike in mock_bikes:
            product_bike = ProductBike(
                name=bike["name"],
                description=bike["description"],
                price=bike["price"],
                images=[
                    ProductBikeImage(
                        image_url=image["image_url"],
                        is_main=image.get("is_main", False),
                    )
                    for image in bike["images"]
                ],
            )
            order_bike = OrderBike(
                name=bike["name"],
                description=bike["description"],
                price=bike["price"],
                images=[
                    OrderBikeImage(
                        image_url=image["image_url"],
                        is_main=image.get("is_main", False),
                    )
                    for image in bike["images"]
                ],
            )
            product_bikes.append(product_bike)
            order_bikes.append(order_bike)

        session_product.add_all(product_bikes)
        session_order.add_all(order_bikes)

        await session_product.commit()
        await session_order.commit()

        print("Mock bikes added to both product and order databases")


# Main function to run the database setup and data population
async def main():
    await create_tables(
        engine_product, ProductBase
    )  # Create the tables in the product database
    await create_tables(
        engine_order, OrderBase
    )  # Create the tables in the order database
    await add_mock_bikes()  # Insert mock data into the databases


# Running the script
if __name__ == "__main__":
    asyncio.run(main())
