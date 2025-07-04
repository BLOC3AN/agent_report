#!/bin/bash

# ==========================================
# deploy.sh - Simple Deploy Script
# ==========================================

echo "🚀 Deploying Auto Report Agent..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file with your credentials"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose -f deployment/docker-compose.yml down 2>/dev/null || true

# Build and start
echo "🔨 Building and starting services..."
docker compose -f deployment/docker-compose.yml up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🔍 Checking service health..."
for i in {1..10}; do
    if curl -f http://localhost:5000/health &>/dev/null; then
        echo "✅ Service is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Service health check failed"
        echo "📋 Check logs with: docker-compose logs -f"
        exit 1
    fi
    echo "⏳ Waiting... ($i/10)"
    sleep 3
done

echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📱 Available endpoints:"
echo "  - Health: http://localhost:5000/health"
echo "  - Scheduler: http://localhost:5000/scheduler/status"
echo "  - Test Slack: http://localhost:5000/test-slack"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker compose -f deployment/docker-compose.yml logs -f"
echo "  - Stop: docker compose -f deployment/docker-compose.yml down"
echo "  - Restart: docker compose -f deployment/docker-compose.yml restart"
echo ""
echo "✨ Your automated report system is running!"
