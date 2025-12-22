// Prediction Service for Animal Sound Safari Game
// This service handles communication with the hearing disability prediction API

const API_BASE_URL = 'http://localhost:5001/api/predict';

export class PredictionService {
  constructor() {
    this.sessionId = this.generateSessionId();
  }

  // Generate unique session ID
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  // Record a game attempt
  async recordAttempt(attemptData) {
    try {
      const response = await fetch(`${API_BASE_URL}/record`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
          animal_shown: attemptData.animalShown,
          animal_selected: attemptData.animalSelected,
          is_correct: attemptData.isCorrect,
          response_time_ms: attemptData.responseTime,
        }),
      });

      const data = await response.json();
      console.log('Attempt recorded:', data);
      return data;
    } catch (error) {
      console.error('Error recording attempt:', error);
      throw error;
    }
  }

  // Get prediction after sufficient attempts
  async analyzePrediction() {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: this.sessionId,
        }),
      });

      const data = await response.json();
      console.log('Prediction result:', data);
      return data;
    } catch (error) {
      console.error('Error getting prediction:', error);
      throw error;
    }
  }

  // Get session data
  async getSessionData() {
    try {
      const response = await fetch(`${API_BASE_URL}/session/${this.sessionId}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting session data:', error);
      throw error;
    }
  }

  // Check API health
  async checkHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API health check failed:', error);
      return { status: 'unhealthy' };
    }
  }

  // Reset session (start new game)
  resetSession() {
    this.sessionId = this.generateSessionId();
    console.log('New session started:', this.sessionId);
  }
}

// Example usage in your game component:
/*

// Initialize the service
const predictionService = new PredictionService();

// When child clicks an animal
async function handleAnimalClick(selectedAnimal, currentAnimal, clickTime) {
  const responseTime = clickTime - gameStartTime;
  const isCorrect = selectedAnimal === currentAnimal;

  // Record the attempt
  const result = await predictionService.recordAttempt({
    animalShown: currentAnimal,
    animalSelected: selectedAnimal,
    isCorrect: isCorrect,
    responseTime: responseTime
  });

  // Check if we have enough attempts to predict
  if (result.stats.can_predict && result.stats.total_attempts >= 10) {
    // Get prediction
    const prediction = await predictionService.analyzePrediction();
    
    if (prediction.success) {
      // Show prediction result to user
      showPredictionResult(prediction);
    }
  }

  // Update UI with current stats
  updateStats(result.stats);
}

// Show prediction result
function showPredictionResult(prediction) {
  const {
    has_hearing_disability,
    probability,
    risk_level,
    recommendation
  } = prediction;

  console.log('Hearing Disability:', has_hearing_disability);
  console.log('Probability:', probability.disability);
  console.log('Risk Level:', risk_level);
  console.log('Recommendation:', recommendation);

  // Display to user with appropriate UI
  // Example: Modal, notification, or results screen
}

*/

export default PredictionService;
