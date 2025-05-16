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
MAX_RETRIES=3

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
    
    if curl -s --head --max-time 10 "https://$app_name.fly.dev" | grep -q "200\|30[1-8]"; then
      echo "✅ App '$app_name' is accessible at https://$app_name.fly.dev"
      return 0
    else
      attempts=$((attempts + 1))
      echo "🔄 Attempt $attempts/$max_attempts: App not yet accessible"
    fi
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
  verify_app "bajkpaker" 3 20
else
  echo "🆕 Creating new frontend app..."
  launch_fly_app "frontend" "Launching frontend application" "bajkpaker"
  verify_app "bajkpaker" 3 20
fi

# Deploy Product Service
step 2 "Deploying Product Service"
if check_app_exists "product-service"; then
  echo "🔍 Product service app 'product-service' already exists."
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/product_service" "flyctl deploy --yes --now" "Deploying product service" true
  verify_app "product-service" 3 20
else
  echo "🆕 Creating new product service app..."
  launch_fly_app "backend/services/product_service" "Launching product service" "product-service"
  verify_app "product-service" 3 20
fi

# Create volumes for images and SQLite database
step 3 "Creating Volumes"
if check_app_exists "product-service"; then
  # Create images volume
  if ! check_volume_exists "product-service" "product_images"; then
    run_in_dir "backend/services/product_service" "flyctl volumes create product_images --size 1 --region waw --yes" "Creating product_images volume" true
  else
    echo "✅ Volume 'product_images' already exists."
  fi
  
  # Create SQLite data volume
  if ! check_volume_exists "product-service" "product_data"; then
    run_in_dir "backend/services/product_service" "flyctl volumes create product_data --size 1 --region waw --yes" "Creating product_data volume" true
  else
    echo "✅ Volume 'product_data' already exists."
  fi
  
  # Upload images to product service volume
  step 4 "Uploading Images"
  run_in_dir "backend/services/product_service/images_upload" "bash upload_images_flyio.sh" "Uploading product images to fly.io volume" true
  
  # Initialize SQLite database on the server
  step 5 "Initializing SQLite Database"
  run_in_dir "backend/services/product_service" "flyctl ssh console -a product-service -C 'python /app/init_sqlite_db.py'" "Initializing SQLite database" true
  
  # Update database with image metadata
  step 6 "Updating Database with Metadata"
  run_in_dir "backend/services/product_service" "flyctl ssh console -a product-service -C 'cd /app && python images_upload/update_image_metadata.py images_upload/image_metadata.json'" "Updating database with bike and image data" true
else
  echo "❌ Product service app 'product-service' does not exist. Skipping volume creation and setup."
  GLOBAL_ERROR=1
fi

echo ""
if [ $GLOBAL_ERROR -eq 0 ]; then
  echo "✅ Deployment completed successfully!"
  echo "🌐 Your application should now be accessible at: https://bajkpaker.fly.dev"
  echo "🔄 Product service should be running at: https://product-service.fly.dev"
else
  echo "⚠️ Deployment completed with some errors. Please check the logs above."
  echo "You may still want to manually verify the deployments:"
  echo "🌐 Frontend: https://bajkpaker.fly.dev"
  echo "🔄 Product service: https://product-service.fly.dev"
fi
echo ""