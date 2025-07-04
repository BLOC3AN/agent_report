# ==========================================
# src/logs/logger.py
# Enhanced Logging System
# ==========================================

import logging
import os
from typing import Optional
from src.config import settings as config

class Logger:
    """Enhanced logger with configuration support"""

    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)

        # Set log level from configuration
        log_level = getattr(logging, config.config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers(log_file)

    def _setup_handlers(self, log_file: Optional[str]):
        """Setup console and file handlers"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if config.config.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler
        log_file = log_file or "app.log"

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else "."
        if log_dir != "." and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self, message: str):
        """Log info message with emoji"""
        self.logger.info(f"✅ {message}")

    def error(self, message: str):
        """Log error message with emoji"""
        self.logger.error(f"❌ {message}")

    def debug(self, message: str):
        """Log debug message with emoji"""
        self.logger.debug(f"🔍 {message}")

    def warning(self, message: str):
        """Log warning message with emoji"""
        self.logger.warning(f"⚠️ {message}")

    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"🎉 {message}")

    def critical(self, message: str):
        """Log critical message with emoji"""
        self.logger.critical(f"🚨 {message}")