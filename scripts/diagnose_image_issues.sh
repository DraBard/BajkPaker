#!/bin/bash
# filepath: /Users/bartlomiejpalus/Documents/Projects/BajkPaker/scripts/diagnose_image_issues_v2.sh

set -e

echo "Starting improved image serving diagnostic..."

# Check if the volume is properly mounted on the server
echo "1. Checking volume mount..."
fly ssh console -a product-service -C "ls -la /app/static/images"

# Count the number of image files
echo "2. Counting image files in the volume..."
fly ssh console -a product-service -C "find /app/static/images -type f | wc -l"

# List a few sample images if they exist
echo "3. Listing sample images (if any)..."
fly ssh console -a product-service -C "find /app/static/images -type f -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' | head -5"

# Check the permissions again
echo "4. Checking directory permissions..."
fly ssh console -a product-service -C "ls -la /app/static"

# Create a temporary Python script to check the database and image paths
echo "5. Creating and running database verification script..."
fly ssh console -a product-service -C "cat > /tmp/verify_db.py << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text
import mimetypes

# Register MIME types
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')
mimetypes.add_type('image/png', '.png')

# Get database connection details from environment
db_user = os.environ.get('DB_USER', 'bajkpaker')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST', 'bajkpaker-mysql.internal')
db_port = os.environ.get('DB_PORT', '3306')
db_name = os.environ.get('DB_NAME', 'bajkpaker_dev')

# Build connection string
db_url = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

try:
    # Connect to database
    engine = create_engine(db_url)
    conn = engine.connect()
    
    # Query bike_images table
    result = conn.execute(text('SELECT id, bike_id, image_url, is_main FROM bike_images'))
    images = [dict(row) for row in result]
    
    print(f'Found {len(images)} images in database')
    
    # Check if paths exist
    for img in images:
        path = img['image_url']
        if path.startswith('/'):
            full_path = f'/app{path}'
        else:
            full_path = f'/app/{path}'
            
        exists = os.path.exists(full_path)
        ext = os.path.splitext(path)[1].lower()
        mime_type = mimetypes.types_map.get(ext, 'unknown')
        
        print(f'ID: {img[\"id\"]}, Bike ID: {img[\"bike_id\"]}, Path: {path}')
        print(f'  File exists: {exists}, MIME type: {mime_type}, Is main: {img[\"is_main\"]}')
        
        if not exists:
            print(f'  WARNING: File not found at {full_path}')
    
    # Check for FastAPI static files configuration
    import importlib.util
    spec = importlib.util.spec_from_file_location('main', '/app/main.py')
    if spec:
        main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main)
        print('\\nFastAPI app configuration:')
        if hasattr(main, 'app'):
            has_static_files = False
            for route in main.app.routes:
                if str(route).find('StaticFiles') >= 0:
                    has_static_files = True
                    print(f'  Found StaticFiles route: {route}')
            if not has_static_files:
                print('  No StaticFiles routes found!')
    
except Exception as e:
    print(f'Error: {e}')
EOF

# Run the verification script
python3 /tmp/verify_db.py
"

# Test accessing a specific image
echo "6. Testing image access..."
fly ssh console -a product-service -C "curl -s -I http://localhost:8001/debug/mime-types"

# Check main application logs for image related errors
echo "7. Checking service logs for image-related errors..."
fly logs -a product-service --instance 0 | grep -i -E "static|image|file|mime" | tail -10

echo "Diagnostic complete!"
echo "Based on the results, you may need to re-upload your images or update database paths."