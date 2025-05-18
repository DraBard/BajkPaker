FROM python:3.10-slim

ARG ENVIRONMENT
ARG DB_NAME
ARG DB_ECHO
ARG ALLOWED_ORIGINS

ENV ENVIRONMENT=$ENVIRONMENT
ENV DB_NAME=$DB_NAME
ENV DB_ECHO=$DB_ECHO
ENV ALLOWED_ORIGINS=$ALLOWED_ORIGINS

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared database directory and models
# COPY ../../../database /app/database
COPY ./database_local /app/database

# Copy the service code
COPY . /app

# Create directories for SQLite database and images
RUN mkdir -p /data && chmod 777 /data
RUN mkdir -p /app/images && chmod 777 /app/images

# Expose the service port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]