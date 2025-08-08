#!/bin/bash

echo "🚀 Starting eFab AI Enhanced..."
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your settings."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🎯 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ eFab AI Enhanced is running!"
echo "================================"
echo "📊 Access points:"
echo "  • API:        http://localhost:8000"
echo "  • API Docs:   http://localhost:8000/docs"
echo "  • UI:         http://localhost:8501"
echo "  • Flower:     http://localhost:5555"
echo ""
echo "📝 Logs: docker-compose logs -f"
echo "🛑 Stop: docker-compose down"
echo "================================"