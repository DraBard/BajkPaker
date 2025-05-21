import asyncio
import os
import sys
import time
from pathlib import Path
import json
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, delete
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Adjust path resolution for both local and production environments
if os.getenv("ENVIRONMENT") != "development":
    app_dir = Path("/app")  # In production, files are in /app
else:
    app_dir = Path(__file__).resolve().parents[1] # Local development path

sys.path.append(str(app_dir))

from models import Bike, BikeImage, Base  # added Base import

# Environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
SQLITE_PATH = os.getenv("SQLITE_PATH")

# SQLite database path configuration
if SQLITE_PATH:
    DB_PATH = SQLITE_PATH
elif ENVIRONMENT == "production":
    DB_PATH = "/app/product_service.db"
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
else:
    DB_PATH = os.path.join(Path(__file__).parents[1], "product_service.db")

print(f"Using database: {DB_PATH}")


# Add table creation to ensure the required tables exist
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created or already exist.")


# Build the database URL
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# Create engine with SQLite settings
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False},  # Allow multithreaded access
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def verify_database_tables(session):
    """Verify that required database tables exist"""
    try:
        # Check if bikes table exists using model's __tablename__ attribute
        table_bikes = Bike.__tablename__
        result = await session.execute(
            text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_bikes}'"
            )
        )
        if result.scalar() is None:
            print(f"❌ Error: {table_bikes} table does not exist in the database")
            return False

        # Check if bike_images table exists using model's __tablename__ attribute
        table_bike_images = BikeImage.__tablename__
        result = await session.execute(
            text(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_bike_images}'"
            )
        )
        if result.scalar() is None:
            print(f"❌ Error: {table_bike_images} table does not exist in the database")
            return False

        print("✅ Database tables verified")
        return True
    except Exception as e:
        print(f"❌ Error verifying database tables: {e}")
        return False


async def update_bike_and_image_data(metadata_file):
    # Create tables if missing
    await create_tables()

    """Update both bikes and bike_images tables with data from the provided JSON file"""

    # Load metadata from JSON file
    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    print(f"Loaded metadata for {len(metadata)} bikes")

    async with AsyncSessionLocal() as session:
        # First verify database tables exist
        if not await verify_database_tables(session):
            print("Database verification failed. Please check your database schema.")
            return False

        # Process each bike and its images
        for bike_data in metadata:
            bike_id = bike_data["bike_id"]
            images = bike_data["images"]
            bike_details = bike_data.get("bike_data", {})

            print(f"Processing bike ID {bike_id}")

            try:
                # Map JSON fields to the correct database model fields
                mapped_bike_details = {
                    "id": bike_id,
                    "name": bike_details.get("name"),
                    "description": bike_details.get("description"),
                    # Use price directly from JSON instead of price_per_day
                    "price": bike_details.get("price"),
                    # Add bought field if it exists in the JSON
                    "bought": bike_details.get("bought", False),
                }

                # Add other fields that exist in the model if needed
                # If the Bike model has a type field
                if "type" in bike_details and hasattr(Bike, "type"):
                    mapped_bike_details["type"] = bike_details["type"]

                # If the Bike model has a size field
                if "size" in bike_details and hasattr(Bike, "size"):
                    mapped_bike_details["size"] = bike_details["size"]

                # If the Bike model has a brand field
                if "brand" in bike_details and hasattr(Bike, "brand"):
                    mapped_bike_details["brand"] = bike_details["brand"]

                # If the Bike model has is_electric field
                if "is_electric" in bike_details and hasattr(Bike, "is_electric"):
                    mapped_bike_details["is_electric"] = bike_details["is_electric"]

                # Check if bike exists
                bike = await session.get(Bike, bike_id)

                if bike:
                    print(f"  Updating existing bike with ID {bike_id}")
                    # Update existing bike with new mapped data
                    for key, value in mapped_bike_details.items():
                        if key != "id" and hasattr(bike, key):  # Skip the ID field
                            setattr(bike, key, value)
                else:
                    print(f"  Creating new bike with ID {bike_id}")
                    # Create new bike record with mapped fields
                    bike = Bike(**mapped_bike_details)
                    session.add(bike)

                # Delete existing images for this bike to avoid duplicates
                await session.execute(
                    delete(BikeImage).where(BikeImage.bike_id == bike_id)
                )
                print(f"  Cleared existing images for bike ID {bike_id}")

                # Add each image to the database
                for image_data in images:
                    image_url = image_data["image_url"]
                    is_main = image_data.get("is_main", False)

                    # Create new image record
                    image = BikeImage(
                        bike_id=bike_id, image_url=image_url, is_main=is_main
                    )

                    session.add(image)
                    print(f"  Added image: {image_url} (Main: {is_main})")

                # Commit changes for each bike separately to isolate potential issues
                await session.commit()

                # Verify bike and images were actually saved
                saved_bike = await session.get(Bike, bike_id)
                if not saved_bike:
                    print(f"⚠️ Warning: Bike ID {bike_id} not found after commit!")
                else:
                    print(f"✅ Successfully saved/updated bike ID {bike_id}")

                result = await session.execute(
                    select(BikeImage).where(BikeImage.bike_id == bike_id)
                )
                saved_images = result.scalars().all()
                if not saved_images:
                    print(
                        f"⚠️ Warning: No images found for bike ID {bike_id} after commit!"
                    )
                else:
                    print(
                        f"✅ Successfully saved {len(saved_images)} images for bike ID {bike_id}"
                    )

            except Exception as e:
                await session.rollback()
                print(f"❌ Error processing bike ID {bike_id}: {e}")
                import traceback

                traceback.print_exc()

        print("All bike and image data processing completed")
        return True


async def main():
    """Main function to update bike and image data in the database"""
    if len(sys.argv) < 2:
        print("No metadata file specified, using default: image_metadata.json")
        metadata_file = "image_metadata.json"
    else:
        metadata_file = sys.argv[1]

    # Ensure file path is correct
    if not os.path.exists(metadata_file):
        # Try with relative path from current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        alternative_path = os.path.join(current_dir, metadata_file)
        if os.path.exists(alternative_path):
            metadata_file = alternative_path
        else:
            print(
                f"Error: Metadata file not found at '{metadata_file}' or '{alternative_path}'"
            )
            return 1  # Return error code instead of sys.exit

    print(f"Using metadata file: {metadata_file}")

    try:
        success = await update_bike_and_image_data(metadata_file)
        if success:
            print("✅ Bike and image data update completed successfully")
            return 0
        else:
            print("❌ Bike and image data update failed")
            return 1
    except Exception as e:
        print(f"❌ Error updating bike and image data: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
