from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

import load_dotenv
load_dotenv.load_dotenv()

from src.logs.logger import Logger
logger = Logger(__name__)

class AgentGemini:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", 
                                          temperature=0.9,
                                          top_p=0.2,
                                          top_k=40,
                                          max_tokens=None,
                                          max_output_tokens=150,
                                          verbose = True,
                                          )
    def agent_gemini(self, tools:list, prompt:ChatPromptTemplate, input:str) -> dict:
        try:
            # Bước 1: Create agent executor from llm model
            agent = create_tool_calling_agent(self.llm, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose = True)
            logger.info("✅ Gemini Agent created successfully")

            # Bước 2: Gọi agent executor
            result = agent_executor.invoke({"input": f"{input}"})
            logger.info(f"📜 Resonsed keys from Gemini Agent \n{result.keys()}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in create Gemini Agent execution: {str(e)}")
            return {"Error as agent_gemini": str(e)}

