# ==========================================
# tests/test_agents.py
# Agent Tests
# ==========================================

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.agent_report import AgentReporter
from src.core.interfaces import AgentContext

class TestAgentReporter:
    """Test report agent"""
    
    def setup_method(self):
        """Setup test method"""
        with patch('src.agents.agent_report.GeminiLLM'):
            self.agent = AgentReporter()
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        assert self.agent.name == "ReportAgent"
        assert hasattr(self.agent, 'llm_provider')
        assert hasattr(self.agent, 'tools')
    
    def test_get_system_prompt(self):
        """Test system prompt retrieval"""
        prompt = self.agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @patch('src.agents.base_agent.create_react_agent')
    @patch('src.agents.base_agent.AgentExecutor')
    def test_process_success(self, mock_executor_class, mock_create_agent):
        """Test successful processing"""
        # Mock agent executor
        mock_executor = Mock()
        mock_executor.invoke.return_value = {"output": "Test report generated"}
        mock_executor_class.return_value = mock_executor
        
        # Mock agent creation
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        
        # Test context
        context = AgentContext(
            user_input="Generate a test report",
            conversation_history=[],
            metadata={"task_type": "test"},
            sheet_url="https://test.com"
        )
        
        result = self.agent.process(context)
        
        assert result["success"] == True
        assert "Test report generated" in result["output"]
        assert result["agent"] == "ReportAgent"
    
    @patch('src.agents.base_agent.create_react_agent')
    def test_process_error(self, mock_create_agent):
        """Test error handling in processing"""
        mock_create_agent.side_effect = Exception("Test error")
        
        context = AgentContext(
            user_input="Generate a test report",
            conversation_history=[],
            metadata={"task_type": "test"}
        )
        
        result = self.agent.process(context)
        
        assert result["success"] == False
        assert "Test error" in result["error"]
        assert result["agent"] == "ReportAgent"
    
    def test_generate_report(self):
        """Test report generation method"""
        with patch.object(self.agent, 'process') as mock_process:
            mock_process.return_value = {"success": True, "output": "Test report"}
            
            result = self.agent.generate_report(
                sheet_url="https://test.com",
                additional_context="Test context"
            )
            
            assert result["success"] == True
            mock_process.assert_called_once()
            
            # Check that context was properly constructed
            call_args = mock_process.call_args[0][0]
            assert call_args.sheet_url == "https://test.com"
            assert "Test context" in call_args.user_input
    
    def test_run_legacy_method(self):
        """Test legacy run method"""
        with patch.object(self.agent, 'process') as mock_process:
            mock_process.return_value = {"success": True, "output": "Test output"}
            
            result = self.agent.run(
                user_input="Test input",
                sheet_url="https://test.com"
            )
            
            assert result["success"] == True
            mock_process.assert_called_once()
            
            # Check context construction
            call_args = mock_process.call_args[0][0]
            assert call_args.user_input == "Test input"
            assert call_args.sheet_url == "https://test.com"
    
    def test_add_tool(self):
        """Test adding tool to agent"""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        initial_count = len(self.agent.tools)
        self.agent.add_tool(mock_tool)
        
        assert len(self.agent.tools) == initial_count + 1
        assert mock_tool in self.agent.tools
    
    def test_add_tools(self):
        """Test adding multiple tools"""
        mock_tools = [Mock(), Mock()]
        mock_tools[0].name = "tool1"
        mock_tools[1].name = "tool2"
        
        initial_count = len(self.agent.tools)
        self.agent.add_tools(mock_tools)
        
        assert len(self.agent.tools) == initial_count + 2
        for tool in mock_tools:
            assert tool in self.agent.tools
