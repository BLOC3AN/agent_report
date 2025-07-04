# ==========================================
# src/tools/send_slack_message.py
# Slack Message Sending Tool
# ==========================================

import requests
from typing import Dict, Any
from src.tools.base_tool import SimpleBaseTool
from src.config import config
from src.logs.logger import Logger

logger = Logger(__name__)

class SendSlackMessageTool(SimpleBaseTool):
    """Tool for sending messages to Slack"""
    
    def __init__(self):
        super().__init__(
            name="send_slack_message",
            description="Send a message to Slack user via direct message"
        )
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool to send Slack message"""
        try:
            # Extract parameters
            message = kwargs.get('message', '')
            target_id = kwargs.get('user_id') or kwargs.get('channel_id') or config.slack.channel_id or config.slack.user_id

            if not message:
                return {"error": "Message parameter is required"}

            if not config.slack.bot_token:
                return {"error": "Slack bot token not configured. Please set SLACK_BOT_TOKEN in .env file"}

            if not target_id:
                return {"error": "No target specified. Please set SLACK_USER_ID or SLACK_CHANNEL_ID in .env file"}

            # Validate token format
            if not config.slack.bot_token.startswith('xoxb-'):
                return {"error": "Invalid Slack bot token format. Token should start with 'xoxb-'"}

            # Determine target type
            if target_id.startswith('C'):
                self.logger.info(f"📢 Sending to channel: {target_id}")
                target_type = "channel"
            elif target_id.startswith('U'):
                self.logger.info(f"👤 Sending to user: {target_id}")
                target_type = "user"
            else:
                self.logger.warning(f"⚠️ Unknown target format: {target_id}")
                target_type = "unknown"

            # Send message via Slack API
            result = self._send_slack_message(message, target_id, target_type)
            
            if result.get("success"):
                self.logger.info("✅ Slack message sent successfully")
                return {
                    "status": "success",
                    "message": "Message sent to Slack successfully",
                    "channel": result.get("channel"),
                    "timestamp": result.get("timestamp")
                }
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ Failed to send Slack message: {error_msg}")
                return {"error": f"Failed to send Slack message: {error_msg}"}
                
        except Exception as e:
            error_msg = f"Error sending Slack message: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}
    
    def _send_slack_message(self, message: str, target_id: str, target_type: str = "user") -> Dict[str, Any]:
        """Send message to Slack using Web API"""
        try:
            # Determine channel ID based on target type
            if target_type == "channel" or target_id.startswith('C'):
                # Direct channel ID
                channel_id = target_id
                self.logger.info(f"📢 Using channel directly: {channel_id}")
            else:
                # Try to open DM channel with user
                dm_channel = self._open_dm_channel(target_id)
                if not dm_channel.get("success"):
                    return dm_channel
                channel_id = dm_channel.get("channel_id")

            # Slack API endpoint
            url = "https://slack.com/api/chat.postMessage"

            # Headers
            headers = {
                "Authorization": f"Bearer {config.slack.bot_token}",
                "Content-Type": "application/json"
            }

            # Format message for better readability
            formatted_message = self._format_report_message(message)

            # Simplified payload
            payload = {
                "channel": channel_id,
                "text": formatted_message,
                "username": "Report Agent",
                "icon_emoji": ":robot_face:"
            }

            self.logger.info(f"🔍 Sending to channel: {channel_id}")
            self.logger.info(f"🔍 Payload: {payload}")

            # Send request
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            self.logger.info(f"🔍 Slack API response: {result}")

            if result.get("ok"):
                return {
                    "success": True,
                    "channel": result.get("channel"),
                    "timestamp": result.get("ts")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown Slack API error")
                }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"HTTP request failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _open_dm_channel(self, user_id: str) -> Dict[str, Any]:
        """Open a DM channel with the user"""
        try:
            url = "https://slack.com/api/conversations.open"
            headers = {
                "Authorization": f"Bearer {config.slack.bot_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "users": user_id
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()

            if result.get("ok"):
                return {
                    "success": True,
                    "channel_id": result.get("channel", {}).get("id")
                }
            else:
                # Fallback: try using user_id directly
                self.logger.warning(f"⚠️ Failed to open DM channel: {result.get('error')}, trying direct user ID")
                return {
                    "success": True,
                    "channel_id": user_id
                }

        except Exception as e:
            # Fallback: use user_id directly
            self.logger.warning(f"⚠️ Error opening DM channel: {str(e)}, using direct user ID")
            return {
                "success": True,
                "channel_id": user_id
            }
    
    def _format_report_message(self, message: str) -> str:
        """Format the report message for Slack"""
        # Add header
        formatted = "📊 *Daily Report*\n\n"
        
        # Format the message content
        formatted += message
        
        # Add footer
        formatted += "\n\n_Generated by Report Agent_ 🤖"
        
        return formatted
    
    def test_slack_connection(self) -> Dict[str, Any]:
        """Test Slack connection and permissions"""
        try:
            url = "https://slack.com/api/auth.test"
            headers = {
                "Authorization": f"Bearer {config.slack.bot_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers)
            result = response.json()

            if result.get("ok"):
                return {
                    "success": True,
                    "bot_id": result.get("bot_id"),
                    "user_id": result.get("user_id"),
                    "team": result.get("team"),
                    "url": result.get("url")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Auth test failed")
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's input schema"""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message content to send to Slack"
                },
                "user_id": {
                    "type": "string",
                    "description": "Slack user ID to send message to (optional, uses default from config)"
                }
            },
            "required": ["message"]
        }

# Test function for debugging
if __name__ == "__main__":
    tool = SendSlackMessageTool()

    # Test connection
    print("Testing Slack connection...")
    connection_test = tool.test_slack_connection()
    print(f"Connection test: {connection_test}")

    # Test message sending
    if connection_test.get("success"):
        print("Testing message sending...")
        result = tool.execute(message="Test message from Report Agent 🤖")
        print(f"Message test: {result}")
    else:
        print("❌ Connection failed, skipping message test")
