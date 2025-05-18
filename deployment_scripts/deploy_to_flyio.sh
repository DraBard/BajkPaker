#!/bin/bash

# Deploy all components to fly.io with SQLite instead of MySQL
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

# Function to prepare service for deployment
prepare_service_for_deployment() {
  local service_dir=$1
  
  echo "📦 Preparing $service_dir for deployment..."
  
  # Create local copy of database directory
  echo "📂 Creating local copy of database directory..."
  mkdir -p "$PROJECT_ROOT/$service_dir/database_local"
  cp -r "$PROJECT_ROOT/backend/database/"* "$PROJECT_ROOT/$service_dir/database_local/"
  
  echo "✅ Service $service_dir prepared for deployment!"
  return 0
}

# Function to create volume for SQLite database
create_sqlite_volume() {
  local app_name=$1
  
  echo "📦 Creating SQLite volume for $app_name"
  
  flyctl volumes list -a "$app_name" | grep -q "sqlite_data" || flyctl volumes create sqlite_data --size 1 --region waw -a "$app_name" --yes
  
  if [ $? -eq 0 ]; then
    echo "✅ SQLite volume created or already exists!"
    return 0
  else
    echo "❌ Failed to create SQLite volume."
    return 1
  fi
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

# Initialize SQLite database script
step 2 "Preparing services to use SQLite"
echo "🔧 Adding aiosqlite to requirements files..."

# Update requirements files to include SQLite driver
for service_dir in backend/services/*/; do
  if [ -f "$service_dir/requirements.txt" ]; then
    echo "Updating $service_dir/requirements.txt"
    if ! grep -q "aiosqlite" "$service_dir/requirements.txt"; then
      echo "aiosqlite==0.19.0" >> "$service_dir/requirements.txt"
    fi
  fi
done

# Deploy Product Service with SQLite
step 3 "Deploying Product Service with SQLite"
if check_app_exists "product-service"; then
  echo "🔍 Product service app 'product-service' already exists."
  
  # Create SQLite volume if it doesn't exist
  create_sqlite_volume "product-service"
  
  # Prepare service for deployment
  prepare_service_for_deployment "backend/services/product_service"
  
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/product_service" "flyctl deploy --yes --now" "Deploying product service with SQLite" true
  verify_app "product-service" 3 20
else
  echo "🆕 Creating new product service app..."
  
  # Prepare service for deployment
  prepare_service_for_deployment "backend/services/product_service"
  
  launch_fly_app "backend/services/product_service" "Launching product service" "product-service"
  
  # Create SQLite volume after app is launched
  create_sqlite_volume "product-service"
  
  # Deploy again to use the volume
  run_in_dir "backend/services/product_service" "flyctl deploy --yes --now" "Deploying product service with SQLite volume" true
  verify_app "product-service" 3 20
fi

# Make sure the volume exists for the product service images
step 4 "Setting Up Image Volume"
if check_app_exists "product-service"; then
  run_in_dir "backend/services/product_service" "flyctl volumes list | grep -q 'product_images' || flyctl volumes create product_images --size 1 --region waw --yes" "Ensuring product_images volume exists" true

  # Initialize database for Product Service
  step 8 "Initializing SQLite Database for Product Service"
  echo "📝 Executing database initialization for product service..."

  # Use flyctl ssh console to run the database initialization for product service only
  for service in "product-service"; do
    if check_app_exists "$service"; then
      echo "🔧 Initializing database for $service..."
      flyctl ssh console -a "$service" -C "python -c \"
import sys, os, sqlite3
from pathlib import Path

DATA_DIR = '/data'
DB_PATH = os.path.join(DATA_DIR, 'bajkpaker_dev.db')

# Read schema file
schema_path = './database/init-scripts/01-schema.sql'
if not os.path.exists(schema_path):
    print('Schema file not found')
    sys.exit(1)

with open(schema_path, 'r') as f:
    schema_sql = f.read()

# Create database
conn = sqlite3.connect(DB_PATH)
try:
    conn.executescript(schema_sql)
    conn.commit()
    print('Database initialized successfully!')
except Exception as e:
    print(f'Error: {e}')
    conn.rollback()
finally:
    conn.close()
\""
    fi
  done

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

# Deploy User Service with SQLite
step 6 "Deploying User Service with SQLite"
if check_app_exists "user-service"; then
  echo "🔍 User service app 'user-service' already exists."
  
  # Create SQLite volume if it doesn't exist
  create_sqlite_volume "user-service"
  
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/user_service" "flyctl deploy --yes --now" "Deploying user service with SQLite" true
  verify_app "user-service" 3 20
else
  echo "🆕 Creating new user service app..."
  # Prepare service for deployment
  prepare_service_for_deployment "backend/services/user_service"
  
  launch_fly_app "backend/services/user_service" "Launching user service" "user-service"
  
  # Create SQLite volume after app is launched
  create_sqlite_volume "user-service"
  
  # Deploy again to use the volume
  run_in_dir "backend/services/user_service" "flyctl deploy --yes --now" "Deploying user service with SQLite volume" true
  verify_app "user-service" 3 20
fi

# Deploy Order Service with SQLite
step 7 "Deploying Order Service with SQLite"
if check_app_exists "order-service"; then
  echo "🔍 Order service app 'order-service' already exists."
  
  # Create SQLite volume if it doesn't exist
  create_sqlite_volume "order-service"
  
  echo "🔄 Deploying new version..."
  run_in_dir "backend/services/order_service" "flyctl deploy --yes --now" "Deploying order service with SQLite" true
  verify_app "order-service" 3 20
else
  echo "🆕 Creating new order service app..."
  # Prepare service for deployment
  prepare_service_for_deployment "backend/services/order_service"
  
  launch_fly_app "backend/services/order_service" "Launching order service" "order-service"
  
  # Create SQLite volume after app is launched
  create_sqlite_volume "order-service"
  
  # Deploy again to use the volume
  run_in_dir "backend/services/order_service" "flyctl deploy --yes --now" "Deploying order service with SQLite volume" true
  verify_app "order-service" 3 20
fi

# Final check
if [ $GLOBAL_ERROR -eq 0 ]; then
  echo ""
  echo "🎉 Deployment completed successfully!"
  echo "Frontend: https://bajkpaker.fly.dev"
  echo "Product Service: https://product-service.fly.dev"
  echo "User Service: https://user-service.fly.dev"
  echo "Order Service: https://order-service.fly.dev"
else
  echo ""
  echo "⚠️ Deployment completed with some errors. Please check the logs above."
fi 