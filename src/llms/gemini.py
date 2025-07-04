# ==========================================
# src/llms/gemini.py
# Refactored Gemini LLM Provider
# ==========================================

from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.interfaces import LLMInterface
from src.config import settings as config
from src.logs.logger import Logger

logger = Logger(__name__)

class GeminiLLM(LLMInterface):
    """Gemini LLM provider implementation"""

    def __init__(self):
        self._llm = None
        self._name = "Gemini 2.0 Flash"
        self._initialize_llm()
        logger.info(f"✅ {self._name} initialized successfully")

    def _initialize_llm(self):
        """Initialize the Gemini LLM with configuration"""
        try:
            llm = config.LLMConfig.from_env()
            self._llm = ChatGoogleGenerativeAI(
                model=llm.model_name,
                temperature=llm.temperature,
                top_p=llm.top_p,
                top_k=llm.top_k,
                max_tokens=None,
                max_output_tokens=llm.max_output_tokens,
                verbose=llm.verbose,
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini LLM: {str(e)}")
            raise

    def get_llm(self):
        """Get the LLM instance"""
        if self._llm is None:
            self._initialize_llm()
        return self._llm

    @property
    def name(self) -> str:
        """Get the LLM name"""
        return self._name