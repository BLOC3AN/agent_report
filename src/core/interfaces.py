# ==========================================
# src/core/interfaces.py
# Core interfaces and abstract base classes
# ==========================================

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AgentContext:
    """Context information for agent processing"""
    user_input: str
    conversation_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    sheet_url: Optional[str] = None

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = []
    
    @abstractmethod
    def process(self, context: AgentContext) -> Dict[str, Any]:
        """Process a request with given context"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    def add_tool(self, tool):
        """Add a tool to the agent"""
        self.tools.append(tool)
    
    def add_tools(self, tools: List):
        """Add multiple tools to the agent"""
        self.tools.extend(tools)

class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's input schema"""
        pass

class DatabaseInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    def save_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save conversation to database"""
        pass
    
    @abstractmethod
    def get_conversations(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve conversations from database"""
        pass

class LLMInterface(ABC):
    """Abstract interface for LLM providers"""

    @abstractmethod
    def get_llm(self) -> Any:
        """Get the LLM instance"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the LLM name"""
        pass
