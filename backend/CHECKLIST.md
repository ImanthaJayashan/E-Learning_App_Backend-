# 📋 Quick Start Checklist

Use this checklist to ensure everything is set up correctly.

## ✅ Pre-Installation Checklist

- [ ] Python 3.11+ installed

  ```bash
  py --version
  ```

  Expected: `Python 3.11.x` or higher

- [ ] pip is available

  ```bash
  py -m pip --version
  ```

- [ ] You're in the correct directory
  ```bash
  cd C:\Users\user\OneDrive\Desktop\frontend\backend
  ```

## ✅ Installation Checklist

- [ ] Install Python packages

  ```bash
  py -m pip install pandas numpy scikit-learn joblib flask flask-cors requests
  ```

- [ ] Verify packages installed
  ```bash
  py -m pip list | Select-String "pandas|numpy|scikit-learn|flask"
  ```
  Should show: pandas, numpy, scikit-learn, flask, flask-cors

## ✅ Files Checklist

Verify these files exist in your backend folder:

- [ ] `train_model.py` - Model training script
- [ ] `prediction_api.py` - API server
- [ ] `generate_data.py` - Data generator
- [ ] `test_api.py` - Testing script
- [ ] `predictionService.js` - Frontend integration
- [ ] `start_api.bat` - Quick start batch file
- [ ] `hearing_model.pkl` - Trained model (136 KB)
- [ ] `model_config.json` - Model config
- [ ] `game_analytics/game_analytics.csv` - Training data (305 entries)

## ✅ Model Training Checklist (Already Done)

- [x] Generated training data (305 entries)
- [x] Trained ML model (100% accuracy)
- [x] Created model files:
  - [x] `hearing_model.pkl`
  - [x] `model_config.json`

## ✅ Running the API Checklist

### Method 1: Batch File

- [ ] Double-click `start_api.bat`
- [ ] Wait for message: "Server starting on http://localhost:5000"
- [ ] Keep the window open (don't close it)

### Method 2: Command Line

- [ ] Open PowerShell in backend folder
- [ ] Run: `py prediction_api.py`
- [ ] See message: "✓ Model loaded successfully"
- [ ] Server shows: "Running on http://127.0.0.1:5000"
- [ ] Keep terminal open

## ✅ Testing Checklist

- [ ] Open a NEW terminal (keep API running in first one)
- [ ] Navigate to backend:
  ```bash
  cd C:\Users\user\OneDrive\Desktop\frontend\backend
  ```
- [ ] Run test script:
  ```bash
  py test_api.py
  ```
- [ ] See: "✅ ALL TESTS COMPLETED!"

## ✅ API Health Check

- [ ] Open browser or PowerShell
- [ ] Test health endpoint:

  ```bash
  # Browser: Visit
  http://localhost:5000/api/predict/health

  # PowerShell: Run
  Invoke-RestMethod -Uri "http://localhost:5000/api/predict/health" -Method GET
  ```

- [ ] Should return:
  ```json
  {
    "status": "healthy",
    "model_version": "1.0",
    "active_sessions": 0
  }
  ```

## ✅ Frontend Integration Checklist

- [ ] Copy `predictionService.js` to your frontend source folder
- [ ] Import the service in your game component
- [ ] Initialize: `const predictionService = new PredictionService();`
- [ ] Track game start time: `let gameStartTime = Date.now();`
- [ ] Record attempts when child clicks:
  ```javascript
  await predictionService.recordAttempt({
    animalShown: currentAnimal,
    animalSelected: selectedAnimal,
    isCorrect: isCorrect,
    responseTime: Date.now() - gameStartTime,
  });
  ```
- [ ] Show prediction after 10+ attempts:
  ```javascript
  const prediction = await predictionService.analyzePrediction();
  ```

## ✅ Verification Checklist

After integration, test:

- [ ] Game records attempts successfully
- [ ] Stats update after each click (attempts, avg time)
- [ ] After 10 attempts, prediction button appears
- [ ] Clicking prediction shows results modal
- [ ] Results show:
  - [ ] Risk level (LOW/MODERATE/HIGH)
  - [ ] Probability percentage
  - [ ] Recommendation message
  - [ ] Key indicators
  - [ ] Next steps

## 🔧 Troubleshooting Checklist

If something doesn't work:

- [ ] Is API server running? (Check terminal)
- [ ] Is port 5000 free? (Check with `netstat -ano | findstr :5000`)
- [ ] Are all packages installed? (Run pip list)
- [ ] Is `hearing_model.pkl` present? (Check files)
- [ ] Is API URL correct in frontend? (`http://localhost:5000`)
- [ ] Check browser console for errors
- [ ] Check API terminal for error messages

## 📊 Expected Results Checklist

### For Normal Child (Fast Responses: 2500-5000ms)

- [ ] Risk Level: LOW
- [ ] Probability: 5-40%
- [ ] Message: "Normal Hearing Reaction Indicators"
- [ ] Green/Success indicator

### For Child with Potential Disability (Slow Responses: >6000ms)

- [ ] Risk Level: MODERATE or HIGH
- [ ] Probability: 60-95%
- [ ] Message: "Concern for Hearing Reaction"
- [ ] Yellow/Red indicator
- [ ] Recommendation to see specialist

## 🎯 Final Checklist

- [ ] API server is running on port 5000
- [ ] Test script passes all tests
- [ ] Frontend can connect to API
- [ ] Attempts are recorded correctly
- [ ] Predictions are displayed properly
- [ ] Results include recommendations
- [ ] Documentation reviewed

## 📝 Quick Commands Reference

```bash
# Navigate to backend
cd C:\Users\user\OneDrive\Desktop\frontend\backend

# Start API
py prediction_api.py

# Test API (in new terminal)
py test_api.py

# Retrain model
py train_model.py

# Check API health
Invoke-RestMethod -Uri "http://localhost:5000/api/predict/health" -Method GET
```

## ⚠️ Remember

- ✅ Keep API server running while using the game
- ✅ API must be started BEFORE loading the game
- ✅ Minimum 5 attempts needed for prediction
- ✅ Best results with 10-15 attempts
- ✅ This is a screening tool, not a diagnosis

---

**Status:**

- [x] System installed
- [x] Model trained
- [ ] API running
- [ ] Frontend integrated
- [ ] Tested successfully

**Next Step:** Start the API server using `start_api.bat` or `py prediction_api.py`
