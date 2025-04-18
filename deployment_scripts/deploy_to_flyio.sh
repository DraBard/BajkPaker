#!/bin/bash

# Deploy all components to fly.io
# Author: BajkPaker

# Exit on error - we'll handle errors ourselves
set +e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🚀 Starting removal from project root: $PROJECT_ROOT"

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

# Deploy Database
step 2 "Deploying Database"
if check_app_exists "bajkpaker-mysql"; then
  echo "🔍 Database app 'bajkpaker-mysql' already exists."
  echo "🔄 Deploying new version..."
  run_in_dir "backend/database" "flyctl deploy --yes --now" "Deploying MySQL database" true
else
  echo "🆕 Creating new database app..."
  launch_fly_app "backend/database" "Launching MySQL database" "bajkpaker-mysql"
fi

# Deploy Product Service
step 3 "Deploying Product Service"
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

# Make sure the volume exists for the product service
step 4 "Checking and Creating Volume"
if check_app_exists "product-service"; then
  run_in_dir "backend/services/product_service" "flyctl volumes list | grep -q 'product_images' || flyctl volumes create product_images --size 1 --region waw --yes" "Ensuring product_images volume exists" true

  # Upload images to product service volume
  step 5 "Uploading Images"
  if check_app_exists "product-service"; then
    run_in_dir "backend/services/product_service/images_upload" "bash upload_images_flyio.sh" "Uploading product images to fly.io volume" true
  else
    echo "❌ Product service app 'product-service' does not exist. Skipping image upload."
    GLOBAL_ERROR=1
  fi
else
  echo "❌ Product service app 'product-service' does not exist. Skipping volume creation and image upload."
  GLOBAL_ERROR=1
fi

# Start database proxy in a separate terminal
step 6 "Database Proxy Instructions"
echo "📡 Database proxy needs to be run in a separate terminal."
echo ""
echo "⚠️ IMPORTANT: Please run the following command in a separate terminal:"
echo "    flyctl proxy 3306 -a bajkpaker-mysql"
echo "and asure there is no local docker mysql instance running on port 3306."
echo ""
echo "🔍 This will forward the remote MySQL database port to your local machine."
echo "⏱️ After starting the proxy, return to this terminal and press Enter to continue..."

# Wait for user confirmation
read -p "Press Enter after starting the database proxy in a separate terminal... " 

# Check if the database proxy port is accessible
if nc -z -w 5 localhost 3306 2>/dev/null; then
  echo "✅ Database proxy connection detected on port 3306."
  
  # Update database with image metadata
  step 7 "Updating Database"
  run_in_dir "backend/services/product_service/images_upload" "python update_image_metadata.py image_metadata.json" "Updating database with bike and image data" true
else
  echo "❌ Unable to connect to database on port 3306. Please verify:"
  echo "  1. You've started the proxy in another terminal"
  echo "  2. The command executed successfully"
  echo "  3. The database app 'bajkpaker-mysql' exists"
  GLOBAL_ERROR=1
fi

echo ""
echo "⚠️ REMINDER: Don't forget to close the proxy terminal when you're finished."

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