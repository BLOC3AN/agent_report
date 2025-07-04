# ==========================================
# src/scheduler/state_manager.py
# Daily Report State Management
# ==========================================

import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional
from enum import Enum
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

class ReportStatus(Enum):
    """Report status enumeration"""
    PENDING = "PENDING"
    CHECKING = "CHECKING"
    FOUND = "FOUND"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REMINDED = "REMINDED"
    WAITING = "WAITING"

class DailyStateManager:
    """Manages daily report generation state"""

    def __init__(self, state_file: Optional[str] = None):
        # Use environment variable or default path
        if state_file is None:
            state_file = os.getenv("SCHEDULER_STATE_FILE", "daily_report_state.json")

        self.state_file = state_file

        # Ensure directory exists
        state_dir = os.path.dirname(self.state_file)
        if state_dir and not os.path.exists(state_dir):
            os.makedirs(state_dir, exist_ok=True)

        self.state_data = self._load_state()
        logger.info(f"📊 Daily State Manager initialized with file: {self.state_file}")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"📂 State loaded from {self.state_file}")
                    return data
            else:
                logger.info("📂 No existing state file, starting fresh")
                return {}
        except Exception as e:
            logger.error(f"❌ Error loading state: {str(e)}")
            return {}
    
    def _save_state(self):
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state_data, f, indent=2, default=str)
            logger.info(f"💾 State saved to {self.state_file}")
        except Exception as e:
            logger.error(f"❌ Error saving state: {str(e)}")
    
    def get_today_key(self) -> str:
        """Get today's date key"""
        return date.today().isoformat()
    
    def get_today_state(self) -> Dict[str, Any]:
        """Get today's state"""
        today_key = self.get_today_key()
        if today_key not in self.state_data:
            # Initialize today's state
            self.state_data[today_key] = {
                "date": today_key,
                "status": ReportStatus.PENDING.value,
                "check_count": 0,
                "last_check": None,
                "report_found": False,
                "notifications_sent": 0,
                "completed_at": None,
                "error_count": 0,
                "last_error": None
            }
            self._save_state()
        
        return self.state_data[today_key]
    
    def update_status(self, status: ReportStatus, **kwargs):
        """Update today's status"""
        today_state = self.get_today_state()
        today_state["status"] = status.value
        today_state["last_check"] = datetime.now().isoformat()
        
        # Update additional fields
        for key, value in kwargs.items():
            if key in today_state:
                today_state[key] = value
        
        self._save_state()
        logger.info(f"📊 Status updated to: {status.value}")
    
    def increment_check_count(self):
        """Increment check count"""
        today_state = self.get_today_state()
        today_state["check_count"] += 1
        self._save_state()
        logger.info(f"🔍 Check count: {today_state['check_count']}")
    
    def increment_notification_count(self):
        """Increment notification count"""
        today_state = self.get_today_state()
        today_state["notifications_sent"] += 1
        self._save_state()
        logger.info(f"📢 Notifications sent: {today_state['notifications_sent']}")
    
    def mark_report_found(self):
        """Mark report as found"""
        self.update_status(ReportStatus.FOUND, report_found=True)
    
    def mark_completed(self):
        """Mark today as completed"""
        self.update_status(
            ReportStatus.COMPLETED, 
            completed_at=datetime.now().isoformat()
        )
    
    def mark_failed(self, error_message: str):
        """Mark today as failed"""
        today_state = self.get_today_state()
        today_state["error_count"] += 1
        self.update_status(
            ReportStatus.FAILED,
            last_error=error_message
        )
    
    def is_completed_today(self) -> bool:
        """Check if today is already completed"""
        today_state = self.get_today_state()
        return today_state["status"] == ReportStatus.COMPLETED.value
    
    def should_send_reminder(self) -> bool:
        """Check if should send reminder"""
        today_state = self.get_today_state()
        return (
            today_state["notifications_sent"] < config.SchedulerConfig.from_env().max_reminders and
            not today_state["report_found"] and
            today_state["status"] not in [ReportStatus.COMPLETED.value, ReportStatus.PROCESSING.value]
        )
    
    def get_reminder_count(self) -> int:
        """Get current reminder count"""
        today_state = self.get_today_state()
        return today_state["notifications_sent"]
    
    def cleanup_old_states(self, days_to_keep: int = 30):
        """Clean up old state data"""
        try:
            cutoff_date = date.today().replace(day=date.today().day - days_to_keep)
            keys_to_remove = []
            
            for date_key in self.state_data.keys():
                try:
                    state_date = datetime.fromisoformat(date_key).date()
                    if state_date < cutoff_date:
                        keys_to_remove.append(date_key)
                except:
                    continue
            
            for key in keys_to_remove:
                del self.state_data[key]
            
            if keys_to_remove:
                self._save_state()
                logger.info(f"🧹 Cleaned up {len(keys_to_remove)} old state entries")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up old states: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        today_state = self.get_today_state()
        return {
            "today": self.get_today_key(),
            "status": today_state["status"],
            "check_count": today_state["check_count"],
            "notifications_sent": today_state["notifications_sent"],
            "report_found": today_state["report_found"],
            "completed": self.is_completed_today(),
            "should_remind": self.should_send_reminder()
        }

# Global state manager instance
state_manager = DailyStateManager()
