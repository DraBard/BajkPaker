#!/bin/bash

# Script to upload images to fly.io volume (SQLite version)

# Ensure script exits on error
set -e

# Check for flyctl CLI
if ! command -v flyctl &> /dev/null; then
  echo "Error: flyctl CLI not found. Please install flyctl and try again."
  exit 1
fi

echo "Starting upload of images to fly.io volume"

# Check if the Fly.io app is running and healthy
APP_STATUS=$(flyctl status -a product-service | grep "VM" | grep "started" || true)
if [ -z "$APP_STATUS" ]; then
  echo "Error: Fly.io app 'product-service' has no started VMs or is not healthy."
  echo "Please deploy and ensure the app is running before uploading images."
  echo "You can check the status with: flyctl status -a product-service"
  exit 1
fi

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

# Retry helper for flyctl commands
flyctl_retry() {
  local max_attempts=5
  local attempt=1
  local delay=8
  while [ $attempt -le $max_attempts ]; do
    "$@"
    status=$?
    if [ $status -eq 0 ]; then
      return 0
    fi
    echo "Attempt $attempt/$max_attempts failed. Retrying in $delay seconds..."
    sleep $delay
    attempt=$((attempt + 1))
  done
  echo "Error: Command failed after $max_attempts attempts: $*"
  return 1
}

# Ensure the destination directory exists on fly.io
echo "Ensuring destination directory exists on fly.io..."
flyctl_retry flyctl ssh console -a product-service -C "mkdir -p /data/static/images"

# Count files for progress tracking
FILE_COUNT=$(find "$LOCAL_IMAGES_DIR" -type f | wc -l)
echo "Preparing to upload $FILE_COUNT files..."

# Upload each file individually using flyctl sftp
echo "Uploading images to fly.io instance..."
for img in "$LOCAL_IMAGES_DIR"/*; do
  if [ -f "$img" ]; then
    filename=$(basename "$img")
    echo "Uploading $filename..."
    
    # Create a temporary sftp batch file
    SFTP_COMMANDS=$(mktemp)
    echo "put \"$img\" \"/data/static/images/$filename\"" > "$SFTP_COMMANDS"
    
    # Use flyctl sftp with retry
    flyctl_retry flyctl sftp shell -a product-service < "$SFTP_COMMANDS"
    
    # Remove the temporary file
    rm "$SFTP_COMMANDS"
  fi
done

# Verify the upload by counting files - local pipe fix
echo "Verifying upload..."
UPLOADED_COUNT=$(flyctl_retry flyctl ssh console -a product-service -C "find /data/static/images -type f" | wc -l)
echo "Uploaded $UPLOADED_COUNT of $FILE_COUNT files"

# Set proper permissions
echo "Setting permissions..."
flyctl_retry flyctl ssh console -a product-service -C "chmod -R 755 /data/static/images"

# List the images in the destination directory to confirm
echo "Listing images in destination directory..."
flyctl_retry flyctl ssh console -a product-service -C "ls -l /data/static/images"

echo "Image upload complete!"
echo "Now you need to update the database with bike data and image metadata"
echo "Run: python update_image_metadata.py image_metadata.json"
