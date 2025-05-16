flyctl secrets set DB_USER=bajkpaker DB_HOST=bajkpaker-mysql.internal \
  DB_PORT=3306 DB_NAME=bajkpaker_dev -a product-service

# Set the password separately as it's sensitive
flyctl secrets set DB_PASSWORD=your_password -a product-service

fly apps destroy bajkpaker --yes

flyctl logs


locally for docker:

docker build \
  --build-arg ALLOWED_ORIGINS='https://bajkpaker.fly.dev,https://bajkpaker-mysql.fly.dev,http://localhost:3000' \
  --build-arg DB_ECHO='False' \
  --build-arg DB_HOST='bajkpaker-mysql.fly.dev' \
  --build-arg DB_NAME='bajkpaker_dev' \
  --build-arg DB_PORT='3306' \
  --build-arg DB_USER='bajkpaker' \
  --build-arg ENVIRONMENT='production' \
  -t product-service .


docker run -d \
  -p 8001:8001 \
  product-service

# Fly.io Deployment Commands for SQLite Based BajkPaker

### Initial Deployment
```bash
# Deploy the application
flyctl deploy

# Create a single volume for both DB and images
flyctl volumes create product_data --size 2 --region waw

# Check application status
flyctl status
```

### After deployment
1. Check if the application is running:
```bash
flyctl status -a product-service
flyctl status -a user-service
flyctl status -a order-service
```

2. Check if the files are in the volume:
```bash
fly ssh console -a product-service -C "ls -la /data/static/images"
fly ssh console -a product-service -C "ls -la /data"
fly ssh console -a user-service -C "ls -la /data"
fly ssh console -a order-service -C "ls -la /data"
```

3. Upload images:
```bash
bash upload_images_flyio.sh
```

4. Run the metadata update script:
```bash
python update_image_metadata.py image_metadata.json
```

5. Initialize SQLite databases:
```bash
flyctl ssh console -a product-service -C "python /app/init_sqlite_db.py --db-path /data/product_service.db"
flyctl ssh console -a user-service -C "python /app/init_sqlite_db.py --db-path /data/user_service.db"
flyctl ssh console -a order-service -C "python /app/init_sqlite_db.py --db-path /data/order_service.db"
```

### Monitoring and Debugging
```bash
# View logs
flyctl logs

# Access the SQLite database console
fly ssh console -a product-service -C "sqlite3 /data/product_service.db"
fly ssh console -a user-service -C "sqlite3 /data/user_service.db"
fly ssh console -a order-service -C "sqlite3 /data/order_service.db"

# Common SQLite commands in the console:
# .tables             - Show all tables
# .schema tablename   - Show table structure
# .quit               - Exit SQLite console
```

### Running locally with Docker
```bash
docker build -t product-service .

docker run -d \
  -p 8001:8001 \
  -v "$(pwd)/data:/data" \
  -v "$(pwd)/static/images:/app/static/images" \
  product-service
```
