#!/bin/bash

# ==========================================
# run.sh - Start Agent Report Service
# ==========================================

echo "🚀 Starting Agent Report Service..."

# Load .env file if it exists
if [ -f .env ]; then
    echo "📄 Loading .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  No .env file found"
fi

# Check if MongoDB is running (optional - service can work without local MongoDB)
if command -v mongod &> /dev/null; then
    echo "📦 Starting MongoDB..."
    sudo rm -f /tmp/mongodb-27017.sock 2>/dev/null
    sudo systemctl start mongod &
    sleep 2
else
    echo "⚠️  MongoDB not found locally - using configured MONGODB_URI"
fi

# Check if required environment variables are set
if [ -z "$MONGODB_URI" ]; then
    echo "⚠️  MONGODB_URI not set, using default: mongodb://localhost:27017"
    export MONGODB_URI="mongodb://localhost:27017"
fi

# Set default values for other environment variables if not set
export DEBUG=${DEBUG:-true}
export LOG_LEVEL=${LOG_LEVEL:-DEBUG}
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-5000}

echo "📊 Configuration:"
echo "  - Debug: $DEBUG"
echo "  - Log Level: $LOG_LEVEL"
echo "  - API Host: $API_HOST"
echo "  - API Port: $API_PORT"
echo "  - MongoDB URI: $MONGODB_URI"
echo "  - MongoDB DB: $MONGODB_DB_NAME"
echo "  - MongoDB Collection: $MONGODB_COLLECTION_NAME"

# Debug: Show all environment variables starting with MONGODB
echo "🔍 MongoDB Environment Variables:"
env | grep MONGODB

# Start the main application
echo "🤖 Starting Agent Report Service..."
python3 main.py
