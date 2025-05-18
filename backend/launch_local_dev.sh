#!/bin/bash

# Script to initialize the SQLite database and launch development servers
# Author: BajkPaker

set -e  # Exit on error

# Find the project root directory
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR" && pwd)
echo "🚀 Starting local development from: $PROJECT_ROOT"

# Function to display step information
step() {
  echo ""
  echo "========================================"
  echo "🔶 STEP $1: $2"
  echo "========================================"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check Python is installed
if ! command_exists python3; then
    echo "❌ Python 3 is required but not found."
    exit 1
fi

# Initialize SQLite database
step 1 "Initializing SQLite Database"
cd "$PROJECT_ROOT"
python3 database/init_db.py
echo "✅ Database initialization completed"

# Launch services in separate terminals
step 2 "Launching Services"

# Function to launch a service in a new terminal
launch_service() {
    local service_dir=$1
    local service_name=$2
    local port=$3
    
    cd "$PROJECT_ROOT/services/$service_dir"
    
    echo "🚀 Launching $service_name on port $port..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell app \"Terminal\" to do script \"cd $PROJECT_ROOT/services/$service_dir && export ENVIRONMENT=development && python3 -m uvicorn main:app --reload --port $port\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try different terminal emulators
        if command_exists gnome-terminal; then
            gnome-terminal -- bash -c "cd $PROJECT_ROOT/services/$service_dir && export ENVIRONMENT=development && python3 -m uvicorn main:app --reload --port $port; exec bash"
        elif command_exists xterm; then
            xterm -e "cd $PROJECT_ROOT/services/$service_dir && export ENVIRONMENT=development && python3 -m uvicorn main:app --reload --port $port; exec bash" &
        else
            echo "⚠️ Unable to launch terminal. Please manually run the following command in a new terminal:"
            echo "cd $PROJECT_ROOT/services/$service_dir && export ENVIRONMENT=development && python3 -m uvicorn main:app --reload --port $port"
        fi
    else
        # Windows or other
        echo "⚠️ Automatic terminal launch not supported on this OS. Please manually run the following command in a new terminal:"
        echo "cd $PROJECT_ROOT/services/$service_dir && export ENVIRONMENT=development && python3 -m uvicorn main:app --reload --port $port"
    fi
}

# Launch product service only
launch_service "product_service" "Product Service" 8001
echo "✅ Product Service launching"

# Launch user and order services (commented out)
# sleep 2  # Brief pause between launching terminals
# 
# launch_service "user_service" "User Service" 8003
# echo "✅ User Service launching"
# 
# sleep 2  # Brief pause between launching terminals
# 
# launch_service "order_service" "Order Service" 8002
# echo "✅ Order Service launching"

echo ""
echo "🎉 Services are starting!"
echo "📝 Service endpoints:"
echo "  - Product Service: http://localhost:8001"
# echo "  - Order Service:   http://localhost:8002"
# echo "  - User Service:    http://localhost:8003"
echo ""
echo "⚠️ Note: Only Product Service is being launched as requested."
echo "💡 To view the database, you can use a SQLite browser like 'DB Browser for SQLite'." 