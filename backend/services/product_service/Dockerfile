FROM python:3.10-slim

# Install build tools and dependencies
RUN apt-get update && apt-get install -y gcc libmariadb-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements file and install dependencies
COPY services/product_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY services/product_service /app

# Copy the shared database code and config file
COPY shared_database /app/shared_database

# Expose the service port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]