from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load model and config
print("Loading hearing disability prediction model...")
model = joblib.load('hearing_model.pkl')
with open('model_config.json', 'r') as f:
    config = json.load(f)

print(f"✓ Model loaded successfully (version {config['version']})")
print(f"✓ Training accuracy: {config['test_accuracy']:.2%}")

# Store session data in memory
session_storage = {}

@app.route('/api/predict/record', methods=['POST'])
def record_attempt():
    """Record a game attempt"""
    data = request.json
    session_id = data['session_id']
    
    # Initialize session if new
    if session_id not in session_storage:
        session_storage[session_id] = {
            'attempts': [],
            'start_time': datetime.now().isoformat()
        }
    
    # Add attempt
    attempt = {
        'timestamp': datetime.now().isoformat(),
        'animal_shown': data['animal_shown'],
        'animal_selected': data['animal_selected'],
        'is_correct': data['is_correct'],
        'response_time_ms': data['response_time_ms'],
        'attempt_number': len(session_storage[session_id]['attempts'])
    }
    
    session_storage[session_id]['attempts'].append(attempt)
    
    # Calculate current stats
    attempts = session_storage[session_id]['attempts']
    response_times = [a['response_time_ms'] for a in attempts]
    correct = [a['is_correct'] for a in attempts]
    
    stats = {
        'total_attempts': len(attempts),
        'avg_response_time': int(np.mean(response_times)),
        'median_response_time': int(np.median(response_times)),
        'slow_responses': sum(1 for rt in response_times if rt > 6000),
        'accuracy_rate': sum(correct) / len(correct),
        'can_predict': len(attempts) >= config['min_attempts_for_prediction']
    }
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'stats': stats
    })

@app.route('/api/predict/analyze', methods=['POST'])
def analyze_session():
    """Analyze session and predict hearing disability"""
    data = request.json
    session_id = data['session_id']
    
    if session_id not in session_storage:
        return jsonify({'error': 'Session not found'}), 404
    
    attempts = session_storage[session_id]['attempts']
    
    # Check minimum attempts
    if len(attempts) < config['min_attempts_for_prediction']:
        return jsonify({
            'success': False,
            'message': f"Need at least {config['min_attempts_for_prediction']} attempts for prediction",
            'current_attempts': len(attempts),
            'required_attempts': config['min_attempts_for_prediction']
        })
    
    # Calculate features
    response_times = np.array([a['response_time_ms'] for a in attempts])
    correct_answers = np.array([a['is_correct'] for a in attempts])
    
    features = {
        'avg_response_time': np.mean(response_times),
        'median_response_time': np.median(response_times),
        'std_response_time': np.std(response_times),
        'max_response_time': np.max(response_times),
        'min_response_time': np.min(response_times),
        'response_time_range': np.max(response_times) - np.min(response_times),
        'slow_response_count': np.sum(response_times > 6000),
        'very_slow_count': np.sum(response_times > 10000),
        'slow_response_pct': np.sum(response_times > 6000) / len(response_times),
        'accuracy_rate': np.mean(correct_answers),
        'total_attempts': len(response_times),
        'incorrect_count': np.sum(~correct_answers)
    }
    
    # Make prediction
    feature_array = np.array([[features[col] for col in config['feature_columns']]])
    prediction = model.predict(feature_array)[0]
    probability = model.predict_proba(feature_array)[0]
    
    # Determine confidence and risk level
    disability_prob = probability[1]
    
    if disability_prob > 0.8:
        risk_level = 'HIGH'
        confidence = 'High'
    elif disability_prob > 0.6:
        risk_level = 'MODERATE'
        confidence = 'Medium'
    else:
        risk_level = 'LOW'
        confidence = 'Low'
    
    # Generate recommendation
    recommendation = generate_recommendation(prediction, disability_prob, features)
    
    result = {
        'success': True,
        'session_id': session_id,
        'total_attempts': len(attempts),
        'has_hearing_disability': bool(prediction),
        'probability': {
            'disability': float(disability_prob),
            'normal': float(probability[0])
        },
        'risk_level': risk_level,
        'confidence': confidence,
        'features': {
            'avg_response_time': int(features['avg_response_time']),
            'median_response_time': int(features['median_response_time']),
            'slow_responses': int(features['slow_response_count']),
            'accuracy_rate': float(features['accuracy_rate']),
            'total_attempts': int(features['total_attempts'])
        },
        'recommendation': recommendation
    }
    
    return jsonify(result)

def generate_recommendation(has_disability, probability, features):
    """Generate detailed recommendation based on prediction"""
    
    if has_disability:
        if probability > 0.8:
            return {
                'level': 'HIGH_RISK',
                'title': '⚠️ High Risk of Hearing Reaction Difficulty',
                'message': 'Strong indicators suggest this child may have hearing reaction difficulties.',
                'suggestion': 'We strongly recommend a comprehensive hearing assessment by a qualified audiologist or pediatric specialist.',
                'key_indicators': [
                    f"Average response time: {int(features['avg_response_time'])}ms (significantly slow)",
                    f"Slow responses: {int(features['slow_response_count'])} out of {int(features['total_attempts'])} attempts ({features['slow_response_pct']*100:.0f}%)",
                    f"Accuracy rate: {features['accuracy_rate']*100:.0f}%",
                    f"Maximum response time: {int(features['max_response_time'])}ms"
                ],
                'next_steps': [
                    'Schedule a hearing test with a pediatric audiologist',
                    'Monitor child\'s response to auditory cues in daily activities',
                    'Consider speech and language evaluation',
                    'Document any other signs of hearing difficulty'
                ]
            }
        else:
            return {
                'level': 'MODERATE_RISK',
                'title': '⚡ Moderate Concern for Hearing Reaction',
                'message': 'Some indicators suggest potential hearing reaction difficulties.',
                'suggestion': 'Consider monitoring the child more closely and schedule a follow-up assessment.',
                'key_indicators': [
                    f"Average response time: {int(features['avg_response_time'])}ms (moderately slow)",
                    f"Slow responses: {int(features['slow_response_count'])} out of {int(features['total_attempts'])} attempts",
                    f"Inconsistent response patterns detected"
                ],
                'next_steps': [
                    'Have the child play again in a quieter environment',
                    'Observe if response times improve with practice',
                    'Consult with pediatrician if concerns persist',
                    'Consider a baseline hearing screening'
                ]
            }
    else:
        return {
            'level': 'LOW_RISK',
            'title': '✅ Normal Hearing Reaction Indicators',
            'message': 'Response times and accuracy suggest normal hearing reaction abilities.',
            'suggestion': 'The child\'s auditory processing and reaction times appear to be within normal ranges.',
            'key_indicators': [
                f"Average response time: {int(features['avg_response_time'])}ms (normal)",
                f"Accuracy rate: {features['accuracy_rate']*100:.0f}% (good)",
                f"Consistent response patterns",
                f"Only {int(features['slow_response_count'])} slow responses"
            ],
            'next_steps': [
                'Continue regular developmental monitoring',
                'Encourage interactive games and activities',
                'Maintain routine pediatric check-ups'
            ]
        }

@app.route('/api/predict/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data"""
    if session_id not in session_storage:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'success': True,
        'session': session_storage[session_id]
    })

@app.route('/api/predict/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_version': config['version'],
        'active_sessions': len(session_storage)
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 HEARING DISABILITY PREDICTION API")
    print("="*70)
    print("\n📡 Available Endpoints:")
    print("  POST /api/predict/record   - Record game attempt")
    print("  POST /api/predict/analyze  - Analyze session and predict")
    print("  GET  /api/predict/session/<id> - Get session data")
    print("  GET  /api/predict/health   - Health check")
    print("\n" + "="*70)
    print("Server starting on http://localhost:5001")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
