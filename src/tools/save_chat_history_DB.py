# ==========================================
# src/tools/save_chat_history_DB.py
# Refactored Chat History Saving Tool
# ==========================================

from typing import Dict, Any
from datetime import datetime
from src.tools.base_tool import SimpleBaseTool
from src.db.mongo.mongo_db import MongoDB
from src.logs.logger import Logger

logger = Logger(__name__)

class SaveChatHistoryTool(SimpleBaseTool):
    """Tool for saving chat history to MongoDB"""

    def __init__(self):
        super().__init__(
            name="save_chat_history_DB",
            description="Save conversation history to MongoDB database"
        )
        self.db = MongoDB()

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool to save chat history"""
        try:
            import json

            # Handle different input formats
            if 'data' in kwargs:
                # Legacy format
                data = kwargs['data']
                document = {
                    "user_input": data.get("user_input", ""),
                    "response": data.get("response", []),
                    "conversation": data.get("conversation", {}),
                    "timestamp": datetime.now(),
                    "metadata": data.get("metadata", {})
                }
            else:
                # New format with direct parameters
                user_input = kwargs.get('user_input', '')
                response = kwargs.get('response', '')
                conversation_data = kwargs.get('conversation_data', '{}')

                # Parse conversation data
                try:
                    conversation_obj = json.loads(conversation_data) if isinstance(conversation_data, str) else conversation_data
                except:
                    conversation_obj = conversation_data

                document = {
                    "user_input": user_input,
                    "response": [
                        {
                            "role": "assistant",
                            "content": response
                        }
                    ],
                    "conversation": conversation_obj,
                    "timestamp": datetime.now(),
                    "metadata": {
                        "tool_used": "save_chat_history_DB",
                        "source": "langchain_agent",
                        "agent_type": "report_agent"
                    }
                }

            # Debug logging
            self.logger.info(f"📝 Saving document with user_input length: {len(document.get('user_input', ''))}")
            if document.get('response') and len(document['response']) > 0:
                content_length = len(document['response'][0].get('content', ''))
                self.logger.info(f"📝 Response content length: {content_length}")

            # Insert into MongoDB
            result = self.db.insert_one(document)

            self.logger.info("✅ Chat history saved successfully with new schema")
            return {
                "status": "success",
                "document_id": str(result.inserted_id),
                "message": "Chat history saved successfully with new schema."
            }

        except Exception as e:
            error_msg = f"Error saving chat history: {str(e)}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's input schema"""
        return {
            "type": "object",
            "properties": {
                "user_input": {
                    "type": "string",
                    "description": "Original user input/request"
                },
                "response": {
                    "type": "string",
                    "description": "Agent's final response/report"
                },
                "conversation_data": {
                    "type": "string",
                    "description": "Raw data extracted from Google Sheets (JSON format)"
                }
            },
            "required": ["user_input", "response", "conversation_data"]
        }



# Legacy function for backward compatibility
def save_chat_history(data):
    """Legacy implementation"""
    tool = SaveChatHistoryTool()
    return tool.execute(data=data)
    
