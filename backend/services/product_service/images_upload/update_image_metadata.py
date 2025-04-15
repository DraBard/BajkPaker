import asyncio
import os
import sys
import socket
import time
from pathlib import Path
import json
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, delete, update
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.append(str(project_root))

# Import shared database models
from database.models import Bike, BikeImage

# Database connection parameters
DB_USER = os.getenv("DB_USER", "bajkpaker")
DB_PASSWORD = os.getenv("DB_PASSWORD")
# For local development with flyctl proxy, use localhost/127.0.0.1 instead of internal hostname
is_local = True  # Set this to True when running locally
DB_HOST = "127.0.0.1" if is_local else os.getenv("DB_HOST", "bajkpaker-mysql.internal")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev")

print(f"Environment: {'Local development' if is_local else 'Production'}")
print(f"Using database: mysql+asyncmy://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

if is_local:
    print("\n⚠️  IMPORTANT CONNECTION NOTICE ⚠️")
    print("This script requires an active flyctl proxy tunnel.")
    print("If you haven't started one yet, please run:")
    print("   flyctl proxy 3306 -a bajkpaker-mysql")
    print("in a separate terminal window.\n")

    # Check if the port is reachable before proceeding
    def check_port(host, port, timeout=5):
        print(f"Testing connection to {host}:{port} (timeout: {timeout}s)...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            if result == 0:
                print(f"✅ Connection to {host}:{port} successful!")
                sock.close()
                return True
            else:
                print(f"❌ Connection to {host}:{port} failed (error code: {result})")
                return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
        finally:
            sock.close()

    # Test connection before proceeding
    if not check_port(DB_HOST, DB_PORT):
        print("\n🚨 Cannot connect to MySQL server! 🚨")
        print("Please start a fly.io proxy tunnel first:")
        print(f"   flyctl proxy {DB_PORT} -a bajkpaker-mysql")
        sys.exit(1)

# Build the database URL
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=60,  # Recycle connections more frequently
    pool_timeout=10,  # Shorter timeout
    pool_pre_ping=True,  # Check connection before use
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def verify_database_tables(session):
    """Verify that required database tables exist"""
    try:
        # Check if bikes table exists
        result = await session.execute(text("SHOW TABLES LIKE 'bikes'"))
        if result.scalar() is None:
            print("❌ Error: bikes table does not exist in the database")
            return False

        # Check if bike_images table exists
        result = await session.execute(text("SHOW TABLES LIKE 'bike_images'"))
        if result.scalar() is None:
            print("❌ Error: bike_images table does not exist in the database")
            return False

        print("✅ Database tables verified")
        return True
    except Exception as e:
        print(f"❌ Error verifying database tables: {e}")
        return False


async def update_bike_and_image_data(metadata_file):
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
            sys.exit(1)

    print(f"Using metadata file: {metadata_file}")

    try:
        success = await update_bike_and_image_data(metadata_file)
        if success:
            print("✅ Bike and image data update completed successfully")
        else:
            print("❌ Bike and image data update failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error updating bike and image data: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
