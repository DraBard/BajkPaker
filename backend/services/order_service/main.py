from fastapi import FastAPI, Request, Response
import logging
from routers import router, configure_cors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Service")

# Configure CORS
configure_cors(app)

# Include routers
app.include_router(router)

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

# Explicitly handle OPTIONS requests at the root level
@app.options("/{rest_of_path:path}")
async def options_handler(request: Request):
    return Response(status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)