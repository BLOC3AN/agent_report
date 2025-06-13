# ==========================================
# src/agents/agent_report.py
# ==========================================

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from src.tools.get_data_ggSheet import get_information_from_url
import load_dotenv

load_dotenv.load_dotenv()

class AgentReporter:
    def __init__(self, url):
        self.url = url
        self.prompt_file_path = "src/prompt/agent_report.md"
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", 
                                          temperature=0,
                                          top_p=0.2,
                                          top_k=40,
                                          max_tokens=None,
                                          max_output_tokens=150,
                                          verbose = True,
                                          )
        
        # Tool binding được thực hiện ngay trong __init__
        self.tools = [get_information_from_url]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # System message
        self.system_prompt = self.read_prompt_from_md(self.prompt_file_path)
        self.system_message = SystemMessage(content=self.system_prompt)
        
        # Message history
        self.messages = [self.system_message]
    
    def read_prompt_from_md(self, file_path) -> str:
        """Loading prompt as file Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {file_path}")
            return "You are a helpful assistant that can analyze data and create reports."
    
    def run(self):
        """Chạy agent với proper message flow"""
        try:
            # Bước 1: Tạo human message
            human_message = HumanMessage(
                content=f"Sử dụng tool get_information_from_url để lấy thông tin từ URL: {self.url} và viết báo cáo tiếng anh"
            )
            self.messages.append(human_message)
            
            print("=== Starting Agent Reporter ===")
            print(f"URL: {self.url}")
            
            # Bước 2: Gọi LLM lần đầu
            ai_response = self.llm_with_tools.invoke(self.messages)
            self.messages.append(ai_response)
            
            print(f"AI Response: {ai_response.content}")
            print(f"Tool calls: {len(ai_response.tool_calls) if ai_response.tool_calls else 0}")
            
            # Bước 3: Xử lý tool calls
            if ai_response.tool_calls:
                for tool_call in ai_response.tool_calls:
                    print(f"\n=== Executing Tool: {tool_call['name']} ===")
                    
                    try:
                        # Thực thi tool
                        tool_result = get_information_from_url(tool_call["args"]["url"])
                        
                        # Tạo tool message
                        tool_message = ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"],
                            name=tool_call["name"]
                        )
                        self.messages.append(tool_message)
                        
                        print(f"Tool executed successfully. Data length: {len(str(tool_result))}")
                        
                    except Exception as e:
                        print(f"Error executing tool: {str(e)}")
                        error_message = ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call["id"],
                            name=tool_call["name"]
                        )
                        self.messages.append(error_message)
                
                # Bước 4: Gọi LLM với kết quả tool
                print("\n=== Generating Final Report ===")
                final_response = self.llm_with_tools.invoke(self.messages)
                self.messages.append(final_response)
                
                print("\n=== FINAL REPORT ===\n")
                print(final_response.content)
                return final_response.content
                
            else:
                print("No tools were called. Direct response:")
                print(ai_response.content)
                return ai_response.content
                
        except Exception as e:
            print(f"Error in agent execution: {str(e)}")
            return None
    
    def get_conversation_history(self):
        """Trả về lịch sử conversation"""
        return self.messages
    
    def reset_conversation(self):
        """Reset conversation về trạng thái ban đầu"""
        self.messages = [self.system_message]
        print("Conversation reset.")
