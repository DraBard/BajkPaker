#!/bin/bash

# Script to upload images to fly.io volume

# Ensure script exits on error
set -e

echo "Starting upload of images to fly.io volume"

# Local directory containing your images
LOCAL_IMAGES_DIR="./static/images"

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

# Ensure the destination directory exists on fly.io
echo "Ensuring destination directory exists on fly.io..."
fly ssh console -a product-service -C "mkdir -p /app/static/images"

# Count files for progress tracking
FILE_COUNT=$(find "$LOCAL_IMAGES_DIR" -type f | wc -l)
echo "Preparing to upload $FILE_COUNT files..."

# Upload each file individually using fly sftp
echo "Uploading images to fly.io instance..."
for img in "$LOCAL_IMAGES_DIR"/*; do
  if [ -f "$img" ]; then
    filename=$(basename "$img")
    echo "Uploading $filename..."
    
    # Create a temporary sftp batch file
    SFTP_COMMANDS=$(mktemp)
    echo "put \"$img\" \"/app/static/images/$filename\"" > "$SFTP_COMMANDS"
    
    # Execute the sftp commands
    fly sftp shell -a product-service < "$SFTP_COMMANDS"
    
    # Remove the temporary file
    rm "$SFTP_COMMANDS"
  fi
done

# Verify the upload by counting files - local pipe fix
echo "Verifying upload..."
UPLOADED_COUNT=$(fly ssh console -a product-service -C "find /app/static/images -type f" | wc -l)
echo "Uploaded $UPLOADED_COUNT of $FILE_COUNT files"

# Set proper permissions
echo "Setting permissions..."
fly ssh console -a product-service -C "chmod -R 755 /app/static/images"

# List the images in the destination directory to confirm
echo "Listing images in destination directory..."
fly ssh console -a product-service -C "ls -l /app/static/images"

echo "Image upload complete!"
echo "Now you need to update the database with bike data and image metadata"
echo "Run: python update_image_metadata.py image_metadata.json"
