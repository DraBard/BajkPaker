# BajkPaker Deployment Guide

This guide explains how to deploy the BajkPaker application on fly.io.

## Prerequisites

1. Install [flyctl](https://fly.io/docs/hands-on/install-flyctl/)
2. Log in to fly.io: `fly auth login`

## Database Deployment

1. Deploy the MySQL database:
   ```bash
   cd backend/database
   fly launch --name bajkpaker-mysql --region waw
   ```

2. Set up database secrets:
   ```bash
   cd backend/scripts
   chmod +x setup_fly_db.sh
   ./setup_fly_db.sh
   ```

## Backend Services Deployment

### Product Service

1. Deploy the Product Service:
   ```bash
   cd backend/services/product_service
   fly launch --name product-service --region waw
   ```

### Order Service

1. Deploy the Order Service:
   ```bash
   cd backend/services/order_service
   fly launch --name order-service --region waw
   ```

### User Service

1. Deploy the User Service:
   ```bash
   cd backend/services/user_service
   fly launch --name user-service --region waw
   ```

## Frontend Deployment

1. Deploy the Frontend:
   ```bash
   cd frontend
   fly launch --name bajkpaker --region waw
   ```

## Verify Deployment

1. Check if all applications are running:
   ```bash
   fly apps list
   ```

2. Visit the frontend application:
   ```
   https://bajkpaker.fly.dev
   ```

## Troubleshooting

### Database Connection Issues

If services can't connect to the database:

1. Check database logs:
   ```bash
   fly logs -a bajkpaker-mysql
   ```

2. Verify service logs:
   ```bash
   fly logs -a product-service
   ```

3. Ensure the database password is correctly set in secrets.

### CORS Issues

If you're experiencing CORS errors:

1. Check that the `ALLOWED_ORIGINS` environment variable includes the frontend domain.
2. Verify that the requests include credentials with `withCredentials: true`.

### Application Not Responding

1. Check the VM status:
   ```bash
   fly status -a bajkpaker
   ```

2. Check application logs:
   ```bash
   fly logs -a bajkpaker
   ```
