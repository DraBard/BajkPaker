#!/bin/bash

# Remove all components from fly.io
# Author: BajkPaker

# Exit on error
set -e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🧹 Starting removal from project root: $PROJECT_ROOT"

# Function to display step information
step() {
  echo ""
  echo "========================================"
  echo "🔶 STEP $1: $2"
  echo "========================================"
}

# Function to check if a Fly app exists
check_app_exists() {
  local app_name=$1
  flyctl status -a "$app_name" &>/dev/null
  return $?
}

# Function to remove a Fly app
remove_app() {
  local app_name=$1
  local description=$2
  
  echo "🗑️ Removing app: $app_name"
  echo "💻 $description"
  
  if check_app_exists "$app_name"; then
    # Remove all volumes first
    echo "📦 Checking for volumes to remove..."
    flyctl volumes list -a "$app_name" 2>/dev/null | grep -v "No volumes found" | awk 'NR>1 {print $1}' | while read -r volume; do
      if [ -n "$volume" ]; then
        echo "🗑️ Removing volume: $volume from $app_name"
        flyctl volumes delete "$volume" -a "$app_name" -y
      fi
    done
    
    # Now remove the app
    flyctl apps destroy "$app_name" --yes
    echo "✅ App $app_name removed successfully!"
  else
    echo "ℹ️ App $app_name does not exist, nothing to remove."
  fi
}

# Remove each component one by one
# Start with services and finish with the frontend

# Remove Product Service
step 1 "Removing Product Service"
remove_app "product-service" "Removing product microservice"

# Remove User Service
step 2 "Removing User Service"
remove_app "user-service" "Removing user microservice"

# Remove Order Service
step 3 "Removing Order Service"
remove_app "order-service" "Removing order microservice"

# Remove Frontend
step 4 "Removing Frontend"
remove_app "bajkpaker" "Removing frontend application"

echo "✅ All components have been removed from Fly.io!"
echo "🎯 Deployment cleanup complete."
