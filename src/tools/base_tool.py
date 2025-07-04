# ==========================================
# src/tools/base_tool.py
# Base Tool Implementation
# ==========================================

from typing import Dict, Any
from src.core.interfaces import BaseTool
from src.logs.logger import Logger

logger = Logger(__name__)

class SimpleBaseTool(BaseTool):
    """Simple base implementation of BaseTool"""

    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.logger = Logger(f"Tool.{name}")

    def get_schema(self) -> Dict[str, Any]:
        """Default schema - override in subclasses"""
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

    def to_langchain_tool(self):
        """Convert to LangChain compatible tool using @tool decorator"""
        from langchain_core.tools import tool
        import json

        # Create a wrapper function for the tool
        def tool_func(input_str: str) -> str:
            try:
                # Parse JSON input string
                try:
                    params = json.loads(input_str)
                except json.JSONDecodeError:
                    # If not valid JSON, handle as single parameter
                    schema = self.get_schema()
                    required = schema.get('required', [])
                    if required:
                        params = {required[0]: input_str}
                    else:
                        params = {"input": input_str}

                result = self.execute(**params)
                self.logger.info(f"🔧 Tool '{self.name}' executed successfully")

                # Convert result to string for LangChain
                if isinstance(result, dict):
                    if "error" in result:
                        return f"Error: {result['error']}"
                    # Format dict results nicely
                    if self.name == "get_information_from_url":
                        formatted = "Latest data from Google Sheet:\n"
                        for key, value in result.items():
                            # Ensure full content is preserved
                            full_value = str(value).replace('\\n', '\n') if value else ""
                            formatted += f"{key}: {full_value}\n"
                        return formatted
                    # For save_chat_history_DB, return success message
                    elif self.name == "save_chat_history_DB":
                        if result.get("status") == "success":
                            return f"✅ Chat history saved successfully. Document ID: {result.get('document_id')}"
                        else:
                            return f"❌ Failed to save: {result.get('message')}"
                    return str(result)

                return str(result)

            except Exception as e:
                self.logger.error(f"❌ Error executing tool '{self.name}': {str(e)}")
                return f"Error: {str(e)}"

        # Set function metadata for the tool decorator
        tool_func.__name__ = self.name.replace('-', '_').replace(' ', '_')
        tool_func.__doc__ = self.description

        # Apply the @tool decorator
        langchain_tool = tool(tool_func)

        return langchain_tool
