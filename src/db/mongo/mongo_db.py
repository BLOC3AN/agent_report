# ==========================================
# src/db/mongo/mongo_db.py
# Refactored MongoDB Integration
# ==========================================

from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from src.core.interfaces import DatabaseInterface
from src.config import config
from src.logs.logger import Logger

logger = Logger(__name__)

class MongoDB(DatabaseInterface):
    """
    Refactored MongoDB operations with proper error handling and configuration
    """

    def __init__(self):
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self._collection: Optional[Collection] = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            self._client = MongoClient(config.database.mongodb_uri)
            self._db = self._client[config.database.mongodb_db_name]
            self._collection = self._db[config.database.mongodb_collection_name]

            # Test connection
            self._client.admin.command('ping')

            # Ensure collection exists
            if self._collection.name not in self._db.list_collection_names():
                logger.info(f"📦 Creating collection: {self._collection.name}")
                self._collection = self._db.create_collection(self._collection.name)
                logger.info(f"✅ Collection {self._collection.name} created successfully")
            else:
                logger.info(f"📦 Collection {self._collection.name} already exists")

        except Exception as e:
            logger.error(f"❌ Failed to initialize MongoDB connection: {str(e)}")
            raise

    @property
    def client(self) -> MongoClient:
        """Get MongoDB client"""
        if self._client is None:
            self._initialize_connection()
        assert self._client is not None, "MongoDB client not initialized"
        return self._client

    @property
    def db(self) -> Database:
        """Get MongoDB database"""
        if self._db is None:
            self._initialize_connection()
        assert self._db is not None, "MongoDB database not initialized"
        return self._db

    @property
    def collection(self) -> Collection:
        """Get MongoDB collection"""
        if self._collection is None:
            self._initialize_connection()
        assert self._collection is not None, "MongoDB collection not initialized"
        return self._collection

    def save_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save conversation to database (implements DatabaseInterface)"""
        try:
            result = self.collection.insert_one(conversation_data)
            logger.info("✅ Conversation saved successfully")
            return {
                "success": True,
                "document_id": str(result.inserted_id),
                "message": "Conversation saved successfully"
            }
        except Exception as e:
            error_msg = f"Error saving conversation: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def get_conversations(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve conversations from database (implements DatabaseInterface)"""
        try:
            cursor = self.collection.find(query)
            conversations = list(cursor)
            logger.info(f"✅ Retrieved {len(conversations)} conversations")
            return conversations
        except Exception as e:
            logger.error(f"❌ Error retrieving conversations: {str(e)}")
            return []

    def get_all_collections(self) -> List[str]:
        """Get all collection names in the database"""
        try:
            return self.db.list_collection_names()
        except Exception as e:
            logger.error(f"❌ Error getting collections: {str(e)}")
            return []

    def insert_one(self, doc: Dict[str, Any]):
        """Insert one document into the collection"""
        try:
            return self.collection.insert_one(doc)
        except Exception as e:
            logger.error(f"❌ Error inserting document: {str(e)}")
            raise

    def find(self, query: Dict[str, Any]):
        """Find documents in the collection"""
        try:
            return self.collection.find(query)
        except Exception as e:
            logger.error(f"❌ Error finding documents: {str(e)}")
            return []

    def delete(self, query: Dict[str, Any]):
        """Delete documents in the collection"""
        try:
            result = self.collection.delete_many(query)
            logger.info(f"✅ Deleted {result.deleted_count} documents")
            return result
        except Exception as e:
            logger.error(f"❌ Error deleting documents: {str(e)}")
            raise

    def close(self):
        """Close the connection to the database"""
        if self._client:
            self._client.close()
            logger.info("📦 MongoDB connection closed")

if __name__ == "__main__":
    mongo = None
    try:
        mongo = MongoDB()
        list_db = mongo.client.list_database_names()
        print(f"Connected to MongoDB. Databases: {list_db}")
        list_collection = mongo.db.list_collection_names()
        print(f"Connected to MongoDB as db [{mongo.db.name}].\nCollections: {list_collection}")
    except Exception as e:
        print("Error:", e)
    finally:
        if mongo:
            mongo.close()