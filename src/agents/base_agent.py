# ==========================================
# src/agents/base_agent.py
# Base Agent Implementation
# ==========================================

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor

from src.core.interfaces import BaseAgent, AgentContext, LLMInterface
from src.config import config
from src.logs.logger import Logger

logger = Logger(__name__)

class LangChainBaseAgent(BaseAgent):
    """Base implementation using LangChain framework"""
    
    def __init__(self, name: str, llm_provider: LLMInterface, prompt_file_path: str):
        super().__init__(name)
        self.llm_provider = llm_provider
        self.prompt_file_path = prompt_file_path
        self.system_prompt = self._load_prompt()
        self.prompt_template = self._create_prompt_template()
        
        logger.info(f"✅ {name} agent initialized successfully")
    
    def _load_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            with open(self.prompt_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logger.info(f"📑 System prompt loaded from {self.prompt_file_path}")
                return content
        except FileNotFoundError:
            logger.warning(f"⚠️ Prompt file not found at {self.prompt_file_path}")
            return self._get_default_prompt()
        except Exception as e:
            logger.error(f"❌ Error reading prompt file: {str(e)}")
            return self._get_default_prompt()
    
    def _get_default_prompt(self) -> str:
        """Get default prompt if file loading fails"""
        return "You are a helpful AI assistant."
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create the prompt template for the agent"""
        react_prompt = """You are a specialized AI agent that MUST use tools to complete tasks.

{system_prompt}

CRITICAL: You CANNOT complete tasks without using the available tools. Always start by using tools to gather data.

TOOLS:
------
You have access to the following tools:

{tools}

MANDATORY TOOL USAGE FORMAT:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

Continue using tools until you have completed all required steps. Only when ALL tools have been used and the task is complete, use:

```
Thought: Do I need to use a tool? No
Final Answer: [your complete response here]
```

REMEMBER: You MUST use tools first. Do not attempt to answer without using the available tools.

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        return ChatPromptTemplate.from_template(react_prompt)
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor"""
        try:
            # Import here to avoid circular imports
            from langchain.agents import create_react_agent

            agent = create_react_agent(
                self.llm_provider.get_llm(),
                tools=self.tools,
                prompt=self.prompt_template
            )
            agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                handle_parsing_errors=True,
                verbose=config.debug,
                max_iterations=15,  # Tăng số iterations
                max_execution_time=300,  # 5 phút timeout
                early_stopping_method="force",  # Cho phép generate output ngay cả khi chưa hoàn thành
                return_intermediate_steps=True  # Trả về intermediate steps để debug
            )
            logger.info(f"🤖 Agent executor created for {self.name} with {len(self.tools)} tools")
            return agent_executor
        except Exception as e:
            logger.error(f"❌ Error creating agent executor: {str(e)}")
            raise
    
    def process(self, context: AgentContext) -> Dict[str, Any]:
        """Process a request with given context"""
        try:
            agent_executor = self._create_agent_executor()

            # Prepare input with context
            user_input = context.user_input

            # Add sheet URL to input if provided
            if context.sheet_url:
                user_input = f"{context.user_input}\nSheet URL: {context.sheet_url}"

            # Prepare agent input with all required variables
            agent_input = {
                "input": user_input,
                "system_prompt": self.system_prompt,
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
                "agent_scratchpad": ""
            }

            result = agent_executor.invoke(agent_input)

            logger.info(f"✅ {self.name} processed request successfully")
            return {
                "success": True,
                "output": result.get("output", ""),
                "agent": self.name,
                "context": context.metadata
            }
        except Exception as e:
            logger.error(f"❌ Error in {self.name} execution: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return self.system_prompt
