# ==========================================
# src/config/settings.py
# Centralized Configuration Management
# ==========================================

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    mongodb_uri: str
    mongodb_db_name: str
    mongodb_collection_name: str
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            mongodb_db_name=os.getenv("MONGODB_DB_NAME", "report"),
            mongodb_collection_name=os.getenv("MONGODB_COLLECTION_NAME", "daily_report")
        )

@dataclass
class LLMConfig:
    """LLM configuration settings"""
    model_name: str
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int
    verbose: bool
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        return cls(
            model_name=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("LLM_TOP_P", "0.8")),
            top_k=int(os.getenv("LLM_TOP_K", "40")),
            max_output_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
            verbose=os.getenv("LLM_VERBOSE", "False").lower() == "true"
        )

@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool
    log_level: str
    default_sheet_url: Optional[str]
    api_host: str
    api_port: int
    
    # Sub-configurations
    database: DatabaseConfig
    llm: LLMConfig
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        return cls(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            default_sheet_url=os.getenv("DEFAULT_SHEET_URL"),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "5000")),
            database=DatabaseConfig.from_env(),
            llm=LLMConfig.from_env()
        )

# Global config instance
config = AppConfig.from_env()

# Validation
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not config.database.mongodb_uri:
        errors.append("MONGODB_URI is required")
    
    if not config.llm.model_name:
        errors.append("LLM_MODEL is required")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Auto-validate on import
validate_config()
