FROM python:3.10-slim

ARG ALLOWED_ORIGINS
ARG DB_ECHO
ARG DB_HOST
ARG DB_NAME
ARG DB_PORT
ARG DB_USER
ARG DB_PASSWORD
ARG ENVIRONMENT

ENV ALLOWED_ORIGINS=$ALLOWED_ORIGINS
ENV DB_ECHO=$DB_ECHO
ENV DB_HOST=$DB_HOST
ENV DB_NAME=$DB_NAME
ENV DB_PORT=$DB_PORT
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV ENVIRONMENT=$ENVIRONMENT

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the service code
COPY . /app

# Expose the service port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]