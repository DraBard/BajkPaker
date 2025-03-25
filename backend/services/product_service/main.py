import sys
from pathlib import Path
import os

# Add the backend directory to the path so imports work correctly
backend_dir = Path(__file__).parent.parent.parent
sys.path.append(str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router as product_router

app = FastAPI(title="Product Service")

# Get allowed origins from env or use default values
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "https://bajkpaker.fly.dev"
).split(",")

print("DEBUG ALLOWED_ORIGINS:", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
