# ==========================================
# src/scheduler/scheduler_service.py
# Main Scheduler Service
# ==========================================

import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Dict, Any

from src.scheduler.state_manager import state_manager, ReportStatus
from src.scheduler.report_checker import ReportChecker
from src.scheduler.reminder_service import ReminderService
from src.agents.agent_report import AgentReporter
from src.tools.tool_registry import tool_registry
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

class SchedulerService:
    """Main scheduler service for automated daily reports"""
    
    def __init__(self):
        self.scheduler = None
        self.report_checker = ReportChecker()
        self.reminder_service = ReminderService()
        self.timezone = pytz.timezone(config.SchedulerConfig.from_env().timezone)
        self.logger = Logger("SchedulerService")
        
        # Initialize agent
        self.agent = AgentReporter()
        tools = tool_registry.get_langchain_tools()
        self.agent.add_tools(tools)
        
        self.logger.info("🕐 Scheduler Service initialized")
    
    def start(self):
        """Start the scheduler"""
        if not config.SchedulerConfig.enabled:
            self.logger.info("⏸️ Scheduler is disabled in configuration")
            return
        
        try:
            self.scheduler = BackgroundScheduler(timezone=self.timezone)
            
            # Schedule daily checks
            for check_time in config.SchedulerConfig.check_times:
                hour, minute = map(int, check_time.split(':'))
                
                self.scheduler.add_job(
                    func=self.daily_check_job,
                    trigger=CronTrigger(hour=hour, minute=minute, timezone=self.timezone),
                    id=f"daily_check_{check_time}",
                    name=f"Daily Report Check at {check_time}",
                    max_instances=1,
                    coalesce=True
                )
                
                self.logger.info(f"📅 Scheduled daily check at {check_time}")
            
            # Schedule cleanup job (daily at midnight)
            self.scheduler.add_job(
                func=self.cleanup_job,
                trigger=CronTrigger(hour=0, minute=0, timezone=self.timezone),
                id="daily_cleanup",
                name="Daily State Cleanup",
                max_instances=1
            )
            
            self.scheduler.start()
            self.logger.info("🚀 Scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("⏹️ Scheduler stopped")
    
    def daily_check_job(self):
        """Main daily check job"""
        try:
            current_time = datetime.now().strftime("%H:%M")
            self.logger.info(f"🔍 Starting daily check at {current_time}")
            
            # Check if already completed today
            if state_manager.is_completed_today():
                self.logger.info("✅ Today's report already completed, skipping check")
                return
            
            # Update state
            state_manager.update_status(ReportStatus.CHECKING)
            state_manager.increment_check_count()
            
            # Check if report exists
            sheet_url = config.AppConfig.from_env().default_sheet_url
            if not sheet_url:
                self.logger.error("❌ No default sheet URL configured")
                state_manager.mark_failed("No sheet URL configured")
                return
            
            # Check for today's report
            report_exists, report_data = self.report_checker.check_today_report(sheet_url)
            
            if report_exists and report_data:
                self.logger.info("✅ Found today's report, processing...")
                self._process_found_report(sheet_url, report_data)
            else:
                self.logger.info("❌ No report found, sending reminder...")
                self._handle_missing_report()
                
        except Exception as e:
            error_msg = f"Error in daily check job: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            state_manager.mark_failed(error_msg)
            self.reminder_service.send_error_notification(error_msg)
    
    def _process_found_report(self, sheet_url: str, report_data: Dict[str, Any]):
        """Process found report"""
        try:
            self.logger.info("🔄 Processing found report...")
            state_manager.mark_report_found()
            state_manager.update_status(ReportStatus.PROCESSING)
            
            # Generate report using agent
            result = self.agent.generate_report(
                sheet_url=sheet_url,
                additional_context="Automated daily report generation"
            )
            
            if result.get("success"):
                # Mark as completed
                state_manager.mark_completed()
                
                # Send success notification
                report_summary = self.report_checker.get_report_summary(report_data)
                self.reminder_service.send_success_notification(report_summary)
                
                self.logger.info("🎉 Report processing completed successfully")
            else:
                error_msg = result.get("error", "Unknown error in report generation")
                self.logger.error(f"❌ Report generation failed: {error_msg}")
                state_manager.mark_failed(error_msg)
                self.reminder_service.send_error_notification(error_msg)
                
        except Exception as e:
            error_msg = f"Error processing found report: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            state_manager.mark_failed(error_msg)
            self.reminder_service.send_error_notification(error_msg)
    
    def _handle_missing_report(self):
        """Handle missing report - send reminder if appropriate"""
        try:
            if state_manager.should_send_reminder():
                reminder_count = state_manager.get_reminder_count()
                
                # Send reminder
                result = self.reminder_service.send_reminder(reminder_count)
                
                if result.get("success"):
                    state_manager.increment_notification_count()
                    state_manager.update_status(ReportStatus.REMINDED)
                    self.logger.info(f"📢 Reminder {reminder_count + 1} sent successfully")
                else:
                    error_msg = result.get("error", "Failed to send reminder")
                    self.logger.error(f"❌ Failed to send reminder: {error_msg}")
            else:
                self.logger.info("⏭️ Maximum reminders reached or conditions not met")
                state_manager.update_status(ReportStatus.WAITING)
                
        except Exception as e:
            error_msg = f"Error handling missing report: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            state_manager.mark_failed(error_msg)
    
    def cleanup_job(self):
        """Daily cleanup job"""
        try:
            self.logger.info("🧹 Running daily cleanup...")
            state_manager.cleanup_old_states()
            self.logger.info("✅ Daily cleanup completed")
        except Exception as e:
            self.logger.error(f"❌ Error in cleanup job: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        try:
            scheduler_status = {
                "running": self.scheduler.running if self.scheduler else False,
                "jobs": [],
                "next_run_times": {}
            }
            
            if self.scheduler:
                for job in self.scheduler.get_jobs():
                    job_info = {
                        "id": job.id,
                        "name": job.name,
                        "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    scheduler_status["jobs"].append(job_info)
                    
                    if job.next_run_time:
                        scheduler_status["next_run_times"][job.id] = job.next_run_time.isoformat()
            
            return {
                "scheduler": scheduler_status,
                "state": state_manager.get_stats(),
                "config": {
                    "enabled": config.SchedulerConfig.enabled,
                    "timezone": config.SchedulerConfig.timezone,
                    "check_times": config.SchedulerConfig.check_times,
                    "max_reminders": config.SchedulerConfig.max_reminders
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting status: {str(e)}")
            return {"error": str(e)}
    
    def trigger_manual_check(self) -> Dict[str, Any]:
        """Trigger manual check (for testing/debugging)"""
        try:
            self.logger.info("🔧 Manual check triggered")
            self.daily_check_job()
            return {"success": True, "message": "Manual check completed"}
        except Exception as e:
            error_msg = f"Error in manual check: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

# Global scheduler service instance
scheduler_service = SchedulerService()
