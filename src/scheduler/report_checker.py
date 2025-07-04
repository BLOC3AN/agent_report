# ==========================================
# src/scheduler/report_checker.py
# Report Content Checker
# ==========================================

import polars as pl
import requests
from datetime import datetime, date
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

class ReportChecker:
    """Checks if daily report content exists in Google Sheets"""
    
    def __init__(self):
        self.logger = Logger("ReportChecker")
    
    def check_today_report(self, sheet_url: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if today's report exists in Google Sheets
        Returns: (report_exists, report_data)
        """
        try:
            self.logger.info(f"🔍 Checking today's report in Google Sheets...")
            
            # Get today's date
            today = date.today()
            today_str = today.strftime("%d/%m/%Y")  # Format: 04/07/2025
            
            self.logger.info(f"📅 Looking for report date: {today_str}")
            
            # Fetch data from Google Sheets
            data = self._fetch_sheet_data(sheet_url)
            if data is None:
                self.logger.warning("⚠️ No data fetched from Google Sheets")
                return False, None
            
            # Check if today's report exists
            report_data = self._find_today_report(data, today_str)
            
            if report_data:
                self.logger.info(f"✅ Found today's report: {today_str}")
                return True, report_data
            else:
                self.logger.info(f"❌ No report found for today: {today_str}")
                return False, None
                
        except Exception as e:
            self.logger.error(f"❌ Error checking today's report: {str(e)}")
            return False, None
    
    def _fetch_sheet_data(self, sheet_url: str) -> Optional[pl.DataFrame]:
        """Fetch data from Google Sheets"""
        try:
            # Convert Google Sheets URL to CSV export URL
            if "docs.google.com/spreadsheets" in sheet_url:
                if "/edit" in sheet_url:
                    sheet_id = sheet_url.split("/d/")[1].split("/edit")[0]
                else:
                    sheet_id = sheet_url.split("/")[-1]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            else:
                csv_url = sheet_url
            
            self.logger.info(f"📥 Fetching data from: {csv_url}")
            
            # Fetch CSV data
            response = requests.get(csv_url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV with polars
            df = pl.read_csv(BytesIO(response.content), encoding="utf8")
            
            if df.is_empty():
                self.logger.warning("⚠️ Empty dataframe from Google Sheets")
                return None
            
            self.logger.info(f"📊 Fetched {len(df)} rows from Google Sheets")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching sheet data: {str(e)}")
            return None
    
    def _find_today_report(self, df: pl.DataFrame, today_str: str) -> Optional[Dict[str, Any]]:
        """Find today's report in the dataframe"""
        try:
            # Check if Date column exists
            if 'Date' not in df.columns:
                self.logger.warning("⚠️ No 'Date' column found in the sheet")
                return None
            
            # Filter for today's date
            today_rows = df.filter(pl.col('Date').str.contains(today_str, literal=True))
            
            if today_rows.is_empty():
                self.logger.info(f"📅 No rows found for date: {today_str}")
                return None
            
            # Get the first matching row
            row_dict = today_rows.to_dicts()[0]
            
            # Check if the row has meaningful content
            if self._has_meaningful_content(row_dict):
                self.logger.info(f"✅ Found meaningful content for {today_str}")
                return row_dict
            else:
                self.logger.info(f"📝 Found date {today_str} but no meaningful content")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error finding today's report: {str(e)}")
            return None
    
    def _has_meaningful_content(self, row_dict: Dict[str, Any]) -> bool:
        """Check if the row has meaningful content beyond just the date"""
        try:
            # Skip the Date column and check other columns
            content_columns = [key for key in row_dict.keys() if key.lower() != 'date']
            
            for column in content_columns:
                value = row_dict.get(column, "")
                str_value = str(value).strip() if value is not None else ""
                if str_value and str_value.lower() not in ['none', 'null', '', 'nan']:
                    # Found non-empty, meaningful content
                    self.logger.info(f"📝 Found content in column '{column}': {str_value[:50]}...")
                    return True
            
            self.logger.info("📝 No meaningful content found in any column")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking meaningful content: {str(e)}")
            return False
    
    def validate_report_completeness(self, report_data: Dict[str, Any]) -> bool:
        """Validate if the report has all required fields"""
        try:
            required_fields = ['Date']
            optional_fields = ['Completed', 'Inprogress', 'In Progress', 'Blocker', 'Blocked']
            
            # Check required fields
            for field in required_fields:
                if field not in report_data or not report_data[field]:
                    self.logger.warning(f"⚠️ Missing required field: {field}")
                    return False
            
            # Check if at least one optional field has content
            has_content = False
            for field in optional_fields:
                if field in report_data and report_data[field]:
                    value = str(report_data[field]).strip()
                    if value and value.lower() not in ['none', 'null', '', 'nan']:
                        has_content = True
                        break
            
            if not has_content:
                self.logger.warning("⚠️ No content found in any progress fields")
                return False
            
            self.logger.info("✅ Report completeness validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating report completeness: {str(e)}")
            return False
    
    def get_report_summary(self, report_data: Dict[str, Any]) -> str:
        """Get a summary of the report for logging"""
        try:
            summary_parts = []
            
            if 'Date' in report_data:
                summary_parts.append(f"Date: {report_data['Date']}")
            
            content_fields = ['Completed', 'Inprogress', 'In Progress', 'Blocker', 'Blocked']
            for field in content_fields:
                if field in report_data and report_data[field]:
                    value = str(report_data[field]).strip()
                    if value and value.lower() not in ['none', 'null', '', 'nan']:
                        # Truncate long content
                        truncated = value[:100] + "..." if len(value) > 100 else value
                        summary_parts.append(f"{field}: {truncated}")
            
            return " | ".join(summary_parts) if summary_parts else "Empty report"
            
        except Exception as e:
            self.logger.error(f"❌ Error creating report summary: {str(e)}")
            return "Error creating summary"

# Test function
if __name__ == "__main__":
    checker = ReportChecker()
    test_url = "https://docs.google.com/spreadsheets/d/19zPaWbW-VuYqhq1ur8vcPoV4EbDKKVDDN84vi4yuOJU/edit?usp=sharing"
    
    exists, data = checker.check_today_report(test_url)
    print(f"Report exists: {exists}")
    if data:
        print(f"Report data: {data}")
        print(f"Summary: {checker.get_report_summary(data)}")
        print(f"Complete: {checker.validate_report_completeness(data)}")
