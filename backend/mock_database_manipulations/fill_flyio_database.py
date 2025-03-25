import asyncio
import os
import sys
from pathlib import Path
import time
import socket
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print("Environment variables loaded")

# Add project root to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
print(f"Project root added to path: {project_root}")

# Import shared database models
from backend.database.models import (
    Base,
    Bike,
    BikeImage,
    User,
)

print("Database models imported successfully")

# Database connection parameters
DB_USER = os.getenv("DB_USER", "bajkpaker")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = "127.0.0.1"  # Changed to localhost for use with flyctl proxy
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev")

print(f"Database configuration:")
print(f"- User: {DB_USER}")
print(f"- Host: {DB_HOST}")
print(f"- Port: {DB_PORT}")
print(f"- Database: {DB_NAME}")
print(f"- Password set: {'Yes' if DB_PASSWORD else 'No'}")

if not DB_PASSWORD:
    print("Error: DB_PASSWORD environment variable is not set")
    sys.exit(1)


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


# Build the database URL
print(f"Testing database connection before proceeding...")
if not check_port(DB_HOST, DB_PORT):
    print("\n🚨 Cannot connect to MySQL server! 🚨")
    print("It seems that either:")
    print("1. You need to start a fly.io proxy tunnel first")
    print("2. The MySQL server is not running")
    print("\nPlease try running this command in a separate terminal:")
    print(f"   flyctl proxy {DB_PORT} -a bajkpaker-mysql")
    print("\nThen run this script again.")
    sys.exit(1)

# Build the database URL
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"Database URL: mysql+asyncmy://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Create engine with optimized settings for potentially unstable connections
print("Creating database engine with the following settings:")
print("- pool_recycle: 60 seconds (shorter to avoid stale connections)")
print("- pool_timeout: 10 seconds (shorter timeout)")
print("- pool_pre_ping: True (verify connections before use)")
print("- connect_args: {'connect_timeout': 10} (connection timeout)")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_recycle=60,  # Recycle connections more frequently
    pool_timeout=10,  # Shorter timeout
    pool_pre_ping=True,  # Check connection before use
    connect_args={
        "connect_timeout": 10,  # MySQL connection timeout in seconds
    },
)
print("Database engine created")

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
print("Session factory created")


async def ping_database():
    """Simple function to test database connection with a basic query"""
    try:
        print("Testing database connection with a simple query...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            ping_result = result.scalar()
            print(f"Database ping successful! Result: {ping_result}")
            return True
    except Exception as e:
        print(f"Database ping failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False


async def create_tables():
    """Create all tables in the database if they don't exist"""
    try:
        print(f"Connecting to database at {DB_HOST}:{DB_PORT}...")
        print("Attempting to create tables if they don't exist...")

        # First try a simple ping to verify connection
        if not await ping_database():
            print("Initial connection test failed. Cannot proceed with table creation.")
            raise ConnectionError("Cannot establish database connection")

        async with engine.begin() as conn:
            print("Database connection established")
            print("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")

            # List created tables
            result = await conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"Tables in database: {[table[0] for table in tables]}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        raise


async def check_existing_data():
    """Check if data already exists in the database"""
    try:
        print("Checking if data already exists in the database...")
        async with AsyncSessionLocal() as session:
            print("Executing count query on bikes table...")
            result = await session.execute(text("SELECT COUNT(*) FROM bikes"))
            bike_count = result.scalar()
            print(f"Found {bike_count} existing bikes in the database")

            if bike_count > 0:
                print("Getting sample of existing bike names...")
                result = await session.execute(text("SELECT name FROM bikes LIMIT 3"))
                sample_bikes = result.fetchall()
                print(f"Sample bike names: {[bike[0] for bike in sample_bikes]}")

            return bike_count
    except Exception as e:
        print(f"Error checking existing data: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        return 0


async def add_mock_data():
    """Add mock data to the database"""
    # Check if data already exists
    print("Checking for existing data before insertion...")
    bike_count = await check_existing_data()
    if bike_count > 0:
        print(f"Database already contains {bike_count} bikes. Skipping data insertion.")
        return

    # Define mock data
    print("Preparing mock data for insertion...")
    description1 = "Elegancki Rower dla Konesera Porto\n\nOddaj się wyrafinowaniu tego niezwykłego roweru, stworzonego z myślą o wymagającym koneserze wina Porto. Jego eleganckie linie i design inspirowany stylem vintage oddają istotę klasy i wyrafinowania. Głęboka burgundowa rama nawiązuje do bogatych odcieni najlepszego Porto, a luksusowe skórzane siodełko i uchwyty kierownicy dodają ponadczasowego charakteru.\n\nIdealny na spokojne przejażdżki po winnicach lub brukowanych uliczkach Porto, ten rower łączy funkcjonalność z elegancją. Niezależnie od tego, czy przewozisz butelkę ulubionego rocznika, czy po prostu cieszysz się malowniczą przejażdżką, ten rower zapewnia płynną i stylową jazdę. To nie tylko środek transportu, ale także wyraz dobrego smaku i wyrafinowania."

    mock_bikes = [
        {
            "name": "Porto",
            "description": description1,
            "price": 599,
            "bought": False,
            "images": [
                {"image_url": "/static/images/PortoMain.jpg", "is_main": True},
                {
                    "image_url": "/static/images/WhatsApp Image 2024-10-01 at 10.24.06.jpeg"
                },
                {
                    "image_url": "/static/images/WhatsApp Image 2024-10-01 at 11.18.10 (1).jpeg"
                },
            ],
        },
        {
            "name": "Road Bike",
            "description": "A lightweight bike for speed",
            "price": 899,
            "bought": False,
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
            "bought": False,
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
            "bought": False,
            "images": [
                {"image_url": "/static/images/hybrid-bike-main.jpg", "is_main": True},
                {"image_url": "/static/images/hybrid-bike-1.jpg"},
                {"image_url": "/static/images/hybrid-bike-2.jpg"},
            ],
        },
    ]

    print(f"Prepared {len(mock_bikes)} bikes for insertion")
    for idx, bike in enumerate(mock_bikes, 1):
        print(
            f"  Bike {idx}: {bike['name']} - ${bike['price']} with {len(bike['images'])} images"
        )

    mock_users = [
        {"username": "user1", "password": "password1", "email": "user1@example.com"},
        {"username": "user2", "password": "password2", "email": "user2@example.com"},
    ]
    print(f"Prepared {len(mock_users)} users for insertion")

    try:
        print("Opening database session for data insertion...")
        async with AsyncSessionLocal() as session:
            print("Creating bike objects...")
            # Create bikes with images
            bikes = []
            for bike_data in mock_bikes:
                print(f"Creating bike: {bike_data['name']}")
                bike = Bike(
                    name=bike_data["name"],
                    description=bike_data["description"],
                    price=bike_data["price"],
                    bought=bike_data["bought"],
                    images=[
                        BikeImage(
                            image_url=image["image_url"],
                            is_main=image.get("is_main", False),
                        )
                        for image in bike_data["images"]
                    ],
                )
                bikes.append(bike)
                print(f"  Created bike object with {len(bike_data['images'])} images")

            print("Creating user objects...")
            # Create users
            users = []
            for user_data in mock_users:
                print(f"Creating user: {user_data['username']}")
                user = User(
                    username=user_data["username"],
                    password=user_data["password"],
                    email=user_data["email"],
                )
                users.append(user)
                print(f"  Created user object: {user_data['username']}")

            # Add all objects to the session
            print(f"Adding {len(bikes)} bikes and {len(users)} users to session")
            session.add_all(bikes + users)

            # Commit to the database
            print("Committing all data to database...")
            await session.commit()
            print("Data commit successful!")
            print(
                f"Successfully added {len(bikes)} bikes and {len(users)} users to the database"
            )
    except Exception as e:
        print(f"Error adding mock data: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        print("Stack trace:")
        import traceback

        traceback.print_exc()
        raise


async def main():
    """Main function to create tables and add mock data with retries"""
    print("\n" + "=" * 50)
    print("STARTING FLY.IO DATABASE INITIALIZATION")
    print("=" * 50)

    print("\n⚠️  IMPORTANT CONNECTION NOTICE ⚠️")
    print("This script requires an active flyctl proxy tunnel.")
    print("If you haven't started one yet, please run:")
    print("   flyctl proxy 3306 -a bajkpaker-mysql")
    print("in a separate terminal window.")
    print("=" * 50 + "\n")

    max_retries = 3
    retry_delay = 5  # seconds

    print(f"Maximum retry attempts: {max_retries}")
    print(f"Initial retry delay: {retry_delay} seconds (with exponential backoff)")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n{'='*20} ATTEMPT {attempt} OF {max_retries} {'='*20}")
            print(f"Connecting to database at {DB_HOST}:{DB_PORT}...")
            print("Step 1: Creating tables...")
            await create_tables()
            print("Step 2: Adding mock data...")
            await add_mock_data()
            print("\n" + "=" * 50)
            print("DATABASE SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            return
        except Exception as e:
            print(f"\n{'!'*20} ATTEMPT {attempt} FAILED {'!'*20}")
            print(f"Error: {e}")
            print(f"Error type: {type(e).__name__}")

            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                print(f"Next retry delay increased to {retry_delay} seconds")
            else:
                print("\n" + "=" * 50)
                print("ALL ATTEMPTS FAILED")
                print("=" * 50)
                print("\nPlease check your connection and credentials.")
                print("\nTROUBLESHOOTING TIPS:")
                print("1. Ensure you've started a flyctl tunnel:")
                print(
                    "   Run in a separate terminal: flyctl proxy 3306 -a bajkpaker-mysql"
                )
                print("   Keep that terminal open while running this script")
                print("2. Verify your environment variables are correctly set:")
                print(
                    f"   - DB_HOST should be '127.0.0.1' when using flyctl proxy (current: {DB_HOST})"
                )
                print(
                    f"   - DB_PORT should match the local port from flyctl proxy (current: {DB_PORT})"
                )
                print("3. Check if the fly.io MySQL instance is running:")
                print("   Run: fly status -a bajkpaker-mysql")
                print("4. Examine the fly.io logs:")
                print("   Run: fly logs -a bajkpaker-mysql")
                print("5. Try restarting the database service:")
                print("   Run: fly apps restart bajkpaker-mysql")
                print("6. Test direct MySQL connection with:")
                print("   mysql -h 127.0.0.1 -P 3306 -u bajkpaker -p")
                sys.exit(1)


if __name__ == "__main__":
    start_time = time.time()
    print(f"Script started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        asyncio.run(main())
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Script completed successfully in {execution_time:.2f} seconds")
        print(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnhandled error: {e}")
        print("Stack trace:")
        import traceback

        traceback.print_exc()
        sys.exit(1)
