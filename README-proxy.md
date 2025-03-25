# BajkPaker Proxy Server

This proxy server was created to solve CORS issues when accessing the bikes API at `product-service.fly.dev:8001`.

## Setup Instructions

1. Navigate to the server directory:
   ```
   cd /Users/bartlomiejpalus/Documents/Projects/BajkPaker/server
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the proxy server:
   ```
   npm start
   ```

4. The proxy server will run on `http://localhost:3001` and will forward API requests to `https://product-service.fly.dev:8001`.

## Usage

Instead of making requests to:
```
https://product-service.fly.dev:8001/api/bikes
```

Make requests to your local proxy:
```
http://localhost:3001/api/bikes
```

This will bypass CORS restrictions as the proxy server adds the necessary headers to the responses.

## Alternative Solutions

If you have control over the product-service server, you can add CORS headers directly to that server instead of using this proxy. This would involve configuring the server to include the following headers in its responses:

```
Access-Control-Allow-Origin: *  // Or specify your domain for better security
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```
