import sys
from pathlib import Path
import os
import logging
import uvicorn
import mimetypes
import gc

# Force garbage collection to run more aggressively
gc.set_threshold(100, 5, 5)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("product_service")

# Add the backend directory to the path so imports work correctly
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from routers import router as product_router

# Ensure proper MIME types are registered for images
mimetypes.add_type("image/jpeg", ".jpg")
mimetypes.add_type("image/jpeg", ".jpeg")
mimetypes.add_type("image/png", ".png")

app = FastAPI(
    title="Product Service", docs_url=None, redoc_url=None
)  # Disable docs in production

# Get allowed origins from env or use default values
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://bajkpaker.fly.dev,http://localhost:3000").split(",")

logger.info(f"Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins to fix the issue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)


# Add CORS headers to all responses
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request headers: {request.headers}")
    
    # Handle OPTIONS preflight requests manually
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response
    
    response = await call_next(request)
    
    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    logger.info(f"Response status code: {response.status_code}")
    logger.info(f"Response headers: {response.headers}")

    # Force garbage collection after each request
    gc.collect()

    return response


# Add debugging endpoint for image testing
@app.get("/debug/test-image")
async def test_image():
    """Test endpoint to verify image serving without browser interference"""
    return {"sample_image_url": "/static/images/PortoMain.jpg"}


# Mount the images directory as a static files endpoint
app.mount("/static/images", StaticFiles(directory="images", html=False), name="images")

app.include_router(product_router)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for the proxy to verify service is running properly"""
    return {"status": "healthy"}


@app.get("/debug/headers")
async def debug_headers(request: Request):
    """Debug endpoint to see what headers are being received"""
    return {"headers": dict(request.headers)}


@app.get("/debug/mime-types")
async def debug_mime_types():
    """Debug endpoint to see registered MIME types for common image extensions"""
    return {
        "jpg": mimetypes.types_map.get(".jpg", "not registered"),
        "jpeg": mimetypes.types_map.get(".jpeg", "not registered"),
        "png": mimetypes.types_map.get(".png", "not registered"),
    }


if __name__ == "__main__":
    logger.info("Starting product service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        proxy_headers=True,  # Important for handling proxy headers correctly
        forwarded_allow_ips="*",  # Allow all forwarded IPs in production
        workers=1,  # Use minimum workers to save memory
        limit_max_requests=1000,  # Restart workers after handling 1000 requests to prevent memory leaks
    )
