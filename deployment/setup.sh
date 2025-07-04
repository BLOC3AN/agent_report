#!/bin/bash

# ==========================================
# deployment/setup.sh - Quick Setup Script
# ==========================================

set -e

echo "🚀 Auto Report Agent - Quick Setup"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Ask for deployment type
echo ""
echo "Choose deployment type:"
echo "1) Local Development (with local MongoDB container)"
echo "2) Production (with external MongoDB Atlas)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "📦 Setting up Local Development environment..."
        COMPOSE_FILE="docker-compose.yml"
        ENV_TEMPLATE=".env.docker"
        ;;
    2)
        echo "🌐 Setting up Production environment..."
        COMPOSE_FILE="docker-compose.prod.yml"
        ENV_TEMPLATE=".env.prod"
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

# Copy environment template
if [ ! -f "deployment/.env" ]; then
    echo "📝 Creating environment file..."
    cp "deployment/$ENV_TEMPLATE" "deployment/.env"
    echo "✅ Environment file created at deployment/.env"
else
    echo "⚠️ Environment file already exists at deployment/.env"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ $overwrite =~ ^[Yy]$ ]]; then
        cp "deployment/$ENV_TEMPLATE" "deployment/.env"
        echo "✅ Environment file updated"
    fi
fi

echo ""
echo "🔧 Please edit deployment/.env with your actual credentials:"
echo ""

if [ "$choice" = "1" ]; then
    echo "Required for Local Development:"
    echo "  - SLACK_BOT_TOKEN=xoxb-your-bot-token"
    echo "  - SLACK_USER_ID=U1234567890"
    echo "  - GOOGLE_API_KEY=your-google-api-key"
    echo "  - GEMINI_API_KEY=your-gemini-api-key"
    echo ""
    echo "MongoDB will run automatically in a container."
else
    echo "Required for Production:"
    echo "  - MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/agent_reports"
    echo "  - SLACK_BOT_TOKEN=xoxb-your-production-bot-token"
    echo "  - SLACK_USER_ID=U1234567890"
    echo "  - GOOGLE_API_KEY=your-google-api-key"
    echo "  - GEMINI_API_KEY=your-gemini-api-key"
    echo "  - DEFAULT_SHEET_URL=your-google-sheets-url"
fi

echo ""
read -p "Press Enter after you've updated the .env file..."

# Validate required environment variables
echo "🔍 Validating environment variables..."

source deployment/.env

if [ -z "$SLACK_BOT_TOKEN" ] || [ "$SLACK_BOT_TOKEN" = "xoxb-your-slack-bot-token-here" ] || [ "$SLACK_BOT_TOKEN" = "xoxb-your-production-bot-token" ]; then
    echo "❌ SLACK_BOT_TOKEN is not set or still using template value"
    exit 1
fi

if [ -z "$SLACK_USER_ID" ] || [ "$SLACK_USER_ID" = "U1234567890" ]; then
    echo "❌ SLACK_USER_ID is not set or still using template value"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key-here" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key" ]; then
    echo "❌ GOOGLE_API_KEY is not set or still using template value"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key-here" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key" ]; then
    echo "❌ GEMINI_API_KEY is not set or still using template value"
    exit 1
fi

if [ "$choice" = "2" ]; then
    if [ -z "$MONGODB_URI" ] || [[ "$MONGODB_URI" == *"username:password"* ]]; then
        echo "❌ MONGODB_URI is not set or still using template value"
        exit 1
    fi
fi

echo "✅ Environment validation passed"

# Deploy
echo ""
echo "🚀 Deploying services..."
docker-compose -f "deployment/$COMPOSE_FILE" --env-file deployment/.env up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🔍 Checking service health..."
for i in {1..30}; do
    if curl -f http://localhost:5000/health &>/dev/null; then
        echo "✅ Service is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Service health check failed after 30 attempts"
        echo "📋 Check logs with: docker-compose -f deployment/$COMPOSE_FILE logs -f"
        exit 1
    fi
    echo "⏳ Waiting for service... ($i/30)"
    sleep 2
done

# Show status
echo ""
echo "📊 Service Status:"
docker-compose -f "deployment/$COMPOSE_FILE" ps

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📱 Available endpoints:"
echo "  - Health Check: http://localhost:5000/health"
echo "  - Scheduler Status: http://localhost:5000/scheduler/status"
echo "  - Test Slack: http://localhost:5000/test-slack"
echo "  - Manual Report: POST http://localhost:5000/report"
echo ""
echo "📋 Useful commands:"
echo "  - View logs: docker-compose -f deployment/$COMPOSE_FILE logs -f"
echo "  - Stop services: docker-compose -f deployment/$COMPOSE_FILE down"
echo "  - Restart: docker-compose -f deployment/$COMPOSE_FILE restart"
echo ""
echo "🕐 Scheduler will automatically check for reports at:"
echo "  - 10:00 AM"
echo "  - 12:00 PM"
echo "  - 3:00 PM"
echo ""
echo "✨ Your automated report system is now running!"
