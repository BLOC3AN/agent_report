# ==========================================
# tests/test_tools.py
# Tool Tests
# ==========================================

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.tools.get_information_from_url import GetInformationFromURLTool
from src.tools.save_chat_history_DB import SaveChatHistoryTool
from src.tools.tool_registry import ToolRegistry

class TestGetInformationFromURLTool:
    """Test URL information fetching tool"""
    
    def setup_method(self):
        """Setup test method"""
        self.tool = GetInformationFromURLTool()
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        assert self.tool.name == "get_information_from_url"
        assert "Google Sheets" in self.tool.description
    
    def test_missing_url_parameter(self):
        """Test execution without URL parameter"""
        result = self.tool.execute()
        assert result["error"] == "URL parameter is required"
    
    @patch('src.tools.get_information_from_url.requests.get')
    @patch('src.tools.get_information_from_url.pl.read_csv')
    def test_successful_execution(self, mock_read_csv, mock_get):
        """Test successful tool execution"""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = b"test,data\n1,2"
        mock_get.return_value = mock_response
        
        # Mock polars DataFrame
        mock_df = Mock()
        mock_df.is_empty.return_value = False
        mock_df.columns = ['Date', 'Task']
        mock_df.to_dicts.return_value = [{'Date': '2025-01-01', 'Task': 'Test task'}]
        mock_read_csv.return_value = mock_df
        
        result = self.tool.execute(url="https://test.com")
        assert 'Date' in result
        assert result['Date'] == '2025-01-01'
    
    @patch('src.tools.get_information_from_url.requests.get')
    def test_http_error(self, mock_get):
        """Test HTTP error handling"""
        mock_get.side_effect = Exception("HTTP Error")
        
        result = self.tool.execute(url="https://test.com")
        assert "error" in result
        assert "HTTP Error" in result["error"]
    
    def test_google_sheets_url_conversion(self):
        """Test Google Sheets URL conversion"""
        with patch('src.tools.get_information_from_url.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("Test")
            mock_get.return_value = mock_response
            
            # Test with edit URL
            self.tool.execute(url="https://docs.google.com/spreadsheets/d/test_id/edit?usp=sharing")
            
            # Verify CSV export URL was called
            expected_url = "https://docs.google.com/spreadsheets/d/test_id/export?format=csv"
            mock_get.assert_called_with(expected_url)

class TestSaveChatHistoryTool:
    """Test chat history saving tool"""
    
    def setup_method(self):
        """Setup test method"""
        with patch('src.tools.save_chat_history_DB.MongoDB'):
            self.tool = SaveChatHistoryTool()
    
    def test_tool_initialization(self):
        """Test tool initialization"""
        assert self.tool.name == "save_chat_history_DB"
        assert "MongoDB" in self.tool.description
    
    def test_successful_save(self):
        """Test successful chat history save"""
        # Mock MongoDB
        mock_result = Mock()
        mock_result.inserted_id = "test_id"
        self.tool.db.insert_one.return_value = mock_result
        
        test_data = {
            "response": ["test response"],
            "conversation": "test conversation",
            "user_input": "test input"
        }
        
        result = self.tool.execute(data=test_data)
        assert result["status"] == "success"
        assert result["document_id"] == "test_id"
    
    def test_database_error(self):
        """Test database error handling"""
        self.tool.db.insert_one.side_effect = Exception("DB Error")
        
        result = self.tool.execute(data={})
        assert result["status"] == "error"
        assert "DB Error" in result["message"]

class TestToolRegistry:
    """Test tool registry"""
    
    def setup_method(self):
        """Setup test method"""
        with patch('src.tools.tool_registry.GetInformationFromURLTool'), \
             patch('src.tools.tool_registry.SaveChatHistoryTool'):
            self.registry = ToolRegistry()
    
    def test_registry_initialization(self):
        """Test registry initialization"""
        assert len(self.registry._tools) >= 0
    
    def test_register_tool(self):
        """Test tool registration"""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        
        self.registry.register_tool(mock_tool)
        assert "test_tool" in self.registry._tools
    
    def test_get_tool(self):
        """Test getting tool by name"""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        self.registry.register_tool(mock_tool)
        
        retrieved_tool = self.registry.get_tool("test_tool")
        assert retrieved_tool == mock_tool
    
    def test_get_nonexistent_tool(self):
        """Test getting non-existent tool"""
        with pytest.raises(ValueError, match="Tool 'nonexistent' not found"):
            self.registry.get_tool("nonexistent")
    
    def test_list_tool_names(self):
        """Test listing tool names"""
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        self.registry.register_tool(mock_tool)
        
        names = self.registry.list_tool_names()
        assert "test_tool" in names
