#!/bin/bash

# ==========================================
# deployment/start.sh - Container Start Script
# ==========================================

echo "🚀 Starting Agent Report Service in container..."

# Set default environment variables if not provided
export DEBUG=${DEBUG:-false}
export LOG_LEVEL=${LOG_LEVEL:-INFO}
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-5000}

# Scheduler defaults
export SCHEDULER_ENABLED=${SCHEDULER_ENABLED:-true}
export SCHEDULER_TIMEZONE=${SCHEDULER_TIMEZONE:-Asia/Ho_Chi_Minh}
export SCHEDULER_CHECK_TIMES=${SCHEDULER_CHECK_TIMES:-10:00,12:00,15:00}
export SCHEDULER_MAX_REMINDERS=${SCHEDULER_MAX_REMINDERS:-3}

# Validate required environment variables
if [ -z "$MONGODB_URI" ]; then
    echo "❌ Error: MONGODB_URI environment variable is required"
    exit 1
fi

echo "📊 Container Configuration:"
echo "  - Debug: $DEBUG"
echo "  - Log Level: $LOG_LEVEL"
echo "  - API Host: $API_HOST"
echo "  - API Port: $API_PORT"
echo "  - MongoDB URI: $MONGODB_URI"
echo "  - Scheduler Enabled: $SCHEDULER_ENABLED"
echo "  - Scheduler Timezone: $SCHEDULER_TIMEZONE"
echo "  - Check Times: $SCHEDULER_CHECK_TIMES"
echo "  - Max Reminders: $SCHEDULER_MAX_REMINDERS"

# Wait for MongoDB to be ready (if using external MongoDB)
echo "⏳ Waiting for MongoDB connection..."
python3 -c "
import pymongo
import time
import os
import sys

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        client = pymongo.MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print('✅ MongoDB connection successful')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ MongoDB connection attempt {retry_count}/{max_retries} failed: {e}')
        if retry_count >= max_retries:
            print('❌ Failed to connect to MongoDB after maximum retries')
            sys.exit(1)
        time.sleep(2)
"

# Setup scheduler state file path
export SCHEDULER_STATE_FILE="/app/data/daily_report_state.json"

# Start the FastAPI application with scheduler
echo "🤖 Starting Agent Report Service with Scheduler..."
echo "📅 Scheduler will check at: $SCHEDULER_CHECK_TIMES"
exec uvicorn main:app --host $API_HOST --port $API_PORT --log-level $(echo $LOG_LEVEL | tr '[:upper:]' '[:lower:]')