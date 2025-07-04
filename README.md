# 🤖 Auto Report Agent

AI-powered automated daily report generation service with intelligent scheduling and Slack integration.

## ✨ Features

- 🤖 **AI Report Generation** - Powered by Google Gemini 2.0 Flash
- 📊 **Google Sheets Integration** - Automatic data extraction and processing  
- 📅 **Smart Scheduling** - Daily checks at 10am, 12pm, 3pm
- 💬 **Slack Notifications** - Direct message delivery with reminders
- 🗄️ **MongoDB Storage** - Conversation history and report persistence
- 🔄 **Auto Retry** - Up to 3 reminder messages if no report found
- 🐳 **Docker Ready** - Containerized deployment with Docker Compose
- 🧪 **Full Test Coverage** - Comprehensive unit tests with CI/CD

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone <repository-url>
cd auto_report_agent
cp .env.example .env  # Configure your environment variables
```

### 2. Environment Configuration
```bash
# Required - Google AI API Key
GOOGLE_API_KEY=your_gemini_api_key

# Required - Slack Integration  
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_ID=U1234567890

# Required - MongoDB (Atlas recommended)
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname

# Optional - Default Google Sheets URL
DEFAULT_SHEET_URL=https://docs.google.com/spreadsheets/d/your-sheet-id

# Optional - Scheduler Settings
SCHEDULER_ENABLED=true
SCHEDULER_CHECK_TIMES=10:00,12:00,15:00
SCHEDULER_MAX_REMINDERS=3
```

### 3. Run with Docker (Recommended)
```bash
# Start all services
make docker-run

# Or manually
docker compose -f deployment/docker-compose.yml up -d

# Check logs
make logs
```

### 4. Run Locally
```bash
# Install dependencies
make install-dev

# Start the service
make run

# Service available at http://localhost:5000
```

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/docs` | API documentation |
| `POST` | `/generate-report` | Generate report manually |
| `GET` | `/scheduler/status` | Check scheduler status |
| `POST` | `/scheduler/trigger` | Trigger manual check |

## 🛠️ Development

### Available Commands
```bash
# Development
make install-dev    # Install dev dependencies
make run           # Run locally
make test          # Run tests
make lint          # Code linting
make format        # Format code

# Docker
make docker-run    # Start with Docker
make docker-stop   # Stop containers
make logs          # View logs

# CI/CD
make ci-test       # Run CI pipeline locally
```

### Project Structure
```
auto_report_agent/
├── src/
│   ├── agents/           # AI agents
│   ├── config/           # Configuration
│   ├── tools/            # LangChain tools
│   ├── scheduler/        # Scheduling system
│   ├── db/mongo/         # Database operations
│   └── logs/             # Logging system
├── tests/                # Unit tests
├── deployment/           # Docker & deployment
├── .github/workflows/    # CI/CD pipelines
└── main.py              # FastAPI app
```

## 📊 How It Works

### Daily Report Flow
1. **📅 Scheduled Check** - System checks Google Sheets at configured times
2. **🔍 Data Validation** - Verifies today's report data exists
3. **🤖 AI Processing** - Gemini generates comprehensive report
4. **💾 Storage** - Saves to MongoDB for history
5. **💬 Slack Delivery** - Sends report via direct message
6. **🔔 Smart Reminders** - Up to 3 reminders if no data found

### Manual Usage
```bash
# Check system status
curl http://localhost:5000/health

# Trigger manual report generation
curl -X POST http://localhost:5000/scheduler/trigger

# Generate report with custom data
curl -X POST http://localhost:5000/generate-report \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Generate daily report", "sheet_url": "your-sheet-url"}'
```

## 🔧 Configuration

### Required Environment Variables
```bash
# AI & LLM
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.0-flash

# Slack Integration
SLACK_BOT_TOKEN=xoxb-your-bot-token  
SLACK_USER_ID=U1234567890

# Database
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
MONGODB_DB_NAME=agent_reports
MONGODB_COLLECTION_NAME=daily_reports
```

### Optional Settings
```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=5000

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_TIMEZONE=Asia/Ho_Chi_Minh
SCHEDULER_CHECK_TIMES=10:00,12:00,15:00
SCHEDULER_MAX_REMINDERS=3

# Google Sheets
DEFAULT_SHEET_URL=https://docs.google.com/spreadsheets/d/your-sheet-id
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_agents.py -v

# Test Docker build
make ci-test
```

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy
docker compose -f deployment/docker-compose.yml up -d

# Health check
curl http://your-server:5000/health

# Monitor logs
docker compose -f deployment/docker-compose.yml logs -f
```

### CI/CD Pipeline
- ✅ **Automated Testing** - Runs on every push/PR
- ✅ **Code Quality** - Linting, type checking, security scans
- ✅ **Docker Build** - Automatic image building and publishing
- ✅ **Release Management** - Automated releases with changelogs

## 📝 Google Sheets Format

Your Google Sheets should have these columns:
```
| Date       | Completed | In Progress | Blocker |
|------------|-----------|-------------|---------|
| 04/07/2025 | Task 1    | Task 2      | Issue 1 |
```

## 🔍 Troubleshooting

### Common Issues
```bash
# Check service status
make logs

# Test MongoDB connection
docker compose exec agent-report python -c "from src.db.mongo.mongo_db import MongoDB; db = MongoDB(); print('✅ MongoDB connected')"

# Test Slack integration
curl -X GET http://localhost:5000/slack/test

# Verify environment variables
docker compose exec agent-report env | grep -E "(GOOGLE_API_KEY|SLACK_|MONGODB_)"
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG
make run
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Made with ❤️ for automated daily reporting**
