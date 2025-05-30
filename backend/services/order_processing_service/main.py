from fastapi import FastAPI, Request, Response
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
from routers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service")

# Configure CORS in main
mode = os.getenv("MODE", "production").lower()
if mode == "development":
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
    ]
else:
    origins = [
        "https://bajkpaker.fly.dev",
        "https://product-service.fly.dev",
    ]

# Configure CORS with more detailed settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=86400,
)
logger.info(f"CORS configured with origins: {origins}")

# Include routers
app.include_router(router)


@app.head("/", include_in_schema=False)
async def head_root():
    return Response(status_code=200)


# Initialize database on startup in production
@app.on_event("startup")
async def startup_event():
    if os.getenv("ENVIRONMENT") == "production":
        try:
            from init_db import init_db

            await init_db()
            logger.info("Database initialized successfully on startup")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")


# Add a debugging middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Request headers: {request.headers}")

    response = await call_next(request)

    logger.info(f"Response status: {response.status_code}")
    return response


@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}


# Add an explicit handler for /api preflight OPTIONS requests
@app.options("/api")
async def options_api_root():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        },
    )


# Explicitly handle OPTIONS requests at the root level
@app.options("/{rest_of_path:path}")
async def options_handler(request: Request, rest_of_path: str):
    logger.info(f"Processing OPTIONS request for: /{rest_of_path}")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
