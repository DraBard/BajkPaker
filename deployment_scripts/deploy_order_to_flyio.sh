#!/bin/bash

# Deploy only the Order Service to fly.io
# Author: BajkPaker

set +e

SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT" || exit 1

GLOBAL_ERROR=0
MAX_RETRIES=1

# Use a unique app name to avoid conflicts
APP_NAME="order-processing-service"

step() {
  echo ""; echo "========================================"
  echo "🔶 STEP $1: $2"; echo "========================================"
}

check_flyctl_auth() {
  echo "🔐 Checking flyctl authentication..."
  if ! flyctl auth whoami &>/dev/null; then
    echo "❌ Not logged into flyctl. Please run: flyctl auth login"
    exit 1
  fi
  echo "✅ flyctl authentication verified"
}

check_app_exists() {
  echo "🔍 [DEBUG] check_app_exists called for app='$1' (org: personal)"
  if flyctl status -a "$1" --org personal &>/dev/null; then
    echo "✅ App '$1' exists"
    return 0
  else
    echo "❌ App '$1' does not exist"
    return 1
  fi
}

run_with_retry() {
  local cmd=$1; local desc=$2; local retries=0; local success=false
  echo "🔧 Running: $cmd"; echo "💻 $desc"
  while [ $retries -lt $MAX_RETRIES ] && [ "$success" != "true" ]; do
    [ $retries -gt 0 ] && { echo "🔄 Retry $retries/$MAX_RETRIES"; sleep 3; }
    eval "$cmd" && success=true || retries=$((retries+1))
  done
  [ "$success" = "true" ] || return 1
}

run_in_dir() {
  echo "🔧 [DEBUG] run_in_dir called with dir='$1', cmd='$2', desc='$3', continue_on_error='$4'"
  cd "$PROJECT_ROOT/$1" || { GLOBAL_ERROR=1; return 1; }
  echo "🔧 [DEBUG] Changed directory to '$PROJECT_ROOT/$1'"
  run_with_retry "$2" "$3"; local res=$?
  echo "🔧 [DEBUG] Command exit code: $res"
  if [ $res -ne 0 ]; then
    GLOBAL_ERROR=1
    [ "$4" = "true" ] && echo "⚠️ Continuing despite error." || { cd "$PROJECT_ROOT"; exit 1; }
  fi
  cd "$PROJECT_ROOT"
  return $res
}

create_unique_app() {
  local base_name=$1
  local service_dir=$2
  local attempt=0
  local current_name=$base_name
  
  cd "$PROJECT_ROOT/$service_dir" || { GLOBAL_ERROR=1; return 1; }
  
  while [ $attempt -lt 5 ]; do
    echo "🚀 [DEBUG] Attempting to create app '$current_name' (attempt $((attempt+1)))"
    
    if flyctl apps create "$current_name" --org personal 2>&1; then
      echo "✅ App '$current_name' created successfully"
      echo "$current_name" > .app_name  # Store the actual app name for later use
      cd "$PROJECT_ROOT"
      return 0
    else
      echo "⚠️ App name '$current_name' is taken, trying alternative..."
      attempt=$((attempt+1))
      current_name="${base_name}-${attempt}"
    fi
  done
  
  echo "❌ Failed to create app after 5 attempts"
  GLOBAL_ERROR=1
  cd "$PROJECT_ROOT"
  return 1
}

launch_fly_app() {
  echo "🚀 [DEBUG] launch_fly_app called with service_dir='$1', app_name='$3'"
  local actual_app_name
  
  # Try to create app with unique name
  if create_unique_app "$3" "$1"; then
    # Read the actual app name that was created
    actual_app_name=$(cat "$PROJECT_ROOT/$1/.app_name")
    echo "🚀 [DEBUG] Using app name: '$actual_app_name'"
  else
    return 1
  fi

  cd "$PROJECT_ROOT/$1" || { GLOBAL_ERROR=1; return 1; }

  echo "🚀 [DEBUG] Deploying app '$actual_app_name'"
  if flyctl deploy --app "$actual_app_name" --yes --now; then
    echo "✅ App '$actual_app_name' deployed successfully"
  else
    echo "❌ Failed to deploy app '$actual_app_name'"
    GLOBAL_ERROR=1
    cd "$PROJECT_ROOT"
    return 1
  fi

  cd "$PROJECT_ROOT"
}

get_app_name() {
  local service_dir=$1
  if [ -f "$PROJECT_ROOT/$service_dir/.app_name" ]; then
    cat "$PROJECT_ROOT/$service_dir/.app_name"
  else
    echo "$APP_NAME"
  fi
}

verify_app() {
  echo "🔍 [DEBUG] verify_app called for '$1' (max=$2, wait=$3)"
  local name=$1 max=${2:-3} wait=${3:-10} i=0
  while [ $i -lt $max ]; do
    [ $i -gt 0 ] && { echo "⏳ Waiting $wait sec"; sleep $wait; }
    if curl -s --head --max-time 10 "https://$name.fly.dev" | grep -q "200\|30[1-8]"; then
      echo "✅ $name is up"; return 0
    fi
    i=$((i+1)); echo "🔄 Attempt $i/$max"
  done
  echo "⚠️ $name not accessible after $max attempts"; return 1
}

# Check authentication before starting
check_flyctl_auth

# STEP 1: Deploy Order Service
step 1 "Deploying Order Service"
CURRENT_APP_NAME=$(get_app_name "backend/services/order_processing_service")

if check_app_exists "$CURRENT_APP_NAME"; then
  echo "🔄 Deploying new version to existing app..."
  run_in_dir "backend/services/order_processing_service" \
             "flyctl deploy --app $CURRENT_APP_NAME --yes --now" \
             "Deploying order service" false
  if [ $? -eq 0 ]; then
    verify_app "$CURRENT_APP_NAME" 5 10
  fi
else
  echo "🆕 App doesn't exist, creating and launching order-processing-service..."
  launch_fly_app "backend/services/order_processing_service" "Launching order service" "$APP_NAME"
  if [ $? -eq 0 ]; then
    CURRENT_APP_NAME=$(get_app_name "backend/services/order_processing_service")
    verify_app "$CURRENT_APP_NAME" 5 10
  fi
fi

# STEP 2: Create Volume
step 2 "Creating order_data Volume"
CURRENT_APP_NAME=$(get_app_name "backend/services/order_processing_service")

if check_app_exists "$CURRENT_APP_NAME"; then
  if ! flyctl volumes list -a "$CURRENT_APP_NAME" 2>/dev/null | grep -q "order_data"; then
    run_in_dir "backend/services/order_processing_service" \
               "flyctl volumes create order_data --size 1 --region waw --yes --app $CURRENT_APP_NAME" \
               "Creating order_data volume" true
  else
    echo "✅ order_data volume exists."
  fi
else
  echo "❌ Cannot create volume: $CURRENT_APP_NAME app does not exist"
  GLOBAL_ERROR=1
fi

# STEP 3: Initialize SQLite DB
step 3 "Initializing SQLite Database"
CURRENT_APP_NAME=$(get_app_name "backend/services/order_processing_service")

if check_app_exists "$CURRENT_APP_NAME"; then
  run_in_dir "backend/services/order_processing_service" \
             "flyctl ssh console -a $CURRENT_APP_NAME -C 'python /app/init_sqlite_db.py --db-path /data/order_processing_service.db'" \
             "Initializing order-processing-service SQLite DB" true
else
  echo "❌ Cannot initialize database: $CURRENT_APP_NAME app does not exist"
  GLOBAL_ERROR=1
fi

echo ""
FINAL_APP_NAME=$(get_app_name "backend/services/order_processing_service")
if [ $GLOBAL_ERROR -eq 0 ]; then
  echo "✅ order-processing-service deployment completed!"
  echo "🔄 https://$FINAL_APP_NAME.fly.dev"
else
  echo "⚠️ Deployment finished with errors."
  echo "🔄 https://$FINAL_APP_NAME.fly.dev"
fi
echo ""
