"""
Comprehensive Flask routes for Vision Therapy Application
Handles: Games, Vision Therapy, Eye Detection, User Profiles, Analytics
"""

from flask import Blueprint, request, jsonify
from vision_therapy_db import vision_db
from datetime import datetime

api_routes = Blueprint('api', __name__, url_prefix='/api')

# ==================== GAME SESSIONS ====================

@api_routes.route('/games/save-session', methods=['POST'])
def save_game_session():
    """Save any game session (Ninja, Snake, AmbloCar, etc.)"""
    try:
        data = request.json
        required_fields = ["userId", "gameType", "score", "elapsedTime"]
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": f"Missing fields: {required_fields}"}), 400
        
        result = vision_db.save_game_session(data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/games/user-sessions/<user_id>', methods=['GET'])
def get_game_sessions(user_id):
    """Get all game sessions for a user"""
    try:
        days = request.args.get('days', default=7, type=int)
        sessions = list(vision_db.db["game_sessions"].find(
            {"userId": user_id},
            {"_id": 0}
        ).sort("createdAt", -1).limit(100))
        
        return jsonify({
            "success": True,
            "count": len(sessions),
            "sessions": sessions
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== VISION THERAPY SESSIONS ====================

@api_routes.route('/therapy/save-session', methods=['POST'])
def save_therapy_session():
    """Save vision therapy session"""
    try:
        data = request.json
        required_fields = ["userId", "gameTitle"]
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": f"Missing fields: {required_fields}"}), 400
        
        result = vision_db.save_vision_therapy_session(data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/therapy/user-sessions/<user_id>', methods=['GET'])
def get_therapy_sessions(user_id):
    """Get vision therapy sessions for a user"""
    try:
        days = request.args.get('days', default=7, type=int)
        result = vision_db.get_user_vision_therapy_sessions(user_id, days)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== EYE DETECTION ====================

@api_routes.route('/eye-detection/save', methods=['POST'])
def save_eye_detection():
    """Save eye problem detection result"""
    try:
        data = request.json
        required_fields = ["userId", "result"]  # result: "lazy_eye" or "normal_eye"
        if not all(field in data for field in required_fields):
            return jsonify({"success": False, "message": f"Missing fields: {required_fields}"}), 400
        
        result = vision_db.save_eye_detection_result(data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/eye-detection/latest/<user_id>', methods=['GET'])
def get_latest_eye_detection(user_id):
    """Get latest eye detection result"""
    try:
        result = vision_db.get_latest_eye_detection(user_id)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/eye-detection/history/<user_id>', methods=['GET'])
def get_eye_detection_history(user_id):
    """Get eye detection history"""
    try:
        days = request.args.get('days', default=7, type=int)
        result = vision_db.get_eye_detection_history(user_id, days)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== USER PROFILES ====================

@api_routes.route('/user/profile', methods=['POST'])
def create_update_profile():
    """Create or update user profile"""
    try:
        data = request.json
        if "userId" not in data:
            return jsonify({"success": False, "message": "userId required"}), 400
        
        result = vision_db.create_or_update_user_profile(data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/user/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """Get user profile"""
    try:
        result = vision_db.get_user_profile(user_id)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== LEARNING STATS ====================

@api_routes.route('/stats/learning/<user_id>', methods=['GET'])
def get_learning_stats(user_id):
    """Get learning statistics"""
    try:
        result = vision_db.get_learning_stats(user_id)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_routes.route('/stats/learning', methods=['POST'])
def update_learning_stats():
    """Update learning statistics"""
    try:
        data = request.json
        user_id = data.get("userId")
        if not user_id:
            return jsonify({"success": False, "message": "userId required"}), 400
        
        # Extract shape data
        shape_data = {
            k: v for k, v in data.items() if k != "userId"
        }
        
        result = vision_db.update_learning_stats(user_id, shape_data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== ACTIVITY LOGGING ====================

@api_routes.route('/activity/log', methods=['POST'])
def log_activity():
    """Log user activity"""
    try:
        data = request.json
        result = vision_db.log_activity(data)
        return jsonify(result), 200 if result["success"] else 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== PARENT DASHBOARD ====================

@api_routes.route('/dashboard/report/<user_id>', methods=['GET'])
def get_dashboard_report(user_id):
    """Get comprehensive report for parent dashboard"""
    try:
        days = request.args.get('days', default=7, type=int)
        result = vision_db.get_comprehensive_user_report(user_id, days)
        return jsonify(result), 200 if result["success"] else 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== HEALTH CHECK ====================

@api_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "ok",
            "database": "vision_therapy_db",
            "collections": [
                "game_sessions",
                "vision_therapy_sessions",
                "eye_detection_results",
                "user_profiles",
                "learning_stats",
                "activity_log"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
