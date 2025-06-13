# ==========================================
# src/agents/agent_report.py
# ==========================================
from langchain_core.prompts import ChatPromptTemplate
from src.tools.get_data_ggSheet import get_information_from_url
from src.llms.gemini import AgentGemini 

import load_dotenv
load_dotenv.load_dotenv()

from src.logs.logger import Logger
logger = Logger(__name__)

class AgentReporter:
    def __init__(self, url):
        self.url = url
        self.prompt_file_path = "src/prompt/agent_report.md"
        self.agent = AgentGemini() 
        self.tools = [get_information_from_url]
        # System message
        self.system_prompt = self.read_prompt_from_md(self.prompt_file_path)   
        logger.info("📑 System prompt loaded.")     
        # Message history
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", f"{self.system_prompt}"),
            ("human", "{input}"),
            ("placeholder", "{conversation}"),
            ("placeholder", "{agent_scratchpad}"),])

    def read_prompt_from_md(self, file_path) -> str:
        """Loading prompt as file Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            logger.warning(f"Warning: Prompt file not found at {file_path}")
            return "You are a helpful assistant that can analyze data and create reports."
    
    def run(self):
        """Chạy agent với proper message flow"""
        try:
            result = self.agent.agent_gemini(self.tools, self.prompt, self.url)
            logger.info(f"Result from agent:\n{result['output']}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in agent execution: {str(e)}")
            return None     
