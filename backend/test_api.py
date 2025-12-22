import requests
import json
import time

API_URL = 'http://localhost:5000/api/predict'

print("="*70)
print("🧪 TESTING HEARING DISABILITY PREDICTION API")
print("="*70)

# Test 1: Health Check
print("\n1. Testing Health Check...")
try:
    response = requests.get(f'{API_URL}/health')
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Response: {response.json()}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test 2: Create a session and record attempts (Normal child)
print("\n2. Testing Normal Child (Fast response times)...")
session_id = f"test_session_{int(time.time())}"

normal_attempts = [
    {'animal_shown': 'cow', 'animal_selected': 'cow', 'is_correct': True, 'response_time_ms': 2800},
    {'animal_shown': 'dog', 'animal_selected': 'dog', 'is_correct': True, 'response_time_ms': 3200},
    {'animal_shown': 'cat', 'animal_selected': 'cat', 'is_correct': True, 'response_time_ms': 2900},
    {'animal_shown': 'lion', 'animal_selected': 'lion', 'is_correct': True, 'response_time_ms': 3500},
    {'animal_shown': 'cow', 'animal_selected': 'dog', 'is_correct': False, 'response_time_ms': 4200},
    {'animal_shown': 'dog', 'animal_selected': 'dog', 'is_correct': True, 'response_time_ms': 3100},
    {'animal_shown': 'cat', 'animal_selected': 'cat', 'is_correct': True, 'response_time_ms': 2700},
    {'animal_shown': 'lion', 'animal_selected': 'lion', 'is_correct': True, 'response_time_ms': 3300},
    {'animal_shown': 'cow', 'animal_selected': 'cow', 'is_correct': True, 'response_time_ms': 2950},
    {'animal_shown': 'dog', 'animal_selected': 'dog', 'is_correct': True, 'response_time_ms': 3150},
]

for i, attempt in enumerate(normal_attempts, 1):
    attempt['session_id'] = session_id
    response = requests.post(f'{API_URL}/record', json=attempt)
    result = response.json()
    print(f"   Attempt {i}: {result['stats']['avg_response_time']}ms avg, "
          f"{result['stats']['accuracy_rate']*100:.0f}% accuracy")

# Get prediction
print("\n   Getting prediction...")
prediction_response = requests.post(f'{API_URL}/analyze', json={'session_id': session_id})
prediction = prediction_response.json()

if prediction['success']:
    print(f"   ✓ Prediction: {'HAS disability' if prediction['has_hearing_disability'] else 'NO disability'}")
    print(f"   ✓ Risk Level: {prediction['risk_level']}")
    print(f"   ✓ Disability Probability: {prediction['probability']['disability']*100:.1f}%")
    print(f"   ✓ Recommendation: {prediction['recommendation']['title']}")
else:
    print(f"   ✗ {prediction.get('message', 'Unknown error')}")

# Test 3: Test child with potential disability (Slow response times)
print("\n3. Testing Child with Potential Disability (Slow response times)...")
session_id2 = f"test_session_{int(time.time())}_2"

slow_attempts = [
    {'animal_shown': 'cow', 'animal_selected': 'cow', 'is_correct': True, 'response_time_ms': 7500},
    {'animal_shown': 'dog', 'animal_selected': 'dog', 'is_correct': True, 'response_time_ms': 8200},
    {'animal_shown': 'cat', 'animal_selected': 'lion', 'is_correct': False, 'response_time_ms': 11000},
    {'animal_shown': 'lion', 'animal_selected': 'lion', 'is_correct': True, 'response_time_ms': 9500},
    {'animal_shown': 'cow', 'animal_selected': 'dog', 'is_correct': False, 'response_time_ms': 13200},
    {'animal_shown': 'dog', 'animal_selected': 'dog', 'is_correct': True, 'response_time_ms': 8100},
    {'animal_shown': 'cat', 'animal_selected': 'cat', 'is_correct': True, 'response_time_ms': 7700},
    {'animal_shown': 'lion', 'animal_selected': 'cow', 'is_correct': False, 'response_time_ms': 14300},
    {'animal_shown': 'cow', 'animal_selected': 'cow', 'is_correct': True, 'response_time_ms': 9950},
    {'animal_shown': 'dog', 'animal_selected': 'cat', 'is_correct': False, 'response_time_ms': 12150},
]

for i, attempt in enumerate(slow_attempts, 1):
    attempt['session_id'] = session_id2
    response = requests.post(f'{API_URL}/record', json=attempt)
    result = response.json()
    print(f"   Attempt {i}: {result['stats']['avg_response_time']}ms avg, "
          f"{result['stats']['accuracy_rate']*100:.0f}% accuracy")

# Get prediction
print("\n   Getting prediction...")
prediction_response = requests.post(f'{API_URL}/analyze', json={'session_id': session_id2})
prediction = prediction_response.json()

if prediction['success']:
    print(f"   ✓ Prediction: {'⚠️  HAS disability' if prediction['has_hearing_disability'] else 'NO disability'}")
    print(f"   ✓ Risk Level: {prediction['risk_level']}")
    print(f"   ✓ Disability Probability: {prediction['probability']['disability']*100:.1f}%")
    print(f"   ✓ Recommendation: {prediction['recommendation']['title']}")
    print(f"\n   Key Indicators:")
    for indicator in prediction['recommendation']['key_indicators']:
        print(f"      • {indicator}")
    print(f"\n   Next Steps:")
    for step in prediction['recommendation']['next_steps']:
        print(f"      • {step}")
else:
    print(f"   ✗ {prediction.get('message', 'Unknown error')}")

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETED!")
print("="*70)
