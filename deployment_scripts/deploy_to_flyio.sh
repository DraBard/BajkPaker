#!/bin/bash

# Deploy all components to fly.io (SQLite version)
# Author: BajkPaker

# Exit on error - we'll handle errors ourselves
set +e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🚀 Starting deployment from project root: $PROJECT_ROOT"

# Change to project root to ensure relative paths work as expected
cd "$PROJECT_ROOT" || exit 1

# Global error flag
GLOBAL_ERROR=0

# Maximum number of retries for commands
MAX_RETRIES=1

# Function to display step information
step() {
  echo ""
  echo "========================================"
  echo "🔶 STEP $1: $2"
  echo "========================================"
}

# Function to check if a Fly app already exists
check_app_exists() {
  local app_name=$1
  flyctl status -a "$app_name" &>/dev/null
  return $?
}

# Function to check if a volume exists
check_volume_exists() {
  local app_name=$1
  local volume_name=$2
  flyctl volumes list -a "$app_name" 2>/dev/null | grep -q "$volume_name"
  return $?
}

# Function to run a command with retries
run_with_retry() {
  local cmd=$1
  local description=$2
  local retries=0
  local success=false

  echo "🔧 Running: $cmd"
  echo "💻 $description"
  
  while [ $retries -lt $MAX_RETRIES ] && [ "$success" != "true" ]; do
    if [ $retries -gt 0 ]; then
      echo "🔄 Retry attempt $retries of $MAX_RETRIES..."
      sleep 3
    fi
    
    eval "$cmd"
    if [ $? -eq 0 ]; then
      success=true
      echo "✅ Command succeeded!"
    else
      retries=$((retries + 1))
      if [ $retries -ge $MAX_RETRIES ]; then
        echo "❌ Command failed after $MAX_RETRIES attempts."
        return 1
      fi
    fi
  done
  
  return 0
}

# Function to run a command in a specific directory
run_in_dir() {
  local dir=$1
  local command=$2
  local description=$3
  local continue_on_error=${4:-false}
  
  echo "📂 Changing to directory: $dir"
  cd "$PROJECT_ROOT/$dir" || {
    echo "❌ Failed to change to directory: $dir"
    GLOBAL_ERROR=1
    return 1
  }
  
  run_with_retry "$command" "$description"
  local result=$?
  
  if [ $result -ne 0 ]; then
    GLOBAL_ERROR=1
    if [ "$continue_on_error" != "true" ]; then
      cd "$PROJECT_ROOT"
      echo "❌ Failed to execute command in $dir. Exiting."
      exit 1
    else
      echo "⚠️ Command failed but continuing as requested."
    fi
  fi
  
  cd "$PROJECT_ROOT"
  return $result
}

# Function to launch a new fly app with automatic responses to prompts
launch_fly_app() {
  local dir=$1
  local description=$2
  local app_name=$3
  
  echo "📂 Changing to directory: $dir"
  cd "$PROJECT_ROOT/$dir" || {
    echo "❌ Failed to change to directory: $dir"
    GLOBAL_ERROR=1
    return 1
  }
  
  echo "🔧 Running: flyctl launch for $app_name"
  echo "💻 $description"
  
  # Use non-interactive flags to avoid prompts
  flyctl launch --name "$app_name" --region waw --org personal --no-deploy --copy-config --yes
  
  if [ $? -eq 0 ]; then
    echo "✅ App launched successfully!"
    echo "🔧 Now deploying the app..."
    echo "ℹ️  This step may take several minutes while Fly.io builds your Docker image. Please be patient..."
    flyctl deploy --yes --now
    local result=$?
    if [ $result -ne 0 ]; then
      GLOBAL_ERROR=1
      echo "❌ Deployment failed after successful launch."
    else
      echo "✅ Deployment succeeded!"
    fi
  else
    GLOBAL_ERROR=1
    echo "❌ Failed to launch app."
  fi
  
  cd "$PROJECT_ROOT"
}

# Function to verify if an app is accessible
verify_app() {
  local app_name=$1
  local max_attempts=${2:-3}
  local wait_seconds=${3:-10}
  local attempts=0
  
  echo "🔍 Verifying app '$app_name' is accessible..."
  
  while [ $attempts -lt $max_attempts ]; do
    if [ $attempts -gt 0 ]; then
      echo "⏳ Waiting $wait_seconds seconds before retry..."
      sleep $wait_seconds
    fi

    if [ "$app_name" = "product-service" ]; then
      response=$(curl -s --max-time 10 "https://$app_name.fly.dev/healthz")
      if [ "$response" = '{"status":"healthy"}' ]; then
        echo "✅ App '$app_name' is healthy at /healthz"
        return 0
      fi
    else
      if curl -s --head --max-time 10 "https://$app_name.fly.dev" | grep -q "200\|30[1-8]"; then
        echo "✅ App '$app_name' is accessible at https://$app_name.fly.dev"
        return 0
      fi
    fi

    attempts=$((attempts + 1))
    echo "🔄 Attempt $attempts/$max_attempts: App not yet accessible"
  done
  
  echo "⚠️ Could not verify app '$app_name' is accessible after $max_attempts attempts."
  return 1
}

# Deploy Frontend
step 1 "Deploying Frontend"
if check_app_exists "bajkpaker"; then
  echo "🔍 Frontend app 'bajkpaker' already exists."
  echo "🔄 Deploying new version..."
  run_in_dir "frontend" "flyctl deploy --yes --now" "Deploying frontend application" true
  verify_app "bajkpaker" 5 10
else
  echo "🆕 Creating new frontend app..."
  launch_fly_app "frontend" "Launching frontend application" "bajkpaker"
  verify_app "bajkpaker" 5 10
fi

# Deploy Product Service
step 2 "Deploying Product Service"
if check_app_exists "product-service"; then
  echo "🔍 Product service app 'product-service' already exists."
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/product_service" "flyctl deploy --yes --now" "Deploying product service" true
  verify_app "product-service" 5 10
else
  echo "🆕 Creating new product service app..."
  launch_fly_app "backend/services/product_service" "Launching product service" "product-service"
  verify_app "product-service" 5 10
fi

# Deploy Order Service
step 3 "Deploying Order Service"
if check_app_exists "order-processing-service"; then
  echo "🔍 Order service app 'order-processing-service' already exists."
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/order_processing_service" "flyctl deploy --yes --now" "Deploying order service" true
  verify_app "order-processing-service" 5 10
else
  echo "🆕 Creating new order service app..."
  launch_fly_app "backend/services/order_processing_service" "Launching order service" "order-processing-service"
  verify_app "order-processing-service" 5 10
fi

# Create volumes for SQLite databases
step 4 "Creating Volumes for SQLite Databases"

# Product Service volume
if check_app_exists "product-service"; then
  if ! check_volume_exists "product-service" "product_data"; then
    run_in_dir "backend/services/product_service" "flyctl volumes create product_data --size 2 --region waw --yes" "Creating product_data volume" true
  else
    echo "✅ Volume 'product_data' already exists."
  fi
fi

# Order Service volume
if check_app_exists "order-processing-service"; then
  if ! check_volume_exists "order-processing-service" "order_data"; then
    run_in_dir "backend/services/order_processing_service" "flyctl volumes create order_data --size 1 --region waw --yes" "Creating order_data volume" true
  else
    echo "✅ Volume 'order_data' already exists."
  fi
fi

# Upload images to product service volume
step 5 "Uploading Images"
attempt=1
uploaded=false
while [ $attempt -le 5 ] && [ "$uploaded" != "true" ]; do
    echo "🔄 Attempt $attempt of 5: Checking if product-service is healthy..."
    if verify_app "product-service" 1 0; then
        echo "✅ Product service is healthy. Trying to upload images..."
        if run_in_dir "backend/services/product_service/images_upload" "bash upload_images_flyio.sh" "Uploading product images to fly.io volume" true; then
            uploaded=true
            echo "✅ Image upload succeeded on attempt $attempt."
        else
            echo "❌ Image upload failed on attempt $attempt."
        fi
    else
        echo "❌ Product service not healthy on attempt $attempt."
    fi
    if [ "$uploaded" != "true" ]; then
        echo "⏳ Waiting 10 seconds before next attempt..."
        sleep 10
    fi
    attempt=$((attempt + 1))
done
if [ "$uploaded" != "true" ]; then
    echo "❌ All 5 image upload attempts failed. Skipping image upload."
fi

# Initialize SQLite databases on the server
step 6 "Initializing SQLite Databases"
run_in_dir "backend/services/product_service" "flyctl ssh console -a product-service -C 'python /app/init_db.py'" "Initializing product service SQLite database" true
run_in_dir "backend/services/order_processing_service" "flyctl ssh console -a order-processing-service -C 'python /app/init_sqlite_db.py --db-path /data/order_processing_service.db'" "Initializing order service SQLite database" true

# Update product database with image metadata
# Step 7: Updating Product Database with Metadata
# Step 7: Update the command to properly set PYTHONPATH
step 7 "Updating Product Database with Metadata"
run_in_dir "backend/services/product_service" "flyctl ssh console -a product-service -C 'sh -c \"cd /app && PYTHONPATH=/app python /app/images_upload/update_image_metadata.py /app/images_upload/image_metadata.json\"'" "Updating product database with bike and image data" true

echo ""
if [ $GLOBAL_ERROR -eq 0 ]; then
  echo "✅ Deployment completed successfully!"
  echo "🌐 Your application should now be accessible at: https://bajkpaker.fly.dev"
  echo "🔄 Product service should be running at: https://product-service.fly.dev"
  echo "🔄 Order service should be running at: https://order-processing-service.fly.dev"
else
  echo "⚠️ Deployment completed with some errors. Please check the logs above."
  echo "You may still want to manually verify the deployments:"
  echo "🌐 Frontend: https://bajkpaker.fly.dev"
  echo "🔄 Product service: https://product-service.fly.dev"
  echo "🔄 Order service: https://order-processing-service.fly.dev"
fi
echo ""