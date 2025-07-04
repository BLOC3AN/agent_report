# ==========================================
# tests/test_api.py
# API Tests
# ==========================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from main import app

class TestAPI:
    """Test FastAPI endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        with patch('main.tool_registry') as mock_registry:
            mock_registry.get_all_tools.return_value = [Mock(), Mock()]
            
            response = self.client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "2.0.0"
            assert data["tools_available"] == 2
    
    def test_health_check_error(self):
        """Test health check with error"""
        with patch('main.tool_registry') as mock_registry:
            mock_registry.get_all_tools.side_effect = Exception("Test error")
            
            response = self.client.get("/health")
            assert response.status_code == 500
    
    @patch('main.get_agent')
    def test_generate_report_success(self, mock_get_agent):
        """Test successful report generation"""
        # Mock agent
        mock_agent = Mock()
        mock_agent.generate_report.return_value = {
            "success": True,
            "output": "Test report generated",
            "agent": "ReportAgent",
            "context": {"task_type": "report_generation"}
        }
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "sheet_url": "https://test.com",
            "additional_context": "Test context"
        }
        
        response = self.client.post("/report", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["output"] == "Test report generated"
        assert data["agent"] == "ReportAgent"
    
    @patch('main.get_agent')
    def test_generate_report_failure(self, mock_get_agent):
        """Test report generation failure"""
        # Mock agent with failure
        mock_agent = Mock()
        mock_agent.generate_report.return_value = {
            "success": False,
            "error": "Test error",
            "agent": "ReportAgent"
        }
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "sheet_url": "https://test.com"
        }
        
        response = self.client.post("/report", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert data["error"] == "Test error"
    
    @patch('main.get_agent')
    def test_generate_report_exception(self, mock_get_agent):
        """Test report generation with exception"""
        mock_get_agent.side_effect = Exception("Unexpected error")
        
        request_data = {
            "sheet_url": "https://test.com"
        }
        
        response = self.client.post("/report", json=request_data)
        assert response.status_code == 500
    
    def test_list_tools(self):
        """Test tools listing endpoint"""
        with patch('main.tool_registry') as mock_registry:
            mock_registry.list_tool_names.return_value = ["tool1", "tool2"]
            
            response = self.client.get("/tools")
            
            assert response.status_code == 200
            data = response.json()
            assert data["tools"] == ["tool1", "tool2"]
            assert data["count"] == 2
    
    def test_list_tools_error(self):
        """Test tools listing with error"""
        with patch('main.tool_registry') as mock_registry:
            mock_registry.list_tool_names.side_effect = Exception("Test error")
            
            response = self.client.get("/tools")
            assert response.status_code == 500
    
    @patch('main.get_agent')
    def test_legacy_run_success(self, mock_get_agent):
        """Test legacy run endpoint"""
        mock_agent = Mock()
        mock_agent.run.return_value = {
            "success": True,
            "output": "Legacy output"
        }
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "user_input": "Test input",
            "sheet_url": "https://test.com"
        }
        
        response = self.client.post("/legacy/run", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["output"] == "Legacy output"
    
    def test_legacy_run_missing_input(self):
        """Test legacy run without user input"""
        request_data = {}
        
        response = self.client.post("/legacy/run", json=request_data)
        assert response.status_code == 400
