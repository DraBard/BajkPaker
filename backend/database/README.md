# BajkPaker SQLite Database

This directory contains the SQLite database configuration for the BajkPaker application.

## Overview

The application uses SQLite as a lightweight, serverless database solution, which is ideal for deployment on Fly.io. SQLite is a file-based database that requires minimal resources and configuration.

## Database Structure

The database schema is defined in:
- `init-scripts/01-schema.sql`: Contains the SQLite schema for all tables
- `models.py`: Contains the SQLAlchemy models used by the application

## Database Initialization

For local development:
1. Run `python init_db.py` from the `backend` directory to create and initialize the SQLite database
2. The database file will be created in the current directory as `bajkpaker_dev.db`

For production:
1. The database is automatically initialized during deployment
2. The database file is stored in a persistent volume at `/data/bajkpaker_dev.db`

## Database Files

- `init_db.py`: Script to initialize the SQLite database
- `models.py`: SQLAlchemy ORM models
- `init-scripts/01-schema.sql`: SQL schema for creating tables

## Using the Database

### Local Development

For local development, all microservices connect to the same SQLite database file, which is created in the backend directory. This simplifies the development process as you don't need to run multiple database instances.

To launch all services with the correct database configuration:
```bash
./launch_local_dev.sh
```

### Production (Fly.io)

In production, each service has its own SQLite database stored in a separate persistent volume. The deployment scripts automatically:

1. Create persistent volumes for each service
2. Mount the volumes at `/data`
3. Initialize the database schema
4. Configure the services to connect to their SQLite databases

## Migrating Data

To migrate data between environments or services, you can use SQLite's backup and restore functions:

```bash
# Export
sqlite3 bajkpaker_dev.db .dump > backup.sql

# Import
sqlite3 new_database.db < backup.sql
```

## Debugging

To inspect the SQLite database:
1. Install a SQLite browser like "DB Browser for SQLite"
2. Open the database file `bajkpaker_dev.db`

## Performance Considerations

SQLite performs well for most use cases in this application. For high-concurrency scenarios, consider:

1. Implementing appropriate indexes
2. Using proper transaction isolation levels
3. Optimizing queries for SQLite's specific characteristics 