# SQLite Database Setup Instructions

## Local Development

### Initialize SQLite Database
```bash
# Create SQLite database for development
python init_sqlite_db.py --db-path ./data/bajkpaker.db
```

### Docker-based Development (Optional)
For those who still want to use Docker for development:

```bash
# Build a lightweight Python Alpine container with SQLite
docker build -t bajkpaker-sqlite -f Dockerfile.sqlite .

# Run the container with mounted volume for database persistence
docker run -d \
  -p 8000:8000 \
  -v "$(pwd)/data:/data" \
  bajkpaker-sqlite
```

## Fly.io Deployment

### Creating Volumes for SQLite
```bash
# Create volumes for each service's database
flyctl volumes create product_data --size 1 --region waw
flyctl volumes create user_data --size 1 --region waw
flyctl volumes create order_data --size 1 --region waw
```

### Deploying Services
```bash
# Deploy each service
flyctl deploy --config path/to/frontend/fly.toml
flyctl deploy --config path/to/product-service/fly.toml
flyctl deploy --config path/to/user-service/fly.toml
```

### Uploading Images and Initializing Database
```bash
# Upload product images
cd path/to/product_service
bash upload_images_flyio.sh

# Initialize database directly on the fly.io instance
flyctl ssh console -a product-service -C "python /app/init_sqlite_db.py --db-path /data/bajkpaker.db"

# Update the database with metadata
python update_image_metadata.py image_metadata.json
```

### SQLite Management

#### Accessing the SQLite Database
```bash
# Connect to the SQLite database on fly.io
flyctl ssh console -a product-service -C "sqlite3 /data/bajkpaker.db"
```

#### Common SQLite Commands
```
.tables           # List all tables
.schema [table]   # Show schema for a table
.mode column      # Format output as columns
.headers on       # Show column headers
SELECT * FROM bikes LIMIT 5;  # Example query
.quit             # Exit SQLite shell
```

#### Backing Up the Database
```bash
# Create a backup of the SQLite database
flyctl ssh console -a product-service -C "sqlite3 /data/bajkpaker.db '.backup /tmp/bajkpaker_backup.db'"
flyctl ssh sftp get -a product-service /tmp/bajkpaker_backup.db ./local_backup.db
```