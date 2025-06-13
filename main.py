# mcp_langchain_agent.py (một file mới để nghiên cứu tích hợp MCP)
import os
import requests
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool, tool
from typing import Dict, Any, List
from pydantic import BaseModel, Field
import load_dotenv
load_dotenv.load_dotenv()

# --- Cấu hình cho MCP Service API ---
MCP_SERVICE_API_URL = os.getenv("MCP_SERVICE_API_URL")

class MCPTool(BaseTool):
    """
    Một lớp BaseTool của LangChain đại diện cho một tool được khám phá từ MCP Service.
    """    
    mcp_endpoint: str

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Thực thi tool bằng cách gọi MCP Service API."""
        headers = {"Content-Type": "application/json"}
        full_url = f"{MCP_SERVICE_API_URL}{self.mcp_endpoint}"
        
        try:
            response = requests.post(full_url, json=kwargs, headers=headers)
            response.raise_for_status()
            result = response.json()            
            if result.get("data"):
                return result.get("data")
               
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to call MCP Service endpoint {self.mcp_endpoint}: {e}"}
        except Exception as e:
            return {"error": f"An unexpected error occurred in MCPTool: {e}"}


def discover_and_create_mcp_tools() -> List[BaseTool]:
    """
    Khám phá các tools từ MCP Service và tạo các đối tượng BaseTool của LangChain.
    """
    headers = {"Content-Type": "application/json"}
    capabilities_url = f"{MCP_SERVICE_API_URL}/capabilities"
    
    try:
        response = requests.get(capabilities_url, headers=headers)
        response.raise_for_status()
        capabilities = response.json()[0]["mcp_schema"]
    except requests.exceptions.RequestException as e:
        print(f"Error discovering MCP capabilities: {e}")
        return []

    langchain_tools = []

    tool_name = capabilities["tool_name"]
    description = capabilities["description"]
    endpoint = capabilities["endpoint_url"]
    input_schema = capabilities["input_schema"] 

    mcp_tool_instance = MCPTool(
        name=tool_name,
        description=description,
        args_schema=input_schema, # Truyền JSON Schema vào args_schema
        mcp_endpoint=endpoint
    )
    langchain_tools.append(mcp_tool_instance)
    
    print(f"Discovered {len(langchain_tools)} tools from MCP Service.")
    return langchain_tools

# --- Main Agent Logic ---
if __name__ == "__main__":
    from src.agents.agent_report import AgentReporter
       # Lấy URL từ biến môi trường
    sheet_url = os.getenv('url')
    agent = AgentReporter(url=None)

    # Bước quan trọng: Khám phá tools từ MCP Service API
    mcp_tools = discover_and_create_mcp_tools()
    
    if not mcp_tools:
        print("No tools discovered from MCP Service. Exiting.")
        exit()

    # Sử dụng tools này trong agent
    agent.tools = mcp_tools
    agent.run(input=f"Tạo cho tôi báo cáo đi bạn từ {sheet_url}, lấy thông tin mới nhất theo ngày và chuyển sáng tiếng anh cho tôi")