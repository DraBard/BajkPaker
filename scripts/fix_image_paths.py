#!/usr/bin/env python3
import os
import sys
import mimetypes
import argparse
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update
from pathlib import Path
import subprocess

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# Import database models if available
try:
    from backend.database.models import BikeImage
except ImportError:
    print("WARNING: Could not import BikeImage model, will use raw SQL")
    BikeImage = None

# Register image MIME types
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/gif", ".gif")

# Command-line arguments
parser = argparse.ArgumentParser(description="Fix image paths in BajkPaker database")
parser.add_argument(
    "--dry-run", action="store_true", help="Check issues without making changes"
)
parser.add_argument(
    "--local", action="store_true", help="Run locally using flyctl proxy"
)
parser.add_argument(
    "--image-dir", default="./static/images", help="Local image directory path"
)
parser.add_argument("--db-user", default="bajkpaker", help="Database username")
parser.add_argument(
    "--db-password", help="Database password (omit to use DB_PASSWORD env var)"
)
parser.add_argument("--db-host", help="Database host")
parser.add_argument("--db-port", default="3306", help="Database port")
parser.add_argument("--db-name", default="bajkpaker_dev", help="Database name")

args = parser.parse_args()

# Get database connection details
db_user = args.db_user
db_password = args.db_password or os.environ.get("DB_PASSWORD")
db_host = args.db_host or ("127.0.0.1" if args.local else "bajkpaker-mysql.internal")
db_port = args.db_port
db_name = args.db_name

if not db_password:
    print(
        "ERROR: Database password not provided. Use --db-password or set DB_PASSWORD env var"
    )
    sys.exit(1)

# Build the database URL
DATABASE_URL = f"mysql+asyncmy://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
print(f"Database URL: mysql+asyncmy://{db_user}:****@{db_host}:{db_port}/{db_name}")

# Create engine with optimized settings
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for debugging SQL queries
    pool_pre_ping=True,  # Check connection before use
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def check_database_connection():
    """Test the database connection"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                print("✅ Database connection successful")
                return True
            return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def get_image_paths_from_db():
    """Get all image paths from the database"""
    try:
        async with AsyncSessionLocal() as session:
            if BikeImage:
                # Use SQLAlchemy model
                result = await session.execute(select(BikeImage))
                images = result.scalars().all()
                return [
                    {
                        "id": img.id,
                        "bike_id": img.bike_id,
                        "image_url": img.image_url,
                        "is_main": img.is_main,
                    }
                    for img in images
                ]
            else:
                # Use raw SQL
                result = await session.execute(
                    text("SELECT id, bike_id, image_url, is_main FROM bike_images")
                )
                return [dict(row) for row in result]
    except Exception as e:
        print(f"❌ Error fetching image paths: {e}")
        return []


def check_image_on_server(image_path):
    """Check if an image exists on the server using fly ssh"""
    try:
        # Remove leading slash if present for path construction
        if image_path.startswith("/"):
            server_path = f"/app{image_path}"
        else:
            server_path = f"/app/{image_path}"

        # Run command to check if file exists
        result = subprocess.run(
            [
                "fly",
                "ssh",
                "console",
                "-a",
                "product-service",
                "-C",
                f"test -f '{server_path}' && echo 'exists' || echo 'missing'",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return "exists" in result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking file on server: {e}")
        print(f"Command output: {e.stdout} {e.stderr}")
        return False


async def update_image_path(image_id, new_path):
    """Update an image path in the database"""
    if args.dry_run:
        print(f"Would update image ID {image_id} to path: {new_path}")
        return True

    try:
        async with AsyncSessionLocal() as session:
            if BikeImage:
                # Use SQLAlchemy model
                result = await session.execute(
                    select(BikeImage).where(BikeImage.id == image_id)
                )
                image = result.scalar_one_or_none()
                if image:
                    image.image_url = new_path
                    await session.commit()
                    return True
            else:
                # Use raw SQL
                await session.execute(
                    text("UPDATE bike_images SET image_url = :path WHERE id = :id"),
                    {"path": new_path, "id": image_id},
                )
                await session.commit()
                return True
    except Exception as e:
        print(f"❌ Error updating image path: {e}")
        return False


async def fix_image_paths():
    """Main function to check and fix image paths"""
    # First check database connection
    if not await check_database_connection():
        print("Exiting due to database connection failure")
        return

    # Get all image paths from database
    print("Fetching image paths from database...")
    images = await get_image_paths_from_db()
    print(f"Found {len(images)} images in database")

    issues_found = 0
    fixes_applied = 0

    # Check each image
    for img in images:
        image_id = img["id"]
        bike_id = img["bike_id"]
        image_url = img["image_url"]
        is_main = img["is_main"]

        print(f"\nChecking image ID {image_id} (Bike ID {bike_id}):")
        print(f"  Path: {image_url}")
        print(f"  Is main: {is_main}")

        # 1. Check if path starts correctly
        if not image_url.startswith("/static/images/"):
            issues_found += 1
            print(f"❌ Path doesn't start with /static/images/: {image_url}")

            # Try to fix by adding prefix
            filename = os.path.basename(image_url)
            new_path = f"/static/images/{filename}"
            print(f"  Suggested fix: {new_path}")

            if await update_image_path(image_id, new_path):
                fixes_applied += 1
                print(f"✅ Updated path for image ID {image_id}")
                # Update for further checks
                image_url = new_path

        # 2. Check if image exists on server
        if not args.local:
            exists = check_image_on_server(image_url)
            if not exists:
                issues_found += 1
                print(f"❌ Image file not found on server: {image_url}")
                print(
                    f"  You may need to upload this file using upload_images_flyio.sh"
                )

        # 3. Validate file extension and MIME type
        ext = os.path.splitext(image_url)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            issues_found += 1
            print(f"❌ Unrecognized or missing file extension: {ext}")
        else:
            mime_type = mimetypes.types_map.get(ext)
            print(f"  File extension: {ext}, MIME type: {mime_type}")

    # Summary
    print("\n--- SUMMARY ---")
    print(f"Total images checked: {len(images)}")
    print(f"Issues found: {issues_found}")
    print(f"Fixes applied: {fixes_applied}")

    if args.dry_run and issues_found > 0:
        print("\nThis was a DRY RUN. Run without --dry-run to apply fixes.")

    if issues_found == 0:
        print("\n✅ All image paths appear to be correct!")
    elif fixes_applied == issues_found:
        print("\n✅ All issues fixed!")
    else:
        print(
            f"\n⚠️ {issues_found - fixes_applied} issues could not be automatically fixed."
        )
        print("You may need to manually upload missing images or fix database entries.")


if __name__ == "__main__":
    if args.local:
        print("Running in local mode using flyctl proxy")
        print("Make sure you have an active flyctl proxy running:")
        print("  flyctl proxy 3306 -a bajkpaker-mysql")

    print(f"Image directory: {args.image_dir}")
    print(f"Dry run: {args.dry_run}")

    asyncio.run(fix_image_paths())
