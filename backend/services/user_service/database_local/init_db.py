#!/usr/bin/env python3
import os
import sys
import sqlite3
from pathlib import Path

# Add project root to path to import database models
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent
sys.path.append(str(project_root))

# Determine if we're in production or development
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"
DATA_DIR = "/data" if IS_PRODUCTION else "."

# Create data directory if it doesn't exist (for local development)
if not IS_PRODUCTION and not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Database file path
DB_NAME = os.getenv("DB_NAME", "bajkpaker_dev.db")
DB_PATH = os.path.join(DATA_DIR, DB_NAME)

def init_database():
    """Initialize the SQLite database with schema"""
    print(f"Initializing SQLite database at: {DB_PATH}")
    
    # Read the schema file
    schema_path = os.path.join(script_dir, "init-scripts", "01-schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Create and initialize the database
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Execute the schema SQL
        cursor.executescript(schema_sql)
        
        # Commit the changes
        conn.commit()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Check if database already exists
    if os.path.exists(DB_PATH):
        response = input(f"Database already exists at {DB_PATH}. Reinitialize? (y/N): ")
        if response.lower() != 'y':
            print("Exiting without changes.")
            sys.exit(0)
    
    init_database() 