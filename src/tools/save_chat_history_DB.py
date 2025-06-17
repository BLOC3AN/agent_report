import pymongo
from dotenv import load_dotenv
load_dotenv()
from src.logs.logger import Logger
logger = Logger(__name__)

from src.db.mongo.mongo_db import MongoDB
from datetime import datetime
db = MongoDB()

def save_chat_history(data):
    """
    Lưu lịch sử chat vào MongoDB.
    """
    try:
        # Đảm bảo dữ liệu đúng định dạng theo schema
        document = {
            "response": data.get("response", []),
            "timestamp": datetime.now(),
            "conversation": data.get("conversation", ""),
            "user_input": data.get("user_input", "")
        }
        
        result = db.insert_one(document)
        logger.info("Chat history saved successfully.")
        return {"status": "success", "document_id": str(result.inserted_id), "message": "Chat history saved successfully."}
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return {"status": "error", "message": str(e)}
    
