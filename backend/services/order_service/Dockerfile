# backend/service1/Dockerfile

# Use the pre-built base image
FROM python:3.10-slim
RUN apt-get update && apt-get install -y gcc libmariadb-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set the service-specific port
ENV PORT=8002

COPY . .
# Inform Docker of the port this service listens on
EXPOSE 8002

CMD ["python", "main.py"]
