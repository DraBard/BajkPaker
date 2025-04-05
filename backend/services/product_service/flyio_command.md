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

### After deployment
Create volume to be able to store images etc.
1. Create the Fly Volume:
flyctl volumes create product_images --size 10 --region waw
2. Check if the files are in the volume:
fly ssh console -a product-service -C "ls -la /app/static/images"
3. Upload images:
bash upload_images_flyio.sh
4. open proxy:
flyctl proxy 3306 -a bajkpaker-mysql
5. Run the metadata update script:
python update_image_metadata.py
