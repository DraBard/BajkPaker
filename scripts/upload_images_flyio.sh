#!/bin/bash

# Script to upload images to fly.io volume

# Ensure script exits on error
set -e

echo "Starting upload of images to fly.io volume"

# Local directory containing your images
LOCAL_IMAGES_DIR="./images_to_upload"

# Create the local directory if it doesn't exist
if [ ! -d "$LOCAL_IMAGES_DIR" ]; then
  echo "Creating local directory '$LOCAL_IMAGES_DIR'..."
  mkdir -p "$LOCAL_IMAGES_DIR"
  echo "Please copy your images to the '$LOCAL_IMAGES_DIR' directory and run this script again."
  exit 1
fi

# Check if the directory is empty
if [ -z "$(ls -A $LOCAL_IMAGES_DIR)" ]; then
  echo "Error: '$LOCAL_IMAGES_DIR' directory is empty. Please add images before running this script."
  exit 1
fi

# Create a temporary directory on the fly.io instance
echo "Creating temporary directory on fly.io instance..."
fly ssh console -a product-service -C "mkdir -p /tmp/images_upload"

# Upload each image using fly ssh sftp shell
echo "Uploading images to fly.io instance..."
for img in "$LOCAL_IMAGES_DIR"/*; do
  if [ -f "$img" ]; then
    filename=$(basename "$img")
    echo "Uploading $filename..."
    
    # Using base64 to transfer binary files through ssh
    base64_content=$(base64 "$img")
    fly ssh console -a product-service -C "echo '$base64_content' | base64 --decode > /tmp/images_upload/'$filename'"
    
    # Verify the file was uploaded
    echo "Verifying upload..."
    fly ssh console -a product-service -C "ls -la /tmp/images_upload/'$filename'"
  fi
done

# Move images from temporary directory to the mounted volume
echo "Moving images to persistent volume..."
fly ssh console -a product-service -C "mkdir -p /app/static/images && cp -r /tmp/images_upload/* /app/static/images/ && chmod -R 755 /app/static/images"

# List the images in the destination directory to confirm
echo "Listing images in destination directory..."
fly ssh console -a product-service -C "ls -la /app/static/images"

# Clean up temporary directory
echo "Cleaning up temporary files..."
fly ssh console -a product-service -C "rm -rf /tmp/images_upload"

echo "Image upload complete!"
echo "Now you need to update the database with image metadata"
