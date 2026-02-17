#!/bin/bash

echo "Starting Debug Process..."

# 1. Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# 2. Check token.json
if [ -d "token.json" ]; then
    echo "Warning: token.json is a directory! Removing it..."
    rm -rf token.json
fi

# 3. Rebuild without cache
echo "Rebuilding containers (no-cache)..."
docker-compose build --no-cache

# 4. Start containers
echo "Starting containers..."
docker-compose up -d

# 5. Show logs for Backend (wait for startup)
echo "Tailing backend logs (Press Ctrl+C to exit logs)..."
docker-compose logs -f backend
