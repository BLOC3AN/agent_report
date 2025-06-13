# Agent Report Service

A microservice that automatically generates daily reports from Google Sheets data using AI.

## Overview

This service connects to a specified Google Sheet, extracts the latest data, and uses Gemini 2.0 Flash to generate a formatted daily report. The service is containerized and can be deployed as a standalone microservice.

## Architecture

```
agent-report-service/
├── deployment/               # Deployment configuration
│   ├── Dockerfile            # Container definition
│   ├── docker-compose.yml    # Service orchestration
│   └── requirements.txt      # Python dependencies
├── src/
│   ├── agents/               # Agent implementations
│   │   └── agent_report.py   # Main reporting agent
│   ├── prompt/               # Prompt templates
│   │   └── agent_report.md   # System prompt for report generation
│   ├── tools/                # Tool implementations
│   │   └── get_data_ggSheet.py # Google Sheet data extraction
│   └── notebook/             # Development notebooks
│       ├── test_agent.ipynb  # Agent testing
│       └── test_API_ggSheet.ipynb # Google Sheet API testing
├── env/                      # Environment configuration (gitignored)
│   └── credentials.json      # Google API credentials
├── main.py                   # FastAPI application entry point
└── .gitignore                # Git ignore configuration
```

## Components

### 1. Agent System

- **AgentReporter** (`src/agents/agent_report.py`): Main agent class that orchestrates the report generation process. It loads the system prompt, initializes the LLM, binds tools, and manages the conversation flow.

### 2. Tools

- **get_information_from_url** (`src/tools/get_data_ggSheet.py`): Tool for extracting data from Google Sheets. It converts the sheet URL to a CSV export URL, downloads the data, and returns the most recent entry.

### 3. Prompts

- **agent_report.md** (`src/prompt/agent_report.md`): System prompt that defines the agent's role, instructions, and report format. It guides the LLM to generate consistent reports.

### 4. API

- **main.py**: FastAPI application that exposes endpoints for report generation and health checks. It initializes the agent and handles HTTP requests.

### 5. Deployment

- **Dockerfile**: Defines the container image, including dependencies, environment setup, and runtime configuration.
- **docker-compose.yml**: Orchestrates the service deployment, including port mapping, environment variables, and health checks.
- **requirements.txt**: Lists all Python dependencies required by the service.

## Workflow

1. The service receives a request to the `/report` endpoint
2. The `AgentReporter` is initialized with the Google Sheet URL
3. The agent sends a message to the LLM requesting data extraction
4. The LLM calls the `get_information_from_url` tool to fetch data from Google Sheets
5. The tool returns the structured data to the LLM
6. The LLM generates a formatted report based on the data and system prompt
7. The report is returned to the client

## Authentication

The service uses Google Service Account credentials to authenticate with the Google Sheets API. The credentials are stored in a JSON file and mounted into the container at runtime.

## Deployment

```bash
# Build and start the service
docker-compose -f deployment/docker-compose.yml up -d

# Check service status
curl http://localhost:7700/health

# Generate a report
curl http://localhost:7700/report
```

## Development

1. Create a virtual environment: `python -m venv venv`
2. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r deployment/requirements.txt`
4. Set environment variables:
   - `url`: Google Sheet URL
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google credentials JSON file
5. Run the service: `python main.py` or `uvicorn main:app --reload`

## Testing

The `src/notebook/` directory contains Jupyter notebooks for testing:
- `test_agent.ipynb`: Tests the agent's functionality
- `test_API_ggSheet.ipynb`: Tests Google Sheets API connectivity

## License

[MIT License](LICENSE)