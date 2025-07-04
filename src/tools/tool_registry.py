# ==========================================
# src/tools/tool_registry.py
# Simple Tool Registry System
# ==========================================

from typing import Dict, List
from src.tools.get_information_from_url import GetInformationFromURLTool
from src.tools.save_chat_history_DB import SaveChatHistoryTool
from src.logs.logger import Logger

logger = Logger(__name__)

class ToolRegistry:
    """Simple registry for managing tools"""
    
    def __init__(self):
        self._tools: Dict[str, object] = {}
        self._initialize_default_tools()
        logger.info("🔧 Tool Registry initialized")
    
    def _initialize_default_tools(self):
        """Initialize default tools"""
        default_tools = [
            GetInformationFromURLTool(),
            SaveChatHistoryTool()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool) -> None:
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.info(f"✅ Tool '{tool.name}' registered")
    
    def get_tool(self, name: str):
        """Get a tool by name"""
        if name in self._tools:
            return self._tools[name]
        else:
            raise ValueError(f"Tool '{name}' not found in registry")
    
    def get_all_tools(self) -> List:
        """Get all registered tools"""
        return list(self._tools.values())
    
    def get_langchain_tools(self) -> List:
        """Get all tools as LangChain compatible tools"""
        langchain_tools = []
        for tool in self._tools.values():
            if hasattr(tool, 'to_langchain_tool'):
                langchain_tools.append(tool.to_langchain_tool())
            else:
                logger.warning(f"⚠️ Tool '{tool.name}' is not LangChain compatible")
        
        logger.info(f"🔧 {len(langchain_tools)} LangChain tools available")
        return langchain_tools
    
    def list_tool_names(self) -> List[str]:
        """List all available tool names"""
        return list(self._tools.keys())
    
    def remove_tool(self, name: str) -> None:
        """Remove a tool from registry"""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"🗑️ Tool '{name}' removed from registry")
        else:
            logger.warning(f"⚠️ Tool '{name}' not found for removal")

# Global tool registry instance
tool_registry = ToolRegistry()
