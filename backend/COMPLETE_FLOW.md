# 🔄 Complete Data Flow: From Game to AI Prediction

## 📋 Table of Contents

1. [Overview](#overview)
2. [Phase 1: Data Collection](#phase-1-data-collection)
3. [Phase 2: Model Training](#phase-2-model-training)
4. [Phase 3: Real-time Prediction](#phase-3-real-time-prediction)
5. [Complete Flow Diagram](#complete-flow-diagram)
6. [File References](#file-references)

---

## Overview

This system has **two separate backends** working together:

| Backend           | File                | Port | Purpose                        |
| ----------------- | ------------------- | ---- | ------------------------------ |
| **Game Logging**  | `app.py`            | 5000 | Collect & store game data      |
| **AI Prediction** | `prediction_api.py` | 5001 | Analyze & predict disabilities |

---

## Phase 1: Data Collection

### 📊 How Game Data is Collected & Stored

#### Step 1.1: Child Plays the Game

**Frontend (React)** captures:

- Which animal sound was played
- Which animal child clicked
- How long they took to respond
- Whether answer was correct

```javascript
// Frontend code example
const attemptData = {
  session_id: "session_1733987654321_abc123",
  animal_shown: "cow",
  animal_selected: "cow",
  is_correct: true,
  response_time_ms: 3200,
  attempt_number: 1,
  total_score: 1,
  game_duration_sec: 3.2,
};
```

#### Step 1.2: Data Sent to Game Backend

**Request:**

```http
POST http://localhost:5000/api/log-interaction
Content-Type: application/json

{
  "session_id": "session_1733987654321_abc123",
  "animal_shown": "cow",
  "animal_selected": "cow",
  "is_correct": true,
  "response_time_ms": 3200,
  "attempt_number": 1,
  "total_score": 1,
  "game_duration_sec": 3.2
}
```

#### Step 1.3: Backend Stores Data

**File: `app.py`** (Lines 30-78)

```python
@app.route('/api/log-interaction', methods=['POST'])
def log_interaction():
    data = request.get_json()

    # Add timestamp
    data['timestamp'] = datetime.now().isoformat()

    # Store in TWO places:

    # 1. JSON file (complete log)
    logs = []
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)

    logs.append(data)

    with open(LOGS_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    # 2. CSV file (for ML training)
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
            data['total_score'],
            data['game_duration_sec']
        ])

    return jsonify({'status': 'success'})
```

#### Step 1.4: Data Storage Locations

**Location 1: JSON File**

- **File**: `backend/game_analytics/game_logs.json`
- **Format**: Array of all interactions
- **Purpose**: Complete audit log, debugging

```json
[
  {
    "session_id": "session_1733987654321_abc123",
    "timestamp": "2025-12-12T10:30:45.123456",
    "animal_shown": "cow",
    "animal_selected": "cow",
    "is_correct": true,
    "response_time_ms": 3200,
    "attempt_number": 1,
    "total_score": 1,
    "game_duration_sec": 3.2
  },
  ...
]
```

**Location 2: CSV File**

- **File**: `backend/game_analytics/game_analytics.csv`
- **Format**: Tabular data
- **Purpose**: Machine learning training

```csv
session_id,timestamp,animal_shown,animal_selected,is_correct,response_time_ms,attempt_number,total_score,game_duration_sec,has_hearing_disability
session_1733987654321_abc123,2025-12-12T10:30:45.123456,cow,cow,True,3200,1,1,3.2,False
session_1733987654321_abc123,2025-12-12T10:30:48.500000,dog,dog,True,3500,2,2,6.7,False
...
```

**Note**: The `has_hearing_disability` column is added manually or via `generate_data.py` for training purposes.

---

## Phase 2: Model Training

### 🧠 How the ML Model is Trained

#### Step 2.1: Prepare Training Data

**File: `generate_data.py`** (Optional - for synthetic data)

This script was used to generate 275 synthetic game sessions with realistic patterns:

- 83.6% normal children (fast responses: 2500-5000ms)
- 16.4% children with hearing difficulties (slow: 6000-12000ms)

```python
# Generates realistic game sessions
def generate_response_time(is_correct, attempt_number, has_disability=False):
    if has_disability:
        return random.uniform(6000, 12000)  # Slow
    else:
        return random.uniform(2400, 5200)   # Normal
```

**Output**: Appends 275 entries to `game_analytics.csv`

#### Step 2.2: Train the Model

**File: `train_model.py`** (Main training script)

**Step 2.2.1: Load Data**

```python
# Lines 17-18
df = pd.read_csv('game_analytics/game_analytics.csv')
print(f"Loaded {len(df)} records from {df['session_id'].nunique()} unique sessions")
```

**Example Data Loaded:**

```
305 records from 17 unique sessions
```

**Step 2.2.2: Feature Engineering**

```python
# Lines 21-45: Aggregate data by session
def create_session_features(df):
    session_stats = []

    for session_id in df['session_id'].unique():
        session_data = df[df['session_id'] == session_id]
        response_times = session_data['response_time_ms'].values
        correct_answers = session_data['is_correct'].values

        # Calculate 12 behavioral features
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
            'incorrect_count': np.sum(~correct_answers),
            'has_hearing_disability': session_data['has_hearing_disability'].iloc[0]
        }
        session_stats.append(features)

    return pd.DataFrame(session_stats)
```

**Transform:**

```
305 individual clicks
    ↓
17 session summaries (one per child)
```

**Example Session Features:**

```python
Session "abc123":
  avg_response_time: 3200,
  median_response_time: 3100,
  slow_response_count: 0,
  accuracy_rate: 0.85,
  has_hearing_disability: False
```

**Step 2.2.3: Split Data**

```python
# Lines 60-63
X = features_df[feature_columns]  # 12 features
y = features_df['has_hearing_disability']  # True/False

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)
```

**Split:**

```
17 sessions → 12 training + 5 testing
```

**Step 2.2.4: Train Random Forest**

```python
# Lines 73-80
rf_model = RandomForestClassifier(
    n_estimators=200,      # 200 decision trees
    max_depth=10,          # Max 10 levels deep
    min_samples_split=2,
    random_state=42,
    class_weight='balanced' # Handle imbalanced data
)

rf_model.fit(X_train, y_train)
```

**How Random Forest Works:**

```
Creates 200 decision trees, each asking:
  Tree 1: "Is avg_response_time > 5000?" → Vote: Normal
  Tree 2: "Is slow_response_count > 5?" → Vote: Normal
  Tree 3: "Is median_response_time > 7000?" → Vote: Disability
  ...
  Tree 200: Final vote

Final prediction: Majority vote (e.g., 195 say Normal → 97.5% confidence)
```

**Step 2.2.5: Evaluate Model**

```python
# Lines 84-100
y_pred = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2%}")
```

**Results:**

```
Accuracy: 100.00%
ROC-AUC Score: 1.000
Cross-Validation: 100.00%
```

**Step 2.2.6: Save Trained Model**

```python
# Lines 134-145
# Save model file
joblib.dump(rf_model, 'hearing_model.pkl')

# Save configuration
model_config = {
    'feature_columns': [...],
    'threshold_probability': 0.5,
    'min_attempts_for_prediction': 5,
    'version': '1.0',
    'training_date': datetime.now().isoformat(),
    'test_accuracy': 1.0
}

with open('model_config.json', 'w') as f:
    json.dump(model_config, f, indent=2)
```

**Output Files:**

- `hearing_model.pkl` (136 KB) - Trained model
- `model_config.json` - Model metadata

---

## Phase 3: Real-time Prediction

### 🎯 How Predictions Work During Gameplay

#### Step 3.1: Start Prediction API

```bash
py prediction_api.py
```

**File: `prediction_api.py`** (Lines 10-15)

```python
# Load the trained model into memory
model = joblib.load('hearing_model.pkl')
with open('model_config.json', 'r') as f:
    config = json.load(f)

# In-memory storage for active game sessions
session_storage = {}
```

**Server Status:**

```
✓ Model loaded (version 1.0)
✓ Training accuracy: 100.00%
✓ Running on http://localhost:5001
```

#### Step 3.2: Game Sends Data to BOTH Backends

**Important**: The frontend sends data to BOTH backends simultaneously:

**To Game Backend (app.py:5000)** - For permanent storage:

```javascript
// Save to CSV/JSON for future training
fetch("http://localhost:5000/api/log-interaction", {
  method: "POST",
  body: JSON.stringify(attemptData),
});
```

**To Prediction Backend (prediction_api.py:5001)** - For real-time analysis:

```javascript
// Store in memory for current session prediction
fetch("http://localhost:5001/api/predict/record", {
  method: "POST",
  body: JSON.stringify({
    session_id: sessionId,
    animal_shown: "cow",
    animal_selected: "cow",
    is_correct: true,
    response_time_ms: 3200,
  }),
});
```

#### Step 3.3: Prediction API Records Attempt

**File: `prediction_api.py`** (Lines 20-55)

```python
@app.route('/api/predict/record', methods=['POST'])
def record_attempt():
    data = request.json
    session_id = data['session_id']

    # Initialize session if new
    if session_id not in session_storage:
        session_storage[session_id] = {
            'attempts': [],
            'start_time': datetime.now().isoformat()
        }

    # Add this attempt to memory
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
    stats = calculate_session_stats(attempts)

    return jsonify({
        'success': True,
        'stats': stats,
        'can_predict': len(attempts) >= 5  # Need 5+ for prediction
    })
```

**In-Memory Storage Structure:**

```python
session_storage = {
    "session_abc123": {
        "start_time": "2025-12-12T10:30:45",
        "attempts": [
            {
                "animal_shown": "cow",
                "animal_selected": "cow",
                "is_correct": true,
                "response_time_ms": 3200,
                "attempt_number": 0
            },
            {
                "animal_shown": "dog",
                "animal_selected": "dog",
                "is_correct": true,
                "response_time_ms": 3500,
                "attempt_number": 1
            },
            ...
        ]
    },
    "session_xyz789": {
        ...
    }
}
```

**Note**: This data is in **RAM only** - lost when server restarts. Historical data is in `game_analytics.csv`.

#### Step 3.4: Frontend Requests Prediction

After 5+ attempts, frontend requests analysis:

```javascript
const response = await fetch("http://localhost:5001/api/predict/analyze", {
  method: "POST",
  body: JSON.stringify({
    session_id: sessionId,
  }),
});

const prediction = await response.json();
```

#### Step 3.5: API Analyzes & Predicts

**File: `prediction_api.py`** (Lines 57-150)

**Step 3.5.1: Retrieve Session Data**

```python
@app.route('/api/predict/analyze', methods=['POST'])
def analyze_session():
    session_id = data['session_id']
    attempts = session_storage[session_id]['attempts']

    # Check minimum attempts
    if len(attempts) < 5:
        return jsonify({
            'success': False,
            'message': 'Need at least 5 attempts'
        })
```

**Step 3.5.2: Calculate Features (Same as Training)**

```python
# Lines 73-91
response_times = [a['response_time_ms'] for a in attempts]
correct_answers = [a['is_correct'] for a in attempts]

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
```

**Example:**

```python
# Child clicked 10 times with these response times:
[3200, 3500, 2900, 4100, 3000, 3300, 2800, 3600, 3100, 2950]

# Calculated features:
{
  'avg_response_time': 3245,      # Mean
  'median_response_time': 3100,   # Median
  'slow_response_count': 0,       # None > 6000ms
  'accuracy_rate': 0.90,          # 9 out of 10 correct
  ...
}
```

**Step 3.5.3: Make Prediction**

```python
# Lines 93-96
# Convert features to array in correct order
feature_array = np.array([[features[col] for col in config['feature_columns']]])

# Get prediction
prediction = model.predict(feature_array)[0]      # True/False
probability = model.predict_proba(feature_array)[0]  # [normal_prob, disability_prob]
```

**Model Process:**

```
Input: [3245, 3100, 0, 0.90, ...] (12 features)
  ↓
Random Forest (200 trees voting)
  ↓
Output:
  - Prediction: False (no disability)
  - Probability: [0.95, 0.05] (95% normal, 5% disability)
```

**Step 3.5.4: Determine Risk Level**

```python
# Lines 98-107
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
```

**Step 3.5.5: Generate Recommendation**

```python
# Lines 152-234
def generate_recommendation(has_disability, probability, features):
    if has_disability and probability > 0.8:
        return {
            'level': 'HIGH_RISK',
            'title': '⚠️ High Risk of Hearing Reaction Difficulty',
            'message': 'Strong indicators suggest this child may have hearing reaction difficulties.',
            'suggestion': 'We strongly recommend a comprehensive hearing assessment...',
            'key_indicators': [
                f"Average response time: {features['avg_response_time']}ms (significantly slow)",
                f"Slow responses: {features['slow_response_count']} out of {features['total_attempts']}",
                ...
            ],
            'next_steps': [
                'Schedule a hearing test with pediatric audiologist',
                'Monitor child\'s response to auditory cues',
                ...
            ]
        }
```

**Step 3.5.6: Return Result**

```python
# Lines 109-125
result = {
    'success': True,
    'session_id': session_id,
    'total_attempts': len(attempts),
    'has_hearing_disability': bool(prediction),
    'probability': {
        'disability': float(probability[1]),
        'normal': float(probability[0])
    },
    'risk_level': risk_level,
    'confidence': confidence,
    'features': {...},
    'recommendation': {...}
}

return jsonify(result)
```

**Example Response:**

```json
{
  "success": true,
  "session_id": "session_abc123",
  "total_attempts": 10,
  "has_hearing_disability": false,
  "probability": {
    "disability": 0.05,
    "normal": 0.95
  },
  "risk_level": "LOW",
  "confidence": "High",
  "features": {
    "avg_response_time": 3245,
    "median_response_time": 3100,
    "slow_responses": 0,
    "accuracy_rate": 0.9
  },
  "recommendation": {
    "level": "LOW_RISK",
    "title": "✅ Normal Hearing Reaction Indicators",
    "message": "Response times and accuracy suggest normal hearing reaction abilities.",
    "key_indicators": [
      "Average response time: 3245ms (normal)",
      "Accuracy rate: 90% (good)",
      "Consistent response patterns"
    ],
    "next_steps": [
      "Continue regular developmental monitoring",
      "Encourage interactive games"
    ]
  }
}
```

#### Step 3.6: Frontend Displays Results

```javascript
function showResults(prediction) {
  // Show modal/dialog with:
  // - Risk level (LOW/MODERATE/HIGH)
  // - Probability percentage
  // - Recommendation message
  // - Key indicators
  // - Next steps
}
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: DATA COLLECTION                         │
└─────────────────────────────────────────────────────────────────────────┘

   ┌──────────────┐
   │   Frontend   │
   │ (React Game) │
   └──────┬───────┘
          │
          │ Child clicks: cow @ 3200ms
          │
          ├────────────────────────────┬─────────────────────────────┐
          │                            │                             │
          ▼                            ▼                             ▼
   ┌──────────────┐            ┌──────────────┐            ┌──────────────┐
   │   app.py     │            │prediction_api│            │  (Display)   │
   │  Port 5000   │            │  Port 5001   │            │              │
   └──────┬───────┘            └──────┬───────┘            └──────────────┘
          │                           │
          │ Store permanently         │ Store in memory (temp)
          │                           │
          ▼                           ▼
   ┌──────────────┐            ┌──────────────┐
   │game_logs.json│            │session_      │
   │(Complete log)│            │storage{}     │
   └──────────────┘            │(RAM only)    │
          │                    └──────────────┘
          ▼
   ┌──────────────┐
   │game_analytics│
   │    .csv      │  ← Used for training
   │(305 entries) │
   └──────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                       PHASE 2: MODEL TRAINING                           │
│                          (One-time setup)                               │
└─────────────────────────────────────────────────────────────────────────┘

   ┌──────────────────┐
   │ game_analytics   │
   │     .csv         │
   │  (305 entries)   │
   └────────┬─────────┘
            │
            │ Load data
            ▼
   ┌──────────────────┐
   │  train_model.py  │
   └────────┬─────────┘
            │
            ├─ 1. Load CSV (305 clicks)
            │
            ├─ 2. Group by session (17 sessions)
            │
            ├─ 3. Calculate features per session:
            │    • avg_response_time: 3245ms
            │    • slow_response_count: 0
            │    • accuracy_rate: 0.90
            │    • ... (12 total features)
            │
            ├─ 4. Split data:
            │    • Training: 12 sessions
            │    • Testing: 5 sessions
            │
            ├─ 5. Train Random Forest:
            │    • Create 200 decision trees
            │    • Each tree learns patterns
            │    • Combine votes for prediction
            │
            ├─ 6. Evaluate:
            │    • Accuracy: 100%
            │    • ROC-AUC: 1.000
            │
            └─ 7. Save outputs:
                    │
                    ├──────────────┬────────────────┐
                    ▼              ▼                ▼
            ┌──────────────┐ ┌──────────┐  ┌──────────────┐
            │hearing_model │ │  model_  │  │  Terminal    │
            │    .pkl      │ │ config   │  │  Output      │
            │  (136 KB)    │ │  .json   │  │  (Metrics)   │
            └──────────────┘ └──────────┘  └──────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE 3: REAL-TIME PREDICTION                      │
│                        (During actual gameplay)                         │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: Start Prediction API
   ┌──────────────────┐
   │ prediction_api.py│
   └────────┬─────────┘
            │
            ├─ Load hearing_model.pkl
            ├─ Load model_config.json
            ├─ Initialize session_storage = {}
            │
            ▼
   ┌──────────────────┐
   │  API Ready on    │
   │  Port 5001       │
   └──────────────────┘


STEP 2-3: Child Plays & Data Recorded
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │
          │ Click 1: cow @ 3200ms
          │
          ▼
   POST /api/predict/record
   {
     session_id: "abc123",
     animal_shown: "cow",
     animal_selected: "cow",
     is_correct: true,
     response_time_ms: 3200
   }
          │
          ▼
   ┌──────────────────────────────┐
   │ prediction_api.py            │
   │                              │
   │ session_storage["abc123"] =  │
   │   attempts: [                │
   │     {response_time: 3200},   │
   │     {response_time: 3500},   │
   │     {response_time: 2900},   │
   │     ... (accumulating)       │
   │   ]                          │
   └──────────────────────────────┘
          │
          │ Return current stats
          ▼
   {
     success: true,
     stats: {
       total_attempts: 3,
       avg_response_time: 3200,
       can_predict: false  ← Need 5+
     }
   }


STEP 4-6: Request & Get Prediction (After 5+ attempts)
   ┌──────────────┐
   │   Frontend   │
   └──────┬───────┘
          │
          │ 10 attempts completed
          │
          ▼
   POST /api/predict/analyze
   {
     session_id: "abc123"
   }
          │
          ▼
   ┌─────────────────────────────────────────┐
   │ prediction_api.py                       │
   │                                         │
   │ 1. Get stored attempts:                 │
   │    [3200, 3500, 2900, 4100, 3000, ...]  │
   │                                         │
   │ 2. Calculate features:                  │
   │    avg_response_time: 3245              │
   │    median_response_time: 3100           │
   │    slow_response_count: 0               │
   │    accuracy_rate: 0.90                  │
   │    ... (12 features total)              │
   │                                         │
   │ 3. Feed to model:                       │
   │    ┌─────────────────┐                  │
   │    │ hearing_model   │                  │
   │    │   .pkl (RAM)    │                  │
   │    └────────┬────────┘                  │
   │             │                           │
   │             │ Random Forest predicts    │
   │             ▼                           │
   │    Prediction: False (no disability)    │
   │    Probability: [0.95, 0.05]            │
   │                                         │
   │ 4. Determine risk:                      │
   │    5% < 60% → LOW RISK                  │
   │                                         │
   │ 5. Generate recommendation              │
   └─────────────────┬───────────────────────┘
                     │
                     ▼
   {
     success: true,
     has_hearing_disability: false,
     probability: {
       disability: 0.05,
       normal: 0.95
     },
     risk_level: "LOW",
     confidence: "High",
     recommendation: {
       title: "✅ Normal Hearing",
       message: "Response times appear normal",
       key_indicators: [
         "Avg: 3245ms (normal)",
         "Accuracy: 90%"
       ],
       next_steps: [
         "Continue monitoring"
       ]
     }
   }
                     │
                     ▼
   ┌──────────────────────┐
   │   Frontend           │
   │   Display Results:   │
   │                      │
   │   ✅ LOW RISK        │
   │   95% Normal         │
   │   Continue monitoring│
   └──────────────────────┘
```

---

## File References

### Data Files

| File                 | Location                  | Size   | Purpose            | Format          |
| -------------------- | ------------------------- | ------ | ------------------ | --------------- |
| `game_logs.json`     | `backend/game_analytics/` | Varies | Complete audit log | JSON array      |
| `game_analytics.csv` | `backend/game_analytics/` | ~50KB  | ML training data   | CSV table       |
| `hearing_model.pkl`  | `backend/`                | 136KB  | Trained ML model   | Binary (pickle) |
| `model_config.json`  | `backend/`                | 2KB    | Model metadata     | JSON object     |

### Code Files

| File                     | Lines | Purpose                 | Key Functions                            |
| ------------------------ | ----- | ----------------------- | ---------------------------------------- |
| **app.py**               | 235   | Game logging backend    | `log_interaction()`, `get_analytics()`   |
| **prediction_api.py**    | 245   | AI prediction backend   | `record_attempt()`, `analyze_session()`  |
| **train_model.py**       | 200+  | Model training script   | `create_session_features()`, `train()`   |
| **generate_data.py**     | 150+  | Generate synthetic data | `generate_game_data()`                   |
| **predictionService.js** | 150   | Frontend API client     | `recordAttempt()`, `analyzePrediction()` |

### Key Code Sections

#### app.py - Store Data

```python
# Lines 30-78: Main logging endpoint
@app.route('/api/log-interaction', methods=['POST'])
def log_interaction():
    # Stores in both JSON and CSV
```

#### prediction_api.py - Load Model

```python
# Lines 10-15: Initialize
model = joblib.load('hearing_model.pkl')
session_storage = {}
```

#### prediction_api.py - Record Attempt

```python
# Lines 20-55: Store in memory
@app.route('/api/predict/record', methods=['POST'])
def record_attempt():
    session_storage[session_id]['attempts'].append(attempt)
```

#### prediction_api.py - Make Prediction

```python
# Lines 57-125: Analyze & predict
@app.route('/api/predict/analyze', methods=['POST'])
def analyze_session():
    features = calculate_features(attempts)
    prediction = model.predict([features])
    return recommendation
```

#### train_model.py - Feature Engineering

```python
# Lines 21-45: Transform raw clicks → session features
def create_session_features(df):
    # Groups 305 clicks → 17 session summaries
```

#### train_model.py - Train Model

```python
# Lines 73-80: Train Random Forest
rf_model = RandomForestClassifier(n_estimators=200)
rf_model.fit(X_train, y_train)
```

---

## Data Flow Summary

### Collection Flow

```
Child plays → Frontend → app.py:5000 → CSV/JSON files
                      ↓
              prediction_api.py:5001 → RAM (session_storage)
```

### Training Flow

```
game_analytics.csv → train_model.py → hearing_model.pkl
                                    → model_config.json
```

### Prediction Flow

```
Child plays → prediction_api.py (in RAM)
            ↓
    Calculate features (same as training)
            ↓
    Feed to loaded model
            ↓
    Get prediction + confidence
            ↓
    Generate recommendation
            ↓
    Return to Frontend
```

---

## Key Differences Between Backends

| Aspect            | app.py (5000)                | prediction_api.py (5001)     |
| ----------------- | ---------------------------- | ---------------------------- |
| **Purpose**       | Permanent data storage       | Real-time analysis           |
| **Storage**       | File system (CSV/JSON)       | RAM only (session_storage)   |
| **Data Lifetime** | Permanent                    | Until server restarts        |
| **Used For**      | Historical records, training | Current session predictions  |
| **Dependencies**  | Flask, CSV                   | Flask, scikit-learn, joblib  |
| **Model**         | None                         | Uses hearing_model.pkl       |
| **Input**         | Full game interaction data   | Same, but stores differently |
| **Output**        | Success confirmation         | Prediction + recommendation  |

---

## Common Questions

### Q: Why two backends?

**A:** Separation of concerns:

- **app.py**: Handles data persistence (save everything)
- **prediction_api.py**: Handles AI logic (analyze current session)

### Q: Where is session data stored during gameplay?

**A:** In two places:

1. **prediction_api.py** - RAM (for current predictions)
2. **app.py** - Disk (CSV/JSON for permanent records)

### Q: How does the model know what to predict?

**A:** It learned patterns during training:

- Fast responses (2500-5000ms) → Normal
- Slow responses (>6000ms) → Potential disability

### Q: What happens if prediction_api.py restarts?

**A:** Active sessions are lost from RAM, but historical data in CSV is safe. Model will reload from `hearing_model.pkl`.

### Q: Can I retrain the model with new data?

**A:** Yes! Add new entries to `game_analytics.csv` and run:

```bash
py train_model.py
```

This generates a new `hearing_model.pkl` with updated patterns.

---

## Quick Commands

```bash
# 1. Generate synthetic training data (optional)
cd backend
py generate_data.py

# 2. Train the model
py train_model.py
# Creates: hearing_model.pkl + model_config.json

# 3. Start backends
py app.py              # Terminal 1 - Port 5000
py prediction_api.py    # Terminal 2 - Port 5001

# 4. Start frontend
cd ../animal-sound-safari
npm run dev            # Terminal 3 - Port 8080
```

---

**System Status**: All components explained! 🎯

This document provides the complete end-to-end flow from data collection through model training to real-time predictions.
