# 🚀 How to Run the Python Backends Locally

## Quick Start (Run Both Backends)

You have two Python backends that work together:

### 1️⃣ Game Logging Backend (Port 5000)

**File**: `app.py`  
**Purpose**: Logs game interactions, saves data to CSV/JSON

### 2️⃣ AI Prediction Backend (Port 5001)

**File**: `prediction_api.py`  
**Purpose**: Analyzes gameplay and predicts hearing disabilities

---

## ✅ Step-by-Step Instructions

### Step 1: Open First Terminal for Game Backend

Open **PowerShell** and run:

```bash
cd C:\Users\user\OneDrive\Desktop\frontend\backend
py app.py
```

**Expected Output:**

```
Starting Animal Sounds Game Analytics Server...
Data will be stored in: C:\Users\user\OneDrive\Desktop\frontend\backend\game_analytics
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

✅ **Keep this terminal open!** Don't close it.

---

### Step 2: Open Second Terminal for Prediction Backend

Open a **NEW PowerShell window** and run:

```bash
cd C:\Users\user\OneDrive\Desktop\frontend\backend
py prediction_api.py
```

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
Server starting on http://localhost:5001
======================================================================

 * Running on http://127.0.0.1:5001
```

✅ **Keep this terminal open too!**

---

## 🔍 Verify Both Are Running

### Check Game Backend (Port 5000)

Open browser and visit:

```
http://localhost:5000/api/health
```

Should return:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T..."
}
```

### Check Prediction Backend (Port 5001)

Open browser and visit:

```
http://localhost:5001/api/predict/health
```

Should return:

```json
{
  "status": "healthy",
  "model_version": "1.0",
  "active_sessions": 0
}
```

---

## 📊 API Endpoints Summary

### Game Backend (Port 5000)

```
POST   http://localhost:5000/api/log-interaction
GET    http://localhost:5000/api/analytics
GET    http://localhost:5000/api/health
```

### Prediction Backend (Port 5001)

```
POST   http://localhost:5001/api/predict/record
POST   http://localhost:5001/api/predict/analyze
GET    http://localhost:5001/api/predict/session/<id>
GET    http://localhost:5001/api/predict/health
```

---

## 🛑 How to Stop the Servers

In each terminal window, press:

```
Ctrl + C
```

---

## 🔧 Troubleshooting

### Problem: "Address already in use"

**Solution**: Kill the process using the port

```bash
# Check what's using the ports
netstat -ano | findstr :5000
netstat -ano | findstr :5001

# Kill the process (replace XXXX with PID from above)
taskkill /PID XXXX /F
```

### Problem: "Module not found"

**Solution**: Install dependencies

```bash
py -m pip install flask flask-cors pandas numpy scikit-learn joblib
```

### Problem: "Model file not found"

**Solution**: Train the model first

```bash
cd C:\Users\user\OneDrive\Desktop\frontend\backend
py train_model.py
```

---

## 🎯 Quick Commands Reference

```bash
# Navigate to backend
cd C:\Users\user\OneDrive\Desktop\frontend\backend

# Start game backend (Terminal 1)
py app.py

# Start prediction backend (Terminal 2)
py prediction_api.py

# Test APIs
curl http://localhost:5000/api/health
curl http://localhost:5001/api/predict/health

# Or in PowerShell:
Invoke-RestMethod http://localhost:5000/api/health
Invoke-RestMethod http://localhost:5001/api/predict/health
```

---

## 📱 Frontend Configuration

Make sure your frontend uses the correct ports:

- **Game logging**: `http://localhost:5000`
- **Predictions**: `http://localhost:5001`

The `predictionService.js` has been updated to use port 5001 automatically.

---

## ✅ Success Checklist

- [ ] Terminal 1: Game backend running on port 5000
- [ ] Terminal 2: Prediction backend running on port 5001
- [ ] Both health checks return "healthy"
- [ ] No error messages in terminals
- [ ] Frontend can connect to both APIs

---

**Ready to go!** Both backends are now running and ready to handle requests from your Animal Sound Safari game.
