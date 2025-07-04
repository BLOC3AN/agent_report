# ==========================================
# tests/test_config.py
# Configuration Tests
# ==========================================

import pytest
import os
from unittest.mock import patch
from src.config.settings import DatabaseConfig, LLMConfig, AppConfig

class TestDatabaseConfig:
    """Test database configuration"""
    
    def test_default_values(self):
        """Test default configuration values"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig.from_env()
            assert config.mongodb_uri == "mongodb://localhost:27017"
            assert config.mongodb_db_name == "report"
            assert config.mongodb_collection_name == "daily_report"
    
    def test_env_override(self):
        """Test environment variable override"""
        env_vars = {
            "MONGODB_URI": "mongodb://test:27017",
            "MONGODB_DB_NAME": "test_db",
            "MONGODB_COLLECTION_NAME": "test_collection"
        }
        with patch.dict(os.environ, env_vars):
            config = DatabaseConfig.from_env()
            assert config.mongodb_uri == "mongodb://test:27017"
            assert config.mongodb_db_name == "test_db"
            assert config.mongodb_collection_name == "test_collection"

class TestLLMConfig:
    """Test LLM configuration"""
    
    def test_default_values(self):
        """Test default LLM configuration"""
        with patch.dict(os.environ, {}, clear=True):
            config = LLMConfig.from_env()
            assert config.model_name == "gemini-2.0-flash"
            assert config.temperature == 0.7
            assert config.top_p == 0.8
            assert config.top_k == 40
            assert config.max_output_tokens == 2048
            assert config.verbose == False
    
    def test_env_override(self):
        """Test environment variable override for LLM"""
        env_vars = {
            "LLM_MODEL": "test-model",
            "LLM_TEMPERATURE": "0.5",
            "LLM_TOP_P": "0.9",
            "LLM_TOP_K": "50",
            "LLM_MAX_TOKENS": "1024",
            "LLM_VERBOSE": "true"
        }
        with patch.dict(os.environ, env_vars):
            config = LLMConfig.from_env()
            assert config.model_name == "test-model"
            assert config.temperature == 0.5
            assert config.top_p == 0.9
            assert config.top_k == 50
            assert config.max_output_tokens == 1024
            assert config.verbose == True

class TestAppConfig:
    """Test application configuration"""
    
    def test_default_values(self):
        """Test default app configuration"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()
            assert config.debug == False
            assert config.log_level == "INFO"
            assert config.default_sheet_url is None
            assert config.api_host == "0.0.0.0"
            assert config.api_port == 5000
    
    def test_nested_configs(self):
        """Test nested configuration objects"""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()
            assert isinstance(config.database, DatabaseConfig)
            assert isinstance(config.llm, LLMConfig)
    
    def test_debug_mode(self):
        """Test debug mode configuration"""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            config = AppConfig.from_env()
            assert config.debug == True
        
        with patch.dict(os.environ, {"DEBUG": "false"}):
            config = AppConfig.from_env()
            assert config.debug == False
