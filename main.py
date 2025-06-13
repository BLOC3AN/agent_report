# ==========================================
# main.py (root directory)
# ==========================================
from src.agents.agent_report import AgentReporter
import os
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI()

def run_agent_with_custom_url(custom_url=None):
    """Running agent by url customized or gotten from .env"""
    url = custom_url or os.getenv("url")
    if not url:
        print("Error: No URL provided")
        return None
    agent = AgentReporter(url)
    return agent.run()

@app.get("/report")
async def get_report():
    result = run_agent_with_custom_url()
    return {"report": result}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    # URL from .env
    print("=== Running with URL from .env ===")
    result = run_agent_with_custom_url()
    print("\n \nLength of result:", len(str(result)))
    return result

if __name__ == "__main__":
    main()
