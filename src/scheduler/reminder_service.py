# ==========================================
# src/scheduler/reminder_service.py
# Reminder and Notification Service
# ==========================================

from datetime import datetime
from typing import Dict, Any
from src.tools.send_slack_message import SendSlackMessageTool
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

class ReminderService:
    """Service for sending reminders and notifications"""
    
    def __init__(self):
        self.slack_tool = SendSlackMessageTool()
        self.logger = Logger("ReminderService")
    
    def send_reminder(self, reminder_count: int) -> Dict[str, Any]:
        """Send reminder message based on count"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            
            # Different messages based on reminder count
            if reminder_count == 0:  # First reminder (10:00)
                message = self._get_first_reminder_message(current_time)
            elif reminder_count == 1:  # Second reminder (12:00)
                message = self._get_second_reminder_message(current_time)
            elif reminder_count == 2:  # Final reminder (15:00)
                message = self._get_final_reminder_message(current_time)
            else:
                message = self._get_generic_reminder_message(current_time)
            
            # Send via Slack
            result = self.slack_tool.execute(message=message)
            
            if result.get("status") == "success":
                self.logger.info(f"✅ Reminder {reminder_count + 1} sent successfully")
                return {"success": True, "message": "Reminder sent"}
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ Failed to send reminder: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending reminder: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_success_notification(self, report_summary: str) -> Dict[str, Any]:
        """Send success notification when report is completed"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            message = f"""✅ **Daily Report Completed!**

📊 Your daily report has been successfully generated and processed at {current_time}.

📋 **Report Summary:**
{report_summary}

✨ **Actions Completed:**
• ✅ Data extracted from Google Sheets
• ✅ Report generated in English
• ✅ Saved to MongoDB database
• ✅ Notification sent to Slack

🎉 Great job on completing today's report!

_Automated by Report Agent_ 🤖"""

            result = self.slack_tool.execute(message=message)
            
            if result.get("status") == "success":
                self.logger.info("✅ Success notification sent")
                return {"success": True, "message": "Success notification sent"}
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ Failed to send success notification: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending success notification: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_error_notification(self, error_message: str) -> Dict[str, Any]:
        """Send error notification when something goes wrong"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            message = f"""❌ **Report Generation Error**

🚨 There was an issue generating your daily report at {current_time}.

**Error Details:**
{error_message}

**What to do:**
• Check your Google Sheets for today's data
• Verify the sheet is accessible
• Try generating the report manually via API

**Manual Generation:**
You can trigger a manual report by calling:
`POST /report` with your sheet URL

_Report Agent will continue checking at the next scheduled time._

_Automated by Report Agent_ 🤖"""

            result = self.slack_tool.execute(message=message)
            
            if result.get("status") == "success":
                self.logger.info("✅ Error notification sent")
                return {"success": True, "message": "Error notification sent"}
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"❌ Failed to send error notification: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending error notification: {str(e)}"
            self.logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def _get_first_reminder_message(self, current_time: str) -> str:
        """First reminder message (10:00)"""
        return f"""📋 **Daily Report Reminder #1**

⏰ **Time:** {current_time}

Hi! It's time for your daily report. I checked your Google Sheets but didn't find today's report yet.

📝 **Please add your daily report with:**
• Today's date: {datetime.now().strftime('%d/%m/%Y')}
• Completed tasks
• In Progress tasks  
• Blocked items (if any)

⏰ **Next Check:** I'll check again at 12:00 PM

_Automated by Report Agent_ 🤖"""
    
    def _get_second_reminder_message(self, current_time: str) -> str:
        """Second reminder message (12:00)"""
        return f"""📋 **Daily Report Reminder #2**

⏰ **Time:** {current_time}

This is your second reminder for today's daily report. I still haven't found your report in the Google Sheets.

📝 **Please don't forget to add:**
• Today's date: {datetime.now().strftime('%d/%m/%Y')}
• Your progress updates
• Any blockers you're facing

⏰ **Final Check:** I'll check one more time at 3:00 PM

_Automated by Report Agent_ 🤖"""
    
    def _get_final_reminder_message(self, current_time: str) -> str:
        """Final reminder message (15:00)"""
        return f"""📋 **Final Daily Report Reminder #3**

⏰ **Time:** {current_time}

This is the final reminder for today's daily report. After this, I'll stop checking for today.

📝 **Last chance to add your report:**
• Date: {datetime.now().strftime('%d/%m/%Y')}
• Your daily progress
• Any updates or blockers

⚠️ **Note:** This is the last automated check for today. If you add your report later, you can trigger manual generation via the API.

_Automated by Report Agent_ 🤖"""
    
    def _get_generic_reminder_message(self, current_time: str) -> str:
        """Generic reminder message"""
        return f"""📋 **Daily Report Reminder**

⏰ **Time:** {current_time}

Please don't forget to add your daily report to the Google Sheets.

📝 **Required:** Today's date ({datetime.now().strftime('%d/%m/%Y')}) and your progress updates.

_Automated by Report Agent_ 🤖"""

# Test function
if __name__ == "__main__":
    reminder_service = ReminderService()
    
    # Test different reminder types
    print("Testing first reminder...")
    result1 = reminder_service.send_reminder(0)
    print(f"Result: {result1}")
    
    print("\nTesting success notification...")
    result2 = reminder_service.send_success_notification("Test report completed successfully")
    print(f"Result: {result2}")
