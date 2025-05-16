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

# Create volumes for persistent storage
flyctl volumes create product_images --size 2 --region waw
flyctl volumes create product_data --size 1 --region waw

# Check application status
flyctl status
```

### After deployment
1. Check if the application is running:
```bash
flyctl status -a product-service
```

2. Check if the files are in the volume:
```bash
fly ssh console -a product-service -C "ls -la /app/static/images"
fly ssh console -a product-service -C "ls -la /data"
```

3. Upload images:
```bash
bash upload_images_flyio.sh
```

4. Run the metadata update script:
```bash
python update_image_metadata.py image_metadata.json
```

### Monitoring and Debugging
```bash
# View logs
flyctl logs

# Access the SQLite database console
fly ssh console -a product-service -C "sqlite3 /data/bajkpaker.db"

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
