#!/bin/bash

# Student Platform API Docker Startup Script

echo "🐳 Starting Student Platform API with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose up --build

echo "🌟 Application is running!"
echo "   API: http://localhost:5005"
echo "   With Nginx: http://localhost:80"
echo "   Health check: http://localhost:5005/api/health/"
