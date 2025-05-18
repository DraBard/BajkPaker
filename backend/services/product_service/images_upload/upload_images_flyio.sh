#!/bin/bash

# Script to upload product images to Fly.io volume
# Author: BajkPaker

set -e  # Exit on error

# Find the script directory
SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR" || exit 1

# Display header
echo "========================================"
echo "🖼️  Product Images Upload to Fly.io Volume"
echo "========================================"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl is not installed. Please install it first."
    echo "Visit: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
fi

# Check if product-service exists
echo "🔍 Checking if product-service exists on Fly.io..."
if flyctl status -a product-service &> /dev/null; then
    echo "✅ product-service found on Fly.io"
else
    echo "❌ Error: product-service not found on Fly.io."
    echo "Please deploy the product service first."
    exit 1
fi

# Check if product_images volume exists
echo "🔍 Checking if product_images volume exists..."
if flyctl volumes list -a product-service | grep -q "product_images"; then
    echo "✅ product_images volume found"
else
    echo "❌ Error: product_images volume not found."
    echo "Creating volume product_images..."
    flyctl volumes create product_images --size 1 --region waw -a product-service
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create volume."
        exit 1
    fi
    echo "✅ product_images volume created"
fi

# Check if local images directory exists
echo "🔍 Checking for local images directory..."
if [ ! -d "./images" ]; then
    echo "ℹ️ Local images directory not found. Creating it..."
    mkdir -p ./images
    echo "✅ Created local images directory"
else
    echo "✅ Local images directory found"
fi

# Check if we have any images to upload
if [ ! "$(ls -A ./images)" ]; then
    echo "⚠️ No images found in the images directory."
    echo "Please copy your product images to the ./images directory before running this script."
    
    # Example images to help user understand what's needed
    echo "ℹ️ Creating example image for testing purposes..."
    echo "This is an example image file" > ./images/example_bike_1.jpg
    echo "This is an example image file" > ./images/example_bike_2.jpg
    echo "✅ Created example images"
fi

# Count how many images we're uploading
IMAGE_COUNT=$(ls -1 ./images | wc -l | tr -d ' ')
echo "📊 Found $IMAGE_COUNT images to upload"

# Upload images to Fly.io volume using SSH
echo "🔼 Uploading images to Fly.io volume..."
echo "(This may take some time depending on the number and size of images)"

# Create the remote directory if it doesn't exist
flyctl ssh console -a product-service -C "mkdir -p /app/images"

# Use flyctl sftp to upload all images
for image in ./images/*; do
    filename=$(basename "$image")
    echo "⬆️ Uploading $filename..."
    
    # Use flyctl sftp to upload the file
    echo "put $image /app/images/$filename" | flyctl sftp shell -a product-service
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully uploaded $filename"
    else
        echo "⚠️ Warning: Failed to upload $filename, trying alternative method..."
        
        # Alternative upload method using SSH and base64
        cat "$image" | base64 | flyctl ssh console -a product-service -C "cat | base64 -d > /app/images/$filename"
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully uploaded $filename using alternative method"
        else
            echo "❌ Failed to upload $filename"
        fi
    fi
done

# Update database with image metadata
echo ""
echo "🗄️ Updating database with image metadata..."

# Check if metadata file exists
if [ ! -f "image_metadata.json" ]; then
    echo "⚠️ Warning: image_metadata.json not found, creating a sample file..."
    cat > image_metadata.json << EOF
{
  "bikes": [
    {
      "name": "Example Mountain Bike",
      "price": 1299,
      "description": "This is an example mountain bike for testing purposes.",
      "images": [
        {"image_url": "/app/images/example_bike_1.jpg", "is_main": true},
        {"image_url": "/app/images/example_bike_2.jpg", "is_main": false}
      ]
    }
  ]
}
EOF
    echo "✅ Created sample metadata file"
fi

# Update the database using SSH command to run the script directly on the server
echo "📝 Running database update on server..."

# Execute Python code directly on the server to update SQLite database
flyctl ssh console -a product-service -C "python -c \"
import json
import os
import sqlite3
from pathlib import Path

# Configure SQLite database path
DATA_DIR = '/data'
DB_PATH = os.path.join(DATA_DIR, 'bajkpaker_dev.db')

# Check if database exists
if not os.path.exists(DB_PATH):
    print('❌ Database not found. Please initialize the database first.')
    exit(1)

# Load metadata from file
metadata_path = '/app/images_upload/image_metadata.json'
if not os.path.exists(metadata_path):
    metadata_path = '/app/services/product_service/images_upload/image_metadata.json'
    if not os.path.exists(metadata_path):
        print('❌ Metadata file not found in expected locations.')
        exit(1)

with open(metadata_path, 'r') as f:
    data = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Process each bike and its images
for bike in data.get('bikes', []):
    # Add bike to database
    try:
        cursor.execute(
            'INSERT INTO bikes (name, price, description, bought) VALUES (?, ?, ?, ?) RETURNING id',
            (bike['name'], bike['price'], bike['description'], False)
        )
        bike_id = cursor.fetchone()[0]
        print(f'✅ Added bike: {bike[\"name\"]} with ID {bike_id}')
        
        # Add images for this bike
        for img in bike.get('images', []):
            cursor.execute(
                'INSERT INTO bike_images (bike_id, image_url, is_main) VALUES (?, ?, ?)',
                (bike_id, img['image_url'], img['is_main'])
            )
        
        print(f'✅ Added {len(bike.get(\"images\", []))} images for bike ID {bike_id}')
    except Exception as e:
        print(f'❌ Error adding bike {bike[\"name\"]}: {str(e)}')

# Commit changes
conn.commit()
conn.close()
print('✅ Database update completed')
\""

echo ""
echo "🎉 Upload process completed!"
echo "🔍 Verify the images are correctly displayed in your application."
