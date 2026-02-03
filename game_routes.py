"""
Flask routes for game session management
Add this to your main Flask app
"""

from flask import Blueprint, request, jsonify
from game_session_db import game_db
from datetime import datetime

game_routes = Blueprint('game', __name__, url_prefix='/api/game')

@game_routes.route('/save-session', methods=['POST'])
def save_game_session():
    """
    Save a game session to MongoDB
    
    Expected JSON:
    {
        "userId": "user123",
        "score": 10,
        "targetShape": "circle",
        "elapsedTime": 120,
        "misses": 2,
        "gameType": "ninja_game"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ["userId", "score", "targetShape", "elapsedTime", "misses"]
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {required_fields}"
            }), 400
        
        result = game_db.save_game_session(data)
        return jsonify(result), 200 if result["success"] else 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@game_routes.route('/user-sessions/<user_id>', methods=['GET'])
def get_user_sessions(user_id):
    """Get all game sessions for a specific user"""
    result = game_db.get_user_sessions(user_id)
    return jsonify(result), 200 if result["success"] else 404

@game_routes.route('/user-stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get statistics for a user's game sessions"""
    result = game_db.get_session_stats(user_id)
    return jsonify(result), 200 if result["success"] else 404

@game_routes.route('/health', methods=['GET'])
def health_check():
    """Check if MongoDB is connected"""
    return jsonify({
        "status": "ok" if game_db.collection else "error",
        "database": "vision_therapy_db",
        "collection": "game_sessions"
    }), 200
