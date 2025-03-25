# Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
# Use npm install instead of npm ci to handle package-lock.json mismatches
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist

# Install serve explicitly in the production image and ensure it's in PATH
RUN npm install -g serve && npm cache clean --force

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000
# Ensure npm global bin is in PATH
ENV PATH /usr/local/bin:/usr/bin:/bin:/app/node_modules/.bin

# Expose the port
EXPOSE 3000

# Use absolute path to serve to ensure it's found
CMD ["/usr/local/bin/serve", "-s", "dist", "-l", "3000"]