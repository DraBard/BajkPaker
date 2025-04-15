#!/bin/bash

# Remove all components from fly.io
# Author: BajkPaker

# Don't exit immediately on error
set +e

# Store the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "🚀 Starting removal from project root: $PROJECT_ROOT"

# Change to project root to ensure relative paths work as expected
cd "$PROJECT_ROOT" || exit 1

# Function to display step information
step() {
  echo ""
  echo "========================================"
  echo "🔶 STEP $1: $2"
  echo "========================================"
}

# Function to check if a Fly.io app exists
app_exists() {
  local app_name=$1
  flyctl apps list | grep -q "$app_name"
  return $?
}

# Function to run a command in a specific directory
run_in_dir() {
  local dir=$1
  local command=$2
  local description=$3
  
  echo "📂 Changing to directory: $dir"
  cd "$dir" || {
    echo "❌ Failed to change to directory: $dir"
    return 1
  }
  echo "🔧 Running: $command"
  echo "💻 $description"
  eval "$command"
  local result=$?
  cd "$PROJECT_ROOT"
  return $result
}

# Function to remove a Fly.io app with error handling
remove_app() {
  local dir=$1
  local app_name=$2
  local description=$3
  
  echo "📂 Changing to directory: $dir"
  cd "$dir" || {
    echo "❌ Failed to change to directory: $dir"
    return 1
  }
  
  echo "🔍 Checking if app '$app_name' exists..."
  if app_exists "$app_name"; then
    echo "✅ App '$app_name' found, proceeding with removal"
    echo "🔧 Running: flyctl apps destroy $app_name --yes"
    echo "💻 $description"
    flyctl apps destroy "$app_name" --yes
    local result=$?
    if [ $result -eq 0 ]; then
      echo "✅ Successfully removed $app_name"
    else
      echo "❌ Failed to remove $app_name (error code: $result)"
    fi
  else
    echo "ℹ️ App '$app_name' not found on Fly.io, skipping removal"
  fi
  
  cd "$PROJECT_ROOT"
}

# Remove Product Service
step 1 "Removing Product Service"
remove_app "backend/services/product_service" "product-service" "Removing product service from Fly.io"

# Remove Database
step 2 "Removing Database"
remove_app "backend/database" "bajkpaker-mysql" "Removing MySQL database from Fly.io"

# Remove Frontend
step 3 "Removing Frontend"
remove_app "frontend" "bajkpaker" "Removing frontend application from Fly.io"

echo ""
echo "✅ Removal process completed!"
