# ==========================================
# src/tools/get_information_from_url.py
# Refactored URL Data Fetching Tool
# ==========================================

import requests
import polars as pl
from io import BytesIO
from typing import Dict, Any
from src.tools.base_tool import SimpleBaseTool
from src.logs.logger import Logger

logger = Logger(__name__)

class GetInformationFromURLTool(SimpleBaseTool):
    """Tool for fetching data from Google Sheets URLs"""

    def __init__(self):
        super().__init__(
            name="get_information_from_url",
            description="Get data from Google Sheets URL and return the latest entry by date"
        )

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool to fetch data from URL"""
        url = kwargs.get('url')
        if not url:
            return {"error": "URL parameter is required"}

        try:
            self.logger.info(f"Fetching data from: {url}")

            # Convert Google Sheets URL to CSV export URL
            if "docs.google.com/spreadsheets" in url:
                sheet_id = url.split("/")[-2] if "/edit" in url else url.split("/")[-1]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            else:
                csv_url = url

            # Fetch data
            response = requests.get(csv_url)
            response.raise_for_status()

            # Parse CSV and get latest entry
            df = pl.read_csv(BytesIO(response.content), encoding="utf8")

            if df.is_empty():
                return {"error": "No data found in the sheet"}

            # Sort by date and get the latest entry
            if 'Date' in df.columns:
                df_formatted = df.with_columns(
                    pl.col('Date').str.to_datetime().dt.date().alias('date_formatted')
                ).sort(by='date_formatted', descending=True)

                # Get the latest non-empty entry
                for row in df_formatted.iter_rows():
                    if any(cell for cell in row[1:] if cell):  # Skip date column, check if any other field has data
                        latest_entry = df.filter(pl.col('Date') == row[0]).to_dicts()[0]
                        self.logger.info("✅ Latest data entry retrieved successfully")
                        return latest_entry

            # Fallback: return first row if no date column or no valid entries
            latest_entry = df.to_dicts()[0] if not df.is_empty() else {}
            self.logger.info("✅ Data retrieved successfully (fallback)")
            return latest_entry

        except Exception as e:
            error_msg = f"Error fetching data from URL: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg}

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's input schema"""
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The Google Sheets URL to fetch data from"
                }
            },
            "required": ["url"]
        }



# Legacy function for backward compatibility
def get_information_from_url_impl(url: str) -> str:
    """Legacy implementation - returns raw CSV content"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content.decode('utf-8')
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise e

if __name__ == "__main__":
    tool = GetInformationFromURLTool()
    test_url = "https://docs.google.com/spreadsheets/d/19zPaWbW-VuYqhq1ur8vcPoV4EbDKKVDDN84vi4yuOJU/edit?usp=sharing"
    result = tool.execute(url=test_url)
    print(result)