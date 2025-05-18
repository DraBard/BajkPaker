#!/bin/bash

# Fix the database path issue for Fly.io deployment
# Author: BajkPaker

set -e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🔧 Starting deployment fix from project root: $PROJECT_ROOT"

# Change to project root to ensure relative paths work as expected
cd "$PROJECT_ROOT" || exit 1

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

# Prepare all services
echo "🔄 Preparing all services for deployment..."

# Product Service
prepare_service_for_deployment "backend/services/product_service"

# User Service
prepare_service_for_deployment "backend/services/user_service"

# Order Service
prepare_service_for_deployment "backend/services/order_service"

echo "✅ All services prepared for deployment!"
echo "🚀 You can now run the deployment script: bash deployment_scripts/deploy_to_flyio.sh" 