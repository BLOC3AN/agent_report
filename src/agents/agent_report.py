# ==========================================
# src/agents/agent_report.py
# Refactored Report Agent using new architecture
# ==========================================

from typing import Dict, Any, Optional
from src.agents.base_agent import LangChainBaseAgent
from src.core.interfaces import AgentContext
from src.llms.gemini import GeminiLLM
from src.logs.logger import Logger

logger = Logger(__name__)

class AgentReporter(LangChainBaseAgent):
    """Specialized agent for generating reports from data sources"""

    def __init__(self):
        llm_provider = GeminiLLM()
        super().__init__(
            name="ReportAgent",
            llm_provider=llm_provider,
            prompt_file_path="src/prompts/agent_report.md"
        )
        logger.info("📊 Report Agent initialized successfully")

    def generate_report(self, sheet_url: str, additional_context: str = "") -> Dict[str, Any]:
        """Generate a report from the specified Google Sheet URL"""
        user_input = f"""Generate a report from the Google Sheet.
        Get the latest information by date and translate to English.
        Ensure to save the conversation history to MongoDB after completion.
        {additional_context}

        Follow the required output format and create a summary table by date."""

        context = AgentContext(
            user_input=user_input,
            conversation_history=[],
            metadata={
                "task_type": "report_generation",
                "output_format": "structured_report"
            },
            sheet_url=sheet_url
        )

        return self.process(context)

    def run(self, user_input: str, sheet_url: Optional[str] = None) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        context = AgentContext(
            user_input=user_input,
            conversation_history=[],
            metadata={"task_type": "general"},
            sheet_url=sheet_url
        )
        return self.process(context)

    def _get_default_prompt(self) -> str:
        """Default prompt for report agent"""
        return """You are an AI assistant specialized in generating daily reports from data sources.

Your role:
1. Extract data from Google Sheets using available tools
2. Translate content from any language to English
3. Create structured reports following the specified format
4. Save conversation history to MongoDB after completion

Report Format:
**Date**: Day report in format *dd/mm/yyyy*
**Completed**: Amount of completed tasks
**In Progress**: Amount of tasks in progress
**Blocked**: Amount of blocked tasks

Instructions:
1. Use get_information_from_url tool to get data from Google Sheet
2. Translate from any language to English
3. Create report in English from the latest data by date
4. IMPORTANT: Use save_chat_history_DB tool to save the entire conversation to MongoDB
5. Ensure you use both tools in the correct order
6. Create a summary table with information by date

Always follow the exact format and ensure data accuracy."""
