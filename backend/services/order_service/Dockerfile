FROM python:3.10-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    sqlite3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared database directory and models
# COPY ../../../database /app/database
COPY ./database_local /app/database

# Copy application code
COPY . .

# Create directory for SQLite database
RUN mkdir -p /data && chmod 777 /data

# Expose port
EXPOSE 8002

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
