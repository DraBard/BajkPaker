#!/bin/bash
# filepath: /Users/bartlomiejpalus/Documents/Projects/BajkPaker/scripts/verify_image_paths.sh

# Set up error handling
set -e

echo "Starting image path verification..."

# Check if the volume is properly mounted on the server
echo "1. Checking volume mount..."
fly ssh console -a product-service -C "ls -la /app/static/images"

# Check the actual files in the volume
echo "2. Listing actual image files on the server..."
fly ssh console -a product-service -C "find /app/static/images -type f | sort"

# Check the database entries for image paths
echo "3. Retrieving image paths from the database..."
fly ssh console -a product-service -C "mysql -u bajkpaker -p\$DB_PASSWORD bajkpaker_dev -e 'SELECT id, bike_id, image_url FROM bike_images;'"

# Try to access one image directly via curl to test serving
echo "4. Testing image access via HTTP..."
fly ssh console -a product-service -C "curl -s -I https://product-service.fly.dev/static/images/PortoMain.jpg"

echo "5. Verifying FastAPI static files configuration..."
fly ssh console -a product-service -C "grep -r 'StaticFiles' /app"

echo "Verification complete. Check the output above for discrepancies between database paths and actual file locations."
echo "If the paths match but images still don't display, check for CORS issues or FastAPI static file serving configuration."