#!/bin/bash

# Deploy updated product service to fix CORS issues
# Exit on error
set -e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🚀 Starting product service deployment from project root: $PROJECT_ROOT"

# Function to display step information
step() {
  echo ""
  echo "========================================"
  echo "🔶 STEP $1: $2"
  echo "========================================"
}

# Navigate to product service directory
cd "$PROJECT_ROOT/backend/services/product_service"

# Deploy the product service
step 1 "Deploying Product Service with CORS fixes"
echo "📤 Deploying product-service to Fly.io"
flyctl deploy --remote-only

echo "✅ Product service has been deployed with CORS fixes!"
echo "🎯 Deployment complete." 