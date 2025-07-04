# ==========================================
# main.py
# Clean FastAPI Application Entry Point
# ==========================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
import uvicorn

from src.agents.agent_report import AgentReporter
from src.tools.tool_registry import tool_registry
from src.scheduler.scheduler_service import SchedulerService
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    try:
        SchedulerService().start()
        logger.info("🚀 Application started with scheduler")
    except Exception as e:
        logger.error(f"❌ Error starting scheduler: {str(e)}")

    yield

    # Shutdown
    try:
        SchedulerService().stop()
        logger.info("⏹️ Application shutdown with scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {str(e)}")

# Initialize FastAPI app
config_debug = config.AppConfig.from_env()
app = FastAPI(
    title="Agent Report Service",
    description="AI-powered report generation service with automated scheduling",
    version="2.0.0",
    debug=config_debug.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ReportRequest(BaseModel):
    sheet_url: str
    additional_context: Optional[str] = ""

class ReportResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    agent: str
    context: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    tools_available: int

# Initialize agent with tools
def get_agent() -> AgentReporter:
    """Get initialized agent with tools"""
    agent = AgentReporter()
    tools = tool_registry.get_langchain_tools()
    agent.add_tools(tools)

    # Debug logging
    logger.info(f"🤖 Agent initialized with {len(tools)} tools")
    for tool in tools:
        logger.info(f"🔧 Tool available: {tool.name} - {tool.description}")

    return agent

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        tools_count = len(tool_registry.get_all_tools())
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            tools_available=tools_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate report from Google Sheets data"""
    try:
        logger.info(f"📊 Report generation requested for: {request.sheet_url}")

        # Get agent and generate report
        agent = get_agent()
        result = agent.generate_report(
            sheet_url=request.sheet_url,
            additional_context=request.additional_context or ""
        )

        if result.get("success"):
            logger.success("Report generated successfully")
            return ReportResponse(
                success=True,
                output=result.get("output"),
                agent=result.get("agent", "ReportAgent"),
                context=result.get("context")
            )
        else:
            logger.error(f"Report generation failed: {result.get('error')}")
            return ReportResponse(
                success=False,
                error=result.get("error"),
                agent=result.get("agent", "ReportAgent")
            )

    except Exception as e:
        error_msg = f"Unexpected error during report generation: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/tools")
async def list_tools():
    """List available tools"""
    try:
        tools = tool_registry.list_tool_names()
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving tools")

@app.get("/test-slack")
async def test_slack_connection():
    """Test Slack connection and configuration"""
    try:
        from src.tools.send_slack_message import SendSlackMessageTool

        slack_tool = SendSlackMessageTool()

        # Test connection
        connection_result = slack_tool.test_slack_connection()
        config_slack = config.SlackConfig.from_env()
        # Test basic configuration
        config_status = {
            "bot_token_configured": bool(config_slack.bot_token),
            "bot_token_format_valid": config_slack.bot_token.startswith('xoxb-') if config_slack.bot_token else False,
            "user_id_configured": bool(config_slack.user_id),
            "user_id_format_valid": config_slack.user_id.startswith('U') if config_slack.user_id else False
        }

        return {
            "config_status": config_status,
            "connection_test": connection_result
        }

    except Exception as e:
        logger.error(f"Error testing Slack: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Slack test failed: {str(e)}")

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status and configuration"""
    try:
        return SchedulerService().get_status()
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scheduler status error: {str(e)}")

@app.post("/scheduler/trigger")
async def trigger_manual_check():
    """Trigger manual scheduler check (for testing)"""
    try:
        result = SchedulerService().trigger_manual_check()
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    except Exception as e:
        logger.error(f"Error triggering manual check: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Manual check error: {str(e)}")

# Legacy endpoint for backward compatibility
@app.post("/legacy/run")
async def legacy_run(request: Dict[str, Any]):
    """Legacy endpoint for backward compatibility"""
    try:
        user_input = request.get("user_input", "")
        sheet_url = request.get("sheet_url")

        if not user_input:
            raise HTTPException(status_code=400, detail="user_input is required")

        agent = get_agent()
        result = agent.run(user_input=user_input, sheet_url=sheet_url)

        return result

    except HTTPException:
        # Re-raise HTTPException as-is (preserves status code)
        raise
    except Exception as e:
        error_msg = f"Legacy endpoint error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    logger.info("🚀 Starting Agent Report Service")
    logger.info(f"📊 Configuration: Debug={config_debug.debug}, Log Level={config_debug.log_level}")
    config_api = config.AppConfig.from_env()
    uvicorn.run(
        "main:app",
        host=config_api.api_host,
        port=config_api.api_port,
        reload=config_api.debug,
        log_level=config_api.log_level.lower()
    )