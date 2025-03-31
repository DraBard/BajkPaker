#!/bin/bash
# Script to diagnose HTTP protocol issues with Fly.io applications

set -e  # Exit on error

echo "Starting HTTP protocol diagnostic tests..."

# Check service status
echo "1. Checking service status..."
fly status -a product-service

# Check recent logs specifically for HTTP errors
echo -e "\n2. Checking recent logs for HTTP errors..."
fly logs -a product-service --instance 0 | grep -E "HTTP|http|proxy|error|invalid" | tail -n 20

# Test accessing a known endpoint with explicit HTTP version specification
echo -e "\n3. Testing HTTP/1.1 request to healthz endpoint..."
fly ssh console -a product-service -C "curl -v --http1.1 http://localhost:8001/healthz"

# Check if service listens on the correct port
echo -e "\n4. Checking if service listens on port 8001..."
fly ssh console -a product-service -C "netstat -tulpn | grep 8001"

# Check HTTP headers from outside using curl
echo -e "\n5. Testing external HTTP request with explicit version..."
curl -v --http1.1 https://product-service.fly.dev/healthz

echo -e "\n6. Testing new debug headers endpoint..."
curl -v --http1.1 https://product-service.fly.dev/debug/headers

echo -e "\nDiagnostic tests completed. Check the output above for clues about HTTP protocol issues."
echo "Look for any 'invalid HTTP version' messages or unexpected protocol behavior."
