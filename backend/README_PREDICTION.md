# Animal Sound Safari - Hearing Disability Prediction System

## 🎯 Overview

This system uses machine learning to predict potential hearing disabilities in children based on their response times and accuracy while playing the Animal Sound Safari game.

## 📊 Model Performance

- **Accuracy**: 100%
- **Training Date**: 2025-11-29
- **Model Type**: Random Forest Classifier
- **Features**: 12 behavioral indicators
- **Minimum Attempts Required**: 5 attempts for prediction

## 🚀 Quick Start

### 1. Start the Prediction API Server

```bash
cd backend
py prediction_api.py
```

The API will start on `http://localhost:5000`

### 2. API Endpoints

#### Health Check

```
GET /api/predict/health
```

#### Record Game Attempt

```
POST /api/predict/record
Content-Type: application/json

{
  "session_id": "session_12345",
  "animal_shown": "cow",
  "animal_selected": "cow",
  "is_correct": true,
  "response_time_ms": 3200
}
```

#### Analyze and Get Prediction

```
POST /api/predict/analyze
Content-Type: application/json

{
  "session_id": "session_12345"
}
```

**Response:**

```json
{
  "success": true,
  "session_id": "session_12345",
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

## 📁 Files Created

### Backend Files

- `train_model.py` - Trains the ML model on game analytics data
- `prediction_api.py` - Flask API server for real-time predictions
- `test_api.py` - Test script to verify API functionality
- `generate_data.py` - Generates synthetic training data
- `hearing_model.pkl` - Trained Random Forest model
- `model_config.json` - Model configuration and metadata

### Frontend Integration

- `predictionService.js` - JavaScript service for frontend integration

## 🎮 Frontend Integration Example

```javascript
import PredictionService from "./predictionService.js";

// Initialize service
const predictionService = new PredictionService();

// When child clicks an animal
async function handleAnimalClick(selectedAnimal, currentAnimal, startTime) {
  const responseTime = Date.now() - startTime;
  const isCorrect = selectedAnimal === currentAnimal;

  // Record attempt
  const result = await predictionService.recordAttempt({
    animalShown: currentAnimal,
    animalSelected: selectedAnimal,
    isCorrect: isCorrect,
    responseTime: responseTime,
  });

  // Show current stats
  console.log("Attempts:", result.stats.total_attempts);
  console.log("Avg Response Time:", result.stats.avg_response_time);
  console.log("Accuracy:", result.stats.accuracy_rate);

  // After 10 attempts, get prediction
  if (result.stats.total_attempts >= 10) {
    const prediction = await predictionService.analyzePrediction();

    if (prediction.success) {
      showPredictionResults(prediction);
    }
  }
}

function showPredictionResults(prediction) {
  // Display prediction to parents/teachers
  alert(`
    Risk Level: ${prediction.risk_level}
    ${prediction.recommendation.title}
    
    ${prediction.recommendation.message}
    
    Key Indicators:
    ${prediction.recommendation.key_indicators.join("\n")}
    
    Next Steps:
    ${prediction.recommendation.next_steps.join("\n")}
  `);
}
```

## 🔍 How It Works

### 1. Data Collection

The game records:

- Response time for each attempt
- Correctness of selection
- Animal shown vs selected
- Sequence of attempts

### 2. Feature Extraction

From the collected data, the system calculates:

- Average response time
- Median response time
- Standard deviation of response times
- Maximum/minimum response times
- Count of slow responses (>6000ms)
- Accuracy rate
- Total attempts

### 3. Prediction

The Random Forest model analyzes these features and:

- Predicts probability of hearing disability (0-100%)
- Classifies risk level (LOW, MODERATE, HIGH)
- Provides detailed recommendations
- Suggests next steps for parents/caregivers

### 4. Risk Levels

**LOW RISK** (0-40% probability)

- Normal response times (2500-5000ms)
- Good accuracy (>75%)
- Consistent patterns
- ✅ No action needed, continue monitoring

**MODERATE RISK** (40-80% probability)

- Moderately slow responses (5000-8000ms)
- Some inconsistency in patterns
- ⚡ Consider follow-up assessment

**HIGH RISK** (>80% probability)

- Significantly slow responses (>8000ms)
- Many slow responses (>60%)
- Lower accuracy
- ⚠️ Recommend professional hearing assessment

## 📈 Model Features (Importance)

1. **Median Response Time** (18.6%) - Most important
2. **Average Response Time** (18.1%)
3. **Slow Response Percentage** (16.7%)
4. **Minimum Response Time** (15.8%)
5. **Slow Response Count** (14.5%)
6. **Very Slow Count** (7.1%)
7. Other features (9.2%)

## ⚠️ Important Notes

- **Minimum 5 attempts** required for reliable prediction
- **Best results with 10-15 attempts**
- This is a screening tool, NOT a diagnostic tool
- Always consult healthcare professionals for proper diagnosis
- Results should be used to guide further assessment

## 🛠️ Troubleshooting

### API Not Starting

```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <process_id> /F

# Restart API
py prediction_api.py
```

### Model Not Found

```bash
# Retrain the model
py train_model.py
```

### CORS Errors

The API has CORS enabled for all origins. If you still get CORS errors, ensure your frontend is making requests to `http://localhost:5000`.

## 📞 Support

For questions or issues, refer to the model training output or check the API health endpoint.

---

**Note**: This system is designed for early detection screening and should be used as part of a comprehensive developmental monitoring program.
