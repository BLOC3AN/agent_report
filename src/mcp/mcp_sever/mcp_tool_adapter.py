from fastapi import FastAPI, HTTPException, Request, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
import sys
import os
# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from src.tools.get_information_from_url import get_information_from_url_impl
import load_dotenv
load_dotenv.load_dotenv()
from src.logs.logger import Logger
logger = Logger(__name__)

app = FastAPI(
    title="MCP Research Tool Service",
    description="An API Gateway mimicking MCP for research purposes.",
    version="0.1.0"
)

# --- Định nghĩa Schema cho các Tool theo cấu trúc tương tự MCP ---
class ToolMetadata(BaseModel):
    mcp_schema:Dict
class GetInfoFromURLRequest(BaseModel):
    url: str
class ToolInvocationResponse(BaseModel):
    data: Any
    Date: Optional[str] = None
    Inprogress: Optional[str] = None
    Blocker: Optional[str] = None
    Completed: Optional[str] = None
    status: Optional[str] = "success"  # Thêm trường status mặc định là "success"
    message: Optional[str] = None  # Thêm trường message để truyền thông báo lỗi hoặc thông tin

# --- Service Discovery Endpoint ---
@app.get("/capabilities", 
         response_model=List[ToolMetadata],
         summary="Khám phá các khả năng (tools) có sẵn theo định dạng MCP.",
         dependencies=[])

async def get_capabilities():
    with open ("src/mcp/mcp_schema/schema.json", "r") as f:
        schema = json.load(f)
    logger.info("Providing list of available tools (capabilities).")
    return [ToolMetadata(mcp_schema=schema)]

# --- Endpoint để gọi Tool ---
# VÀ ĐÂY CHÍNH LÀ ĐIỂM QUAN TRỌNG: KHI AGENT TRỎ TỚI ĐỊA CHỈ TOOL, ĐÓ SẼ LÀ POST
@app.post("/tools/get_information_from_url", 
          response_model=ToolInvocationResponse,
          summary="Thực thi tool 'get_information_from_url'để truy cập vào Google Sheet và lấy thông tin",
          dependencies=[])

async def invoke_get_information_from_url(request_body: GetInfoFromURLRequest):
    logger.info(f"Received invocation request for get_information_from_url with URL: {request_body.url}")
    try:
        result = get_information_from_url_impl(request_body.url) # Gọi hàm core logic của tool
        logger.info(f"Successfully invoked get_information_from_url for URL: {request_body.url}")
        return ToolInvocationResponse(data = result) # Chuyển đổi kết quả về dạng Pydantic model
    except Exception as e:
        logger.error(f"Error invoking get_information_from_url: {str(e)}")
        return ToolInvocationResponse(status="error", message=str(e), data = None)

# --- Main execution ---
if __name__ == "__main__":
    import uvicorn
    # Đảm bảo biến môi trường MCP_SERVICE_API_KEY đã được đặt trước khi chạy
    uvicorn.run(app, host="0.0.0.0", port=8001)
