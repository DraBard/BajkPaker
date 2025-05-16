#!/usr/bin/env python3
"""
SQLite database initialization script for BajkPaker
Creates the necessary tables based on the models
"""

import os
import sys
import sqlite3
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import models
sys.path.append(str(Path(__file__).parent.parent))
from database.models import Base


def init_sqlite_db(db_path):
    """Initialize SQLite database with schema from models"""
    print(f"Initializing SQLite database at: {db_path}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create tables using SQLAlchemy metadata
    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    print(f"✅ Database initialized successfully at {db_path}")

    # Verify tables were created
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables created:")
    for table in tables:
        print(f"  - {table[0]}")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize SQLite database")
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to SQLite database file",
    )
    args = parser.parse_args()

    # Always resolve the db_path relative to this script's directory if not absolute
    if args.db_path is None:
        # Default to ../services/product_service/product_service.db relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(
            os.path.join(
                script_dir, "..", "services", "product_service", "product_service.db"
            )
        )
    elif not os.path.isabs(args.db_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(script_dir, args.db_path))
    else:
        db_path = args.db_path

    init_sqlite_db(db_path)
