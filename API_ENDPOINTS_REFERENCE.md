# 🌐 Complete API Endpoints Reference

## Base URL
```
http://localhost:5000/api
```

---

## 🎮 GAME SESSIONS API

### Save Game Session
**POST** `/games/save-session`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "gameType": "ninja_game",
  "score": 25,
  "targetShape": "circle",
  "elapsedTime": 180,
  "misses": 3,
  "gameStatus": "completed"
}
```

**Response (Success):**
```json
{
  "success": true,
  "sessionId": "507f1f77bcf86cd799439011",
  "message": "Game session saved successfully"
}
```

---

### Get User Game Sessions
**GET** `/games/user-sessions/student_ravi`

**Optional Query Parameters:**
- `days=7` - Get sessions from last N days (default: 7)

**Response:**
```json
{
  "success": true,
  "count": 12,
  "sessions": [
    {
      "userId": "student_ravi",
      "gameType": "ninja_game",
      "score": 25,
      "elapsedTime": 180,
      "createdAt": "2026-02-03T10:33:00Z"
    },
    // ... more sessions
  ]
}
```

---

## 🏥 VISION THERAPY API

### Save Therapy Session
**POST** `/therapy/save-session`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "gameTitle": "Ninja Game",
  "startTime": "2026-02-03T10:30:00Z",
  "endTime": "2026-02-03T10:33:00Z",
  "duration": 180,
  "difficulty": "medium",
  "status": "completed"
}
```

**Response:**
```json
{
  "success": true,
  "sessionId": "507f1f77bcf86cd799439012",
  "message": "Vision therapy session saved"
}
```

---

### Get User Therapy Sessions
**GET** `/therapy/user-sessions/student_ravi?days=7`

**Response:**
```json
{
  "success": true,
  "count": 7,
  "period_days": 7,
  "sessions": [
    {
      "userId": "student_ravi",
      "gameTitle": "Ninja Game",
      "duration": 180,
      "status": "completed",
      "createdAt": "2026-02-03T10:33:00Z"
    },
    // ... more sessions
  ]
}
```

---

## 👁️ EYE DETECTION API

### Save Eye Detection Result
**POST** `/eye-detection/save`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "result": "lazy_eye",
  "probability": 0.92,
  "confidence": "high",
  "eyeType": "left",
  "analysisDetails": {
    "pupilSize": 4.5,
    "gazeFocus": "normal",
    "blinkRate": 18
  }
}
```

**Response:**
```json
{
  "success": true,
  "detectionId": "507f1f77bcf86cd799439013",
  "message": "Eye detection saved"
}
```

---

### Get Latest Eye Detection
**GET** `/eye-detection/latest/student_ravi`

**Response:**
```json
{
  "success": true,
  "result": {
    "userId": "student_ravi",
    "result": "lazy_eye",
    "probability": 0.92,
    "confidence": "high",
    "createdAt": "2026-02-03T10:45:00Z"
  },
  "message": "Latest detection retrieved"
}
```

---

### Get Eye Detection History
**GET** `/eye-detection/history/student_ravi?days=30`

**Response:**
```json
{
  "success": true,
  "count": 3,
  "period_days": 30,
  "results": [
    {
      "userId": "student_ravi",
      "result": "lazy_eye",
      "probability": 0.92,
      "createdAt": "2026-02-03T10:45:00Z"
    },
    {
      "userId": "student_ravi",
      "result": "lazy_eye",
      "probability": 0.88,
      "createdAt": "2026-02-02T14:20:00Z"
    },
    {
      "userId": "student_ravi",
      "result": "normal_eye",
      "probability": 0.05,
      "createdAt": "2026-02-01T09:15:00Z"
    }
  ]
}
```

---

## 👤 USER PROFILE API

### Create/Update User Profile
**POST** `/user/profile`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "name": "Ravi Kumar",
  "age": 8,
  "grade": "Grade 3",
  "parentName": "Shyam Kumar",
  "parentEmail": "shyam@email.com",
  "parentPhone": "+94712345678",
  "diagnosis": "Amblyopia",
  "status": "active"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User profile saved",
  "isNew": true
}
```

---

### Get User Profile
**GET** `/user/profile/student_ravi`

**Response:**
```json
{
  "success": true,
  "profile": {
    "userId": "student_ravi",
    "name": "Ravi Kumar",
    "age": 8,
    "parentEmail": "shyam@email.com",
    "diagnosis": "Amblyopia",
    "updatedAt": "2026-02-03T10:33:05Z"
  },
  "message": "User profile retrieved"
}
```

---

## 📊 LEARNING STATS API

### Get Learning Statistics
**GET** `/stats/learning/student_ravi`

**Response:**
```json
{
  "success": true,
  "stats": {
    "userId": "student_ravi",
    "circle": {
      "totalTime": 450,
      "visits": 5,
      "lastVisit": "2026-02-03T10:33:00Z",
      "averageScore": 12.4
    },
    "square": {
      "totalTime": 320,
      "visits": 3,
      "lastVisit": "2026-02-02T14:20:00Z",
      "averageScore": 10.2
    },
    "triangle": {
      "totalTime": 280,
      "visits": 2,
      "lastVisit": "2026-02-01T11:15:00Z",
      "averageScore": 9.8
    },
    "star": {
      "totalTime": 510,
      "visits": 6,
      "lastVisit": "2026-02-03T09:45:00Z",
      "averageScore": 13.5
    },
    "updatedAt": "2026-02-03T10:33:05Z"
  },
  "message": "Learning stats retrieved"
}
```

---

### Update Learning Statistics
**POST** `/stats/learning`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "circle": {
    "totalTime": 450,
    "visits": 5,
    "averageScore": 12.4
  },
  "square": {
    "totalTime": 320,
    "visits": 3,
    "averageScore": 10.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Learning stats updated"
}
```

---

## 📝 ACTIVITY LOG API

### Log Activity
**POST** `/activity/log`

**Request Body:**
```json
{
  "userId": "student_ravi",
  "activityType": "game_started",
  "gameType": "ninja_game",
  "details": {
    "device": "web_browser",
    "duration": 180
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Activity logged"
}
```

---

## 📊 PARENT DASHBOARD API (MAIN)

### Get Comprehensive Report
**GET** `/dashboard/report/student_ravi?days=7`

**Parameters:**
- `days=7` - Report for last N days (default: 7)

**Response:**
```json
{
  "success": true,
  "userId": "student_ravi",
  "period_days": 7,
  
  "gameMetrics": {
    "totalSessions": 12,
    "totalScore": 145,
    "averageScore": 12.08,
    "totalTime": 2160,
    "gameBreakdown": {
      "ninja_game": { "count": 5, "totalScore": 65 },
      "snake_game": { "count": 4, "totalScore": 52 },
      "amblocar": { "count": 3, "totalScore": 28 }
    }
  },
  
  "visionTherapyMetrics": {
    "totalSessions": 7,
    "totalTime": 2100,
    "gamesPlayed": ["Ninja Game", "Snake Game", "AmbloCar"]
  },
  
  "eyeDetectionMetrics": {
    "totalDetections": 3,
    "lazyEyeCount": 2,
    "normalEyeCount": 1,
    "lazyEyePercentage": 66.67
  },
  
  "userProfile": {
    "userId": "student_ravi",
    "name": "Ravi Kumar",
    "age": 8,
    "diagnosis": "Amblyopia"
  },
  
  "learningStats": {
    "circle": { "totalTime": 450, "visits": 5, "averageScore": 12.4 },
    "square": { "totalTime": 320, "visits": 3, "averageScore": 10.2 },
    "triangle": { "totalTime": 280, "visits": 2, "averageScore": 9.8 },
    "star": { "totalTime": 510, "visits": 6, "averageScore": 13.5 }
  },
  
  "reportGeneratedAt": "2026-02-03T15:30:00Z"
}
```

---

## 🔍 HEALTH CHECK API

### System Health
**GET** `/health`

**Response:**
```json
{
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
  "timestamp": "2026-02-03T15:30:00Z"
}
```

---

## 🧪 Testing the APIs

### Using cURL

```bash
# Save a game session
curl -X POST http://localhost:5000/api/games/save-session \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "student_ravi",
    "gameType": "ninja_game",
    "score": 25,
    "elapsedTime": 180
  }'

# Get user games
curl http://localhost:5000/api/games/user-sessions/student_ravi

# Get dashboard report
curl http://localhost:5000/api/dashboard/report/student_ravi?days=7

# Health check
curl http://localhost:5000/api/health
```

### Using JavaScript/Fetch

```javascript
// Save game session
const response = await fetch('http://localhost:5000/api/games/save-session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    userId: 'student_ravi',
    gameType: 'ninja_game',
    score: 25,
    elapsedTime: 180
  })
});
const data = await response.json();
console.log(data);

// Get dashboard report
const report = await fetch('http://localhost:5000/api/dashboard/report/student_ravi?days=7');
const reportData = await report.json();
console.log(reportData);
```

---

## 📌 Common Response Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET request returns data |
| 201 | Created | New document inserted |
| 400 | Bad Request | Missing required fields |
| 404 | Not Found | User ID doesn't exist |
| 500 | Server Error | Database connection failed |

---

## ✅ API Summary

```
Total Endpoints: 15

Games:        2 endpoints
Therapy:      2 endpoints
Eye Detection: 3 endpoints
User Profile: 2 endpoints
Learning Stats: 2 endpoints
Activity Log: 1 endpoint
Dashboard:    1 endpoint
Health:       1 endpoint
Ninja Game:   1 endpoint (legacy)
```

All endpoints are live and ready to use! 🚀
