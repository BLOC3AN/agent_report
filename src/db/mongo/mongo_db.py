import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
class MongoDB:
    """
    A class to handle MongoDB operations.
    """
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[str(os.getenv("MONGODB_DB_NAME"))]
        self.collection = self.db[str(os.getenv("MONGODB_COLLECTION_NAME"))]

    def insert_one(self, doc):
        """Insert one document into the collection."""
        return self.collection.insert_one(doc)
    
    def find(self, query):
        """Find documents in the collection."""
        return self.collection.find(query)
    
    def delete(self, query):
        """Delete documents in the collection."""
        self.collection.delete_many(query)
    
    def close(self):
        """Close the connection to the database."""
        self.client.close()

if __name__ == "__main__":
    try:
        mongo = MongoDB()
        print(mongo.collection.find_one({"session_id":"demo-session-001"}))
    except Exception as e:
        print("Error:", e)
    finally:
        mongo.close() # type: ignore