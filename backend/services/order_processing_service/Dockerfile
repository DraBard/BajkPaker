FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for production database
RUN mkdir -p /data

# Set environment to production
ENV ENVIRONMENT=production

# Initialize database and run application
CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8002"]
