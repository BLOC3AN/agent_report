import polars as pl
import requests
from io import BytesIO
from typing import Dict, Any, Optional
from langchain_core.tools import tool

@tool(description="get_information_from_url")
def get_information_from_url(url: str) -> Dict[str, Any]: #type:ignore
    """
    Lấy dữ liệu báo cáo hàng ngày từ Google Sheet bằng URL
    """
    # Tải dữ liệu dưới dạng bytes
    sheet_id = url.split("/")[-2]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

    response = requests.get(csv_url)
    response.raise_for_status()

    # Đọc CSV với encoding UTF-8
    try:
        df = pl.read_csv(BytesIO(response.content), encoding="utf8")
        df_formated = df.with_columns(pl.col('Date').str.to_datetime().dt.date().alias('date_formated')).sort(by='date_formated',descending=True) # type: ignore
        for content in df_formated.iter_rows():
            if content[1]:
                return df.filter(pl.col('Date')==content[0]).to_struct()[0]
            else: return {"error from sheet": "No data"}
    except Exception as e:
        print("Error:", e)
        return {"Error as get_data_ggSheet tool: ": str(e)}
