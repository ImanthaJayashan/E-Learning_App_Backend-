from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
import csv

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Data storage paths
DATA_DIR = 'game_analytics'
LOGS_FILE = os.path.join(DATA_DIR, 'game_logs.json')
CSV_FILE = os.path.join(DATA_DIR, 'game_analytics.csv')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'session_id', 'timestamp', 'animal_shown', 'animal_selected',
            'is_correct', 'response_time_ms', 'attempt_number', 
            'total_score', 'game_duration_sec'
        ])


@app.route('/api/log-interaction', methods=['POST'])
def log_interaction():
    """
    Log each user interaction with the game
    Expected payload:
    {
        "session_id": "unique_session_identifier",
        "animal_shown": "dog",
        "animal_selected": "cat",
        "is_correct": false,
        "response_time_ms": 1523,
        "attempt_number": 2,
        "total_score": 5,
        "game_duration_sec": 45.3
    }
    """
    try:
        data = request.get_json()
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Validate required fields
        required_fields = [
            'session_id', 'animal_shown', 'animal_selected', 
            'is_correct', 'response_time_ms', 'attempt_number'
        ]
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Save to JSON log file (append)
        logs = []
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r') as f:
                logs = json.load(f)
        
        logs.append(data)
        
        with open(LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
        
        # Save to CSV for easy ML analysis
        with open(CSV_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                data['session_id'],
                data['timestamp'],
                data['animal_shown'],
                data['animal_selected'],
                data['is_correct'],
                data['response_time_ms'],
                data['attempt_number'],
                data.get('total_score', 0),
                data.get('game_duration_sec', 0)
            ])
        
        return jsonify({
            'status': 'success',
            'message': 'Interaction logged successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session-summary', methods=['POST'])
def session_summary():
    """
    Log complete session summary
    Expected payload:
    {
        "session_id": "unique_session_identifier",
        "total_attempts": 10,
        "correct_attempts": 7,
        "incorrect_attempts": 3,
        "final_score": 7,
        "total_duration_sec": 120.5,
        "average_response_time_ms": 1850,
        "animals_played": ["dog", "cat", "cow", "lion"]
    }
    """
    try:
        data = request.get_json()
        data['timestamp'] = datetime.now().isoformat()
        data['type'] = 'session_summary'
        
        # Save to JSON log file
        logs = []
        if os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'r') as f:
                logs = json.load(f)
        
        logs.append(data)
        
        with open(LOGS_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': 'Session summary logged successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """
    Retrieve analytics data for ML processing
    Query parameters:
    - session_id: Filter by specific session (optional)
    - start_date: Filter from date (optional)
    - end_date: Filter to date (optional)
    """
    try:
        if not os.path.exists(LOGS_FILE):
            return jsonify({'data': []}), 200
        
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        
        # Apply filters if provided
        session_id = request.args.get('session_id')
        if session_id:
            logs = [log for log in logs if log.get('session_id') == session_id]
        
        return jsonify({'data': logs, 'count': len(logs)}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """
    Get aggregated statistics across all sessions
    """
    try:
        if not os.path.exists(LOGS_FILE):
            return jsonify({'error': 'No data available'}), 404
        
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
        
        # Filter only interaction logs (not summaries)
        interactions = [log for log in logs if log.get('type') != 'session_summary']
        
        if not interactions:
            return jsonify({'error': 'No interaction data available'}), 404
        
        # Calculate statistics
        total_interactions = len(interactions)
        correct_count = sum(1 for log in interactions if log.get('is_correct'))
        incorrect_count = total_interactions - correct_count
        
        response_times = [log['response_time_ms'] for log in interactions if 'response_time_ms' in log]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Animal-specific statistics
        animal_stats = {}
        for log in interactions:
            animal = log.get('animal_shown')
            if animal:
                if animal not in animal_stats:
                    animal_stats[animal] = {'total': 0, 'correct': 0, 'incorrect': 0}
                animal_stats[animal]['total'] += 1
                if log.get('is_correct'):
                    animal_stats[animal]['correct'] += 1
                else:
                    animal_stats[animal]['incorrect'] += 1
        
        # Calculate accuracy per animal
        for animal in animal_stats:
            total = animal_stats[animal]['total']
            correct = animal_stats[animal]['correct']
            animal_stats[animal]['accuracy'] = (correct / total * 100) if total > 0 else 0
        
        return jsonify({
            'total_interactions': total_interactions,
            'correct_attempts': correct_count,
            'incorrect_attempts': incorrect_count,
            'accuracy_percentage': (correct_count / total_interactions * 100) if total_interactions > 0 else 0,
            'average_response_time_ms': round(avg_response_time, 2),
            'animal_statistics': animal_stats,
            'unique_sessions': len(set(log.get('session_id') for log in interactions if log.get('session_id')))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200


if __name__ == '__main__':
    print("Starting Animal Sounds Game Analytics Server...")
    print(f"Data will be stored in: {os.path.abspath(DATA_DIR)}")
    print(f"JSON logs: {os.path.abspath(LOGS_FILE)}")
    print(f"CSV data: {os.path.abspath(CSV_FILE)}")
    app.run(host='0.0.0.0', port=5000, debug=True)