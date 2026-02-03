"""
Comprehensive MongoDB Integration for Vision Therapy Application
Stores: Game Sessions, Vision Therapy, Eye Detection, Parent Dashboard Data
"""

from pymongo import MongoClient
from datetime import datetime
import os

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://root:<db_password>@e-learning-eye.x9ghjzh.mongodb.net/?appName=E-learning-eye")
DB_NAME = "vision_therapy_db"

# Collections
GAME_SESSIONS = "game_sessions"
VISION_THERAPY = "vision_therapy_sessions"
EYE_DETECTION = "eye_detection_results"
USER_PROFILES = "user_profiles"
LEARNING_STATS = "learning_stats"
ACTIVITY_LOG = "activity_log"

class VisionTherapyDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGO_URI)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            print("✓ Connected to MongoDB Atlas successfully")
            print(f"✓ Database: {DB_NAME}")
            self._ensure_indexes()
        except Exception as e:
            print(f"✗ MongoDB connection failed: {e}")
    
    def _ensure_indexes(self):
        """Create indexes for faster queries"""
        try:
            self.db[GAME_SESSIONS].create_index("userId")
            self.db[VISION_THERAPY].create_index("userId")
            self.db[EYE_DETECTION].create_index("userId")
            self.db[USER_PROFILES].create_index("userId")
            print("✓ Database indexes created")
        except Exception as e:
            print(f"⚠ Index creation warning: {e}")
    
    # ============== GAME SESSIONS ==============
    def save_game_session(self, session_data):
        """Save a game session (Ninja, Snake, AmbloCar, etc.)"""
        try:
            session_data["createdAt"] = datetime.utcnow()
            session_data["updatedAt"] = datetime.utcnow()
            
            result = self.db[GAME_SESSIONS].insert_one(session_data)
            print(f"✓ Game session saved: {result.inserted_id}")
            return {
                "success": True,
                "sessionId": str(result.inserted_id),
                "message": "Game session saved successfully"
            }
        except Exception as e:
            print(f"✗ Error saving game session: {e}")
            return {"success": False, "message": str(e)}
    
    # ============== VISION THERAPY SESSIONS ==============
    def save_vision_therapy_session(self, session_data):
        """Save vision therapy session data"""
        try:
            session_data["createdAt"] = datetime.utcnow()
            session_data["updatedAt"] = datetime.utcnow()
            
            result = self.db[VISION_THERAPY].insert_one(session_data)
            print(f"✓ Vision therapy session saved: {result.inserted_id}")
            return {
                "success": True,
                "sessionId": str(result.inserted_id),
                "message": "Vision therapy session saved"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_user_vision_therapy_sessions(self, user_id, days=7):
        """Get vision therapy sessions for a user (last N days)"""
        try:
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(days=days)
            
            sessions = list(self.db[VISION_THERAPY].find(
                {
                    "userId": user_id,
                    "createdAt": {"$gte": since}
                }
            ).sort("createdAt", -1))
            
            return {
                "success": True,
                "sessions": sessions,
                "count": len(sessions),
                "period_days": days
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ============== EYE DETECTION RESULTS ==============
    def save_eye_detection_result(self, detection_data):
        """Save eye problem detection results"""
        try:
            detection_data["createdAt"] = datetime.utcnow()
            detection_data["timestamp"] = datetime.utcnow()
            
            result = self.db[EYE_DETECTION].insert_one(detection_data)
            print(f"✓ Eye detection result saved: {result.inserted_id}")
            return {
                "success": True,
                "detectionId": str(result.inserted_id),
                "message": "Eye detection saved"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_latest_eye_detection(self, user_id):
        """Get the latest eye detection result"""
        try:
            result = self.db[EYE_DETECTION].find_one(
                {"userId": user_id},
                sort=[("createdAt", -1)]
            )
            return {
                "success": True,
                "result": result,
                "message": "Latest detection retrieved"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_eye_detection_history(self, user_id, days=7):
        """Get eye detection history"""
        try:
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(days=days)
            
            results = list(self.db[EYE_DETECTION].find(
                {
                    "userId": user_id,
                    "createdAt": {"$gte": since}
                }
            ).sort("createdAt", -1))
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "period_days": days
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ============== USER PROFILES ==============
    def create_or_update_user_profile(self, user_data):
        """Create or update user profile"""
        try:
            user_id = user_data.get("userId")
            user_data["updatedAt"] = datetime.utcnow()
            
            result = self.db[USER_PROFILES].update_one(
                {"userId": user_id},
                {"$set": user_data},
                upsert=True
            )
            return {
                "success": True,
                "message": "User profile saved",
                "isNew": result.upserted_id is not None
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        try:
            profile = self.db[USER_PROFILES].find_one({"userId": user_id})
            return {
                "success": True,
                "profile": profile,
                "message": "User profile retrieved"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ============== LEARNING STATS ==============
    def update_learning_stats(self, user_id, shape_data):
        """Update learning statistics for shapes"""
        try:
            self.db[LEARNING_STATS].update_one(
                {"userId": user_id},
                {
                    "$set": {
                        "userId": user_id,
                        "updatedAt": datetime.utcnow(),
                        **shape_data
                    }
                },
                upsert=True
            )
            return {"success": True, "message": "Learning stats updated"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_learning_stats(self, user_id):
        """Get learning statistics"""
        try:
            stats = self.db[LEARNING_STATS].find_one({"userId": user_id})
            return {
                "success": True,
                "stats": stats,
                "message": "Learning stats retrieved"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ============== ACTIVITY LOG ==============
    def log_activity(self, activity_data):
        """Log user activity"""
        try:
            activity_data["createdAt"] = datetime.utcnow()
            self.db[ACTIVITY_LOG].insert_one(activity_data)
            return {"success": True, "message": "Activity logged"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # ============== DASHBOARD ANALYTICS ==============
    def get_comprehensive_user_report(self, user_id, days=7):
        """Get comprehensive report for parent dashboard"""
        try:
            from datetime import timedelta
            since = datetime.utcnow() - timedelta(days=days)
            
            # Get all data for the user
            game_sessions = list(self.db[GAME_SESSIONS].find(
                {"userId": user_id, "createdAt": {"$gte": since}}
            ))
            
            vision_sessions = list(self.db[VISION_THERAPY].find(
                {"userId": user_id, "createdAt": {"$gte": since}}
            ))
            
            eye_detections = list(self.db[EYE_DETECTION].find(
                {"userId": user_id, "createdAt": {"$gte": since}}
            ))
            
            user_profile = self.db[USER_PROFILES].find_one({"userId": user_id})
            learning_stats = self.db[LEARNING_STATS].find_one({"userId": user_id})
            
            # Calculate metrics
            total_game_score = sum(g.get("score", 0) for g in game_sessions)
            avg_game_score = total_game_score / len(game_sessions) if game_sessions else 0
            total_gaming_time = sum(g.get("elapsedTime", 0) for g in game_sessions)
            
            total_therapy_time = sum(v.get("duration", 0) for v in vision_sessions)
            
            # Eye detection stats
            lazy_eye_detections = [e for e in eye_detections if e.get("result") == "lazy_eye"]
            normal_eye_count = len(eye_detections) - len(lazy_eye_detections)
            
            return {
                "success": True,
                "userId": user_id,
                "period_days": days,
                "gameMetrics": {
                    "totalSessions": len(game_sessions),
                    "totalScore": total_game_score,
                    "averageScore": round(avg_game_score, 2),
                    "totalTime": total_gaming_time,
                    "gameBreakdown": self._breakdown_games(game_sessions)
                },
                "visionTherapyMetrics": {
                    "totalSessions": len(vision_sessions),
                    "totalTime": total_therapy_time,
                    "gamesPlayed": self._get_unique_games(vision_sessions)
                },
                "eyeDetectionMetrics": {
                    "totalDetections": len(eye_detections),
                    "lazyEyeCount": len(lazy_eye_detections),
                    "normalEyeCount": normal_eye_count,
                    "lazyEyePercentage": round((len(lazy_eye_detections) / len(eye_detections) * 100) if eye_detections else 0, 2)
                },
                "userProfile": user_profile,
                "learningStats": learning_stats,
                "reportGeneratedAt": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def _breakdown_games(self, game_sessions):
        """Helper to breakdown games by type"""
        breakdown = {}
        for session in game_sessions:
            game_type = session.get("gameType", "unknown")
            if game_type not in breakdown:
                breakdown[game_type] = {"count": 0, "totalScore": 0}
            breakdown[game_type]["count"] += 1
            breakdown[game_type]["totalScore"] += session.get("score", 0)
        return breakdown
    
    def _get_unique_games(self, vision_sessions):
        """Helper to get unique games played"""
        games = set()
        for session in vision_sessions:
            game = session.get("gameTitle")
            if game:
                games.add(game)
        return list(games)
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

# Global instance
vision_db = VisionTherapyDB()
