"""
MongoDB Integration for storing game session data
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB Connection
# Replace <db_password> with your actual MongoDB password in .env file
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://root:<db_password>@e-learning-eye.x9ghjzh.mongodb.net/?appName=E-learning-eye")
DB_NAME = "vision_therapy_db"
COLLECTION_NAME = "game_sessions"

class GameSessionDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGO_URI)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✓ Connected to MongoDB Atlas successfully")
            print(f"✓ Database: {DB_NAME}")
            print(f"✓ Collection: {COLLECTION_NAME}")
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
            print("⚠ Make sure to replace <db_password> in .env file with your actual password")
    
    def save_game_session(self, session_data):
        """
        Save a game session to MongoDB
        
        session_data should contain:
        {
            "userId": "user123",
            "score": 10,
            "targetShape": "circle",
            "elapsedTime": 120,
            "misses": 2,
            "sessionStartTime": datetime,
            "gameType": "ninja_game"
        }
        """
        try:
            session_data["createdAt"] = datetime.utcnow()
            session_data["updatedAt"] = datetime.utcnow()
            
            result = self.collection.insert_one(session_data)
            print(f"✓ Game session saved with ID: {result.inserted_id}")
            return {
                "success": True,
                "sessionId": str(result.inserted_id),
                "message": "Game session saved successfully"
            }
        except Exception as e:
            print(f"✗ Error saving game session: {e}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_user_sessions(self, user_id):
        """Get all game sessions for a user"""
        try:
            sessions = list(self.collection.find(
                {"userId": user_id},
                {"_id": 0}
            ).sort("createdAt", -1))
            return {
                "success": True,
                "sessions": sessions,
                "count": len(sessions)
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_session_stats(self, user_id):
        """Get statistics for a user's game sessions"""
        try:
            sessions = list(self.collection.find({"userId": user_id}))
            if not sessions:
                return {
                    "success": False,
                    "message": "No sessions found for this user"
                }
            
            total_score = sum(s.get("score", 0) for s in sessions)
            avg_score = total_score / len(sessions)
            total_time = sum(s.get("elapsedTime", 0) for s in sessions)
            total_misses = sum(s.get("misses", 0) for s in sessions)
            
            return {
                "success": True,
                "totalSessions": len(sessions),
                "totalScore": total_score,
                "averageScore": round(avg_score, 2),
                "totalTimeSpent": total_time,
                "totalMisses": total_misses,
                "averageMisses": round(total_misses / len(sessions), 2)
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

# Global instance
game_db = GameSessionDB()
