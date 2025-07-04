# Agent Report Service

A clean, modular microservice that automatically generates daily reports from Google Sheets data using AI.

## Overview

This refactored service provides a clean, maintainable architecture for AI-powered report generation. It connects to Google Sheets, extracts the latest data, and uses Gemini 2.0 Flash to generate formatted daily reports with proper error handling and configuration management.

## Architecture

```
agent-report-service/
├── src/
│   ├── agents/               # Agent implementations
│   │   ├── base_agent.py     # Base agent class
│   │   └── agent_report.py   # Report generation agent
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py       # Centralized configuration
│   ├── core/                 # Core interfaces and abstractions
│   │   ├── __init__.py
│   │   └── interfaces.py     # Abstract base classes
│   ├── db/                   # Database integrations
│   │   └── mongo/
│   │       └── mongo_db.py   # MongoDB operations
│   ├── llms/                 # LLM providers
│   │   └── gemini.py         # Gemini LLM integration
│   ├── logs/                 # Logging system
│   │   └── logger.py         # Enhanced logger
│   ├── prompts/              # Prompt templates
│   │   └── agent_report.md   # System prompt for reports
│   └── tools/                # Tool implementations
│       ├── base_tool.py      # Base tool class
│       ├── get_information_from_url.py # Google Sheets data extraction
│       ├── save_chat_history_DB.py     # MongoDB persistence
│       └── tool_registry.py  # Tool management
├── tests/                    # Unit tests
│   ├── test_agents.py
│   ├── test_api.py
│   ├── test_config.py
│   └── test_tools.py
├── deployment/               # Deployment configuration
├── main.py                   # FastAPI application entry point
├── pytest.ini               # Test configuration
└── requirements-test.txt     # Testing dependencies
```

## Key Features

### 🏗️ Clean Architecture
- **Separation of Concerns**: Clear separation between agents, tools, configuration, and data layers
- **Dependency Injection**: Configurable LLM providers and database connections
- **Interface-Based Design**: Abstract base classes for extensibility

### 🔧 Tool System
- **Simple Tool Registry**: Easy tool discovery and management
- **LangChain Integration**: Seamless integration with LangChain framework
- **Error Handling**: Robust error handling and logging

### ⚙️ Configuration Management
- **Environment-Based**: All configuration through environment variables
- **Type Safety**: Strongly typed configuration with validation
- **Hierarchical**: Nested configuration objects for organization

### 🧪 Testing
- **Comprehensive Tests**: Unit tests for all major components
- **Mocking**: Proper mocking for external dependencies
- **Coverage**: Test coverage reporting with pytest-cov

## Components

### 1. Agent System
- **BaseAgent** (`src/agents/base_agent.py`): Abstract base class with common functionality
- **AgentReporter** (`src/agents/agent_report.py`): Specialized report generation agent
- **LangChain Integration**: Uses LangChain's ReAct agent pattern

### 2. Tool System
- **GetInformationFromURLTool**: Extracts data from Google Sheets with smart CSV parsing
- **SaveChatHistoryTool**: Persists conversation history to MongoDB
- **ToolRegistry**: Centralized tool management and discovery

### 3. Configuration
- **Centralized Settings**: All configuration in `src/config/settings.py`
- **Environment Variables**: Configurable through environment variables
- **Validation**: Automatic configuration validation on startup

### 4. Database
- **MongoDB Integration**: Async-ready MongoDB operations
- **Interface-Based**: Abstract database interface for flexibility
- **Error Handling**: Comprehensive error handling and logging

## API Endpoints

### Health Check
```bash
GET /health
```
Returns service health status and available tools count.

### Generate Report
```bash
POST /report
Content-Type: application/json

{
  "sheet_url": "https://docs.google.com/spreadsheets/d/your_sheet_id/edit",
  "additional_context": "Optional additional context"
}
```

### List Tools
```bash
GET /tools
```
Returns available tools and their count.

### Legacy Endpoint
```bash
POST /legacy/run
Content-Type: application/json

{
  "user_input": "Generate report from sheet",
  "sheet_url": "https://docs.google.com/spreadsheets/d/your_sheet_id/edit"
}
```

## Configuration

### Environment Variables
```bash
# Application
DEBUG=false
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=5000

# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=agent_reports
MONGODB_COLLECTION_NAME=chat_history

# LLM
LLM_MODEL=gemini-2.0-flash
LLM_TEMPERATURE=0.7
LLM_TOP_P=0.8
LLM_TOP_K=40
LLM_MAX_TOKENS=2048
LLM_VERBOSE=false

# Google Sheets (optional)
DEFAULT_SHEET_URL=your_default_sheet_url
```

## Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Start development server
python main.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

## Deployment

### Docker
```bash
# Build and start
docker-compose -f deployment/docker-compose.yml up -d

# Check logs
docker-compose -f deployment/docker-compose.yml logs -f

# Stop
docker-compose -f deployment/docker-compose.yml down
```

### Local Development
```bash
# Start the service
python main.py

# Service will be available at:
# - API: http://localhost:5000
# - Health: http://localhost:5000/health
# - Docs: http://localhost:5000/docs
```

## Workflow

1. **Request**: Client sends POST request to `/report` endpoint with Google Sheet URL
2. **Initialization**: AgentReporter is initialized with configured tools
3. **Data Extraction**: Agent uses `get_information_from_url` tool to fetch latest data
4. **Processing**: LLM processes data and generates structured report in English
5. **Persistence**: Agent uses `save_chat_history_DB` tool to save conversation to MongoDB
6. **Response**: Formatted report is returned to client

## Architecture Benefits

### 🔧 Maintainability
- **Clean Separation**: Clear boundaries between components
- **Single Responsibility**: Each class has a focused purpose
- **Dependency Injection**: Easy to test and modify

### 🚀 Scalability
- **Modular Design**: Easy to add new agents and tools
- **Configuration-Driven**: Environment-based configuration
- **Interface-Based**: Easy to swap implementations

### 🧪 Testability
- **Unit Tests**: Comprehensive test coverage
- **Mocking**: Proper isolation of dependencies
- **CI/CD Ready**: Automated testing pipeline

## License

[MIT License](LICENSE)