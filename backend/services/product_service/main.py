import sys
from pathlib import Path
import os
import logging
import uvicorn

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
from routers import router as product_router

app = FastAPI(title="Product Service")

# Get allowed origins from env or use default values
allowed_origins = os.getenv("ALLOWED_ORIGINS", "https://bajkpaker.fly.dev").split(",")

logger.info(f"Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add middleware to log request/response info for debugging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request headers: {request.headers}")

    response = await call_next(request)

    logger.info(f"Response status code: {response.status_code}")
    return response


# Mount the static directory to serve images
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(product_router)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for the proxy to verify service is running properly"""
    return {"status": "healthy"}


@app.get("/debug/headers")
async def debug_headers(request: Request):
    """Debug endpoint to see what headers are being received"""
    return {"headers": dict(request.headers)}


if __name__ == "__main__":
    logger.info("Starting product service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        proxy_headers=True,  # Important for handling proxy headers correctly
        forwarded_allow_ips="*",  # Allow all forwarded IPs in production
    )
