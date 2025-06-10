/**
 * Game API Client for Quiz Game Collection Mobile Apps
 * 
 * This client provides a clean interface to communicate with the FastAPI backend,
 * maintaining the same functionality as the desktop apps while optimized for mobile.
 */

/**
 * API Configuration
 */
const API_CONFIG = {
  // Default to localhost for development
  // In production, this should be your deployed API URL
  baseURL: __DEV__ ? 'http://localhost:8000' : 'https://your-api-domain.com',
  timeout: 10000, // 10 seconds
  retries: 3,
};

/**
 * HTTP Client with error handling and retries
 */
class HTTPClient {
  constructor(baseURL, timeout = 10000) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      timeout: this.timeout,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  async get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  async post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

/**
 * Game API Client
 */
class GameAPI {
  constructor(baseURL = API_CONFIG.baseURL) {
    this.client = new HTTPClient(baseURL, API_CONFIG.timeout);
    this.currentGameId = null;
  }

  /**
   * Health check - verify API is accessible
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/');
      return response.status === 'healthy';
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }

  /**
   * Get available game types
   */
  async getGameTypes() {
    try {
      const response = await this.client.get('/games/types');
      return response.game_types;
    } catch (error) {
      console.error('Failed to get game types:', error);
      throw new Error('Unable to load game types. Please check your connection.');
    }
  }

  /**
   * Create a new game
   * @param {string} gameType - Type of game (e.g., 'truth_or_dare')
   * @param {Array} playerNames - Array of player names
   * @param {number} questionCount - Number of questions
   * @param {Object} settings - Game-specific settings
   */
  async createGame(gameType, playerNames, questionCount = 15, settings = {}) {
    try {
      const response = await this.client.post('/games', {
        game_type: gameType,
        player_names: playerNames,
        question_count: questionCount,
        settings: settings,
      });

      this.currentGameId = response.game_id;
      return response;
    } catch (error) {
      console.error('Failed to create game:', error);
      throw new Error('Unable to create game. Please try again.');
    }
  }

  /**
   * Start a game
   * @param {string} gameId - Game ID (optional, uses current game if not provided)
   */
  async startGame(gameId = null) {
    const id = gameId || this.currentGameId;
    if (!id) {
      throw new Error('No game ID provided');
    }

    try {
      const response = await this.client.post(`/games/${id}/start`);
      return response;
    } catch (error) {
      console.error('Failed to start game:', error);
      throw new Error('Unable to start game. Please try again.');
    }
  }

  /**
   * Get current question
   * @param {string} gameId - Game ID (optional, uses current game if not provided)
   */
  async getCurrentQuestion(gameId = null) {
    const id = gameId || this.currentGameId;
    if (!id) {
      throw new Error('No game ID provided');
    }

    try {
      const response = await this.client.get(`/games/${id}/question`);
      return response;
    } catch (error) {
      console.error('Failed to get current question:', error);
      throw new Error('Unable to load question. Please try again.');
    }
  }

  /**
   * Submit answer for current question
   * @param {boolean} completed - Whether the question was completed or skipped
   * @param {string} gameId - Game ID (optional, uses current game if not provided)
   */
  async submitAnswer(completed, gameId = null) {
    const id = gameId || this.currentGameId;
    if (!id) {
      throw new Error('No game ID provided');
    }

    try {
      const response = await this.client.post(`/games/${id}/answer`, {
        completed: completed,
      });
      return response;
    } catch (error) {
      console.error('Failed to submit answer:', error);
      throw new Error('Unable to submit answer. Please try again.');
    }
  }

  /**
   * Get game status
   * @param {string} gameId - Game ID (optional, uses current game if not provided)
   */
  async getGameStatus(gameId = null) {
    const id = gameId || this.currentGameId;
    if (!id) {
      throw new Error('No game ID provided');
    }

    try {
      const response = await this.client.get(`/games/${id}/status`);
      return response;
    } catch (error) {
      console.error('Failed to get game status:', error);
      throw new Error('Unable to load game status. Please try again.');
    }
  }

  /**
   * End a game
   * @param {string} gameId - Game ID (optional, uses current game if not provided)
   */
  async endGame(gameId = null) {
    const id = gameId || this.currentGameId;
    if (!id) {
      throw new Error('No game ID provided');
    }

    try {
      const response = await this.client.delete(`/games/${id}`);
      if (id === this.currentGameId) {
        this.currentGameId = null;
      }
      return response;
    } catch (error) {
      console.error('Failed to end game:', error);
      throw new Error('Unable to end game. Please try again.');
    }
  }

  /**
   * List all active games
   */
  async listActiveGames() {
    try {
      const response = await this.client.get('/games');
      return response.active_games;
    } catch (error) {
      console.error('Failed to list active games:', error);
      throw new Error('Unable to load active games. Please try again.');
    }
  }

  /**
   * Get database statistics
   */
  async getStats() {
    try {
      const response = await this.client.get('/stats');
      return response;
    } catch (error) {
      console.error('Failed to get stats:', error);
      throw new Error('Unable to load statistics. Please try again.');
    }
  }

  /**
   * Get available themes
   */
  async getThemes() {
    try {
      const response = await this.client.get('/themes');
      return response.themes;
    } catch (error) {
      console.error('Failed to get themes:', error);
      throw new Error('Unable to load themes. Please try again.');
    }
  }

  /**
   * Set current game ID
   * @param {string} gameId - Game ID to set as current
   */
  setCurrentGame(gameId) {
    this.currentGameId = gameId;
  }

  /**
   * Get current game ID
   */
  getCurrentGameId() {
    return this.currentGameId;
  }

  /**
   * Clear current game
   */
  clearCurrentGame() {
    this.currentGameId = null;
  }
}

/**
 * Game Session Manager
 * Provides higher-level game management with state tracking
 */
class GameSession {
  constructor(api = null) {
    this.api = api || new GameAPI();
    this.gameState = {
      gameId: null,
      gameType: null,
      players: [],
      currentPlayer: null,
      questionNumber: 0,
      totalQuestions: 0,
      progress: 0,
      started: false,
      finished: false,
      settings: {},
    };
    this.listeners = [];
  }

  /**
   * Add state change listener
   * @param {Function} listener - Function to call when state changes
   */
  addListener(listener) {
    this.listeners.push(listener);
  }

  /**
   * Remove state change listener
   * @param {Function} listener - Function to remove
   */
  removeListener(listener) {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  /**
   * Notify all listeners of state change
   */
  notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.gameState);
      } catch (error) {
        console.error('Error in state listener:', error);
      }
    });
  }

  /**
   * Update game state
   * @param {Object} updates - State updates to apply
   */
  updateState(updates) {
    this.gameState = { ...this.gameState, ...updates };
    this.notifyListeners();
  }

  /**
   * Create and start a new game session
   */
  async createGame(gameType, playerNames, questionCount = 15, settings = {}) {
    try {
      // Create game
      const createResponse = await this.api.createGame(gameType, playerNames, questionCount, settings);
      
      this.updateState({
        gameId: createResponse.game_id,
        gameType: gameType,
        players: playerNames,
        totalQuestions: questionCount,
        settings: settings,
        started: false,
        finished: false,
      });

      // Start game
      await this.api.startGame();
      
      // Get first question
      const questionData = await this.api.getCurrentQuestion();
      
      this.updateState({
        started: true,
        currentPlayer: questionData.current_player,
        questionNumber: questionData.question_number,
        progress: questionData.progress_percentage,
        finished: questionData.finished,
      });

      return questionData;
    } catch (error) {
      console.error('Failed to create game session:', error);
      throw error;
    }
  }

  /**
   * Get current question
   */
  async getCurrentQuestion() {
    try {
      const questionData = await this.api.getCurrentQuestion();
      
      this.updateState({
        currentPlayer: questionData.current_player,
        questionNumber: questionData.question_number,
        progress: questionData.progress_percentage,
        finished: questionData.finished,
      });

      return questionData;
    } catch (error) {
      console.error('Failed to get current question:', error);
      throw error;
    }
  }

  /**
   * Submit answer and get next question
   */
  async submitAnswer(completed) {
    try {
      const result = await this.api.submitAnswer(completed);
      
      if (result.session_complete) {
        this.updateState({ finished: true });
        return { finished: true, result };
      } else {
        // Get next question
        const questionData = await this.getCurrentQuestion();
        return { finished: false, questionData };
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
      throw error;
    }
  }

  /**
   * End current game session
   */
  async endGame() {
    try {
      const result = await this.api.endGame();
      
      this.updateState({
        gameId: null,
        started: false,
        finished: true,
      });

      return result;
    } catch (error) {
      console.error('Failed to end game:', error);
      throw error;
    }
  }

  /**
   * Get current game state
   */
  getState() {
    return { ...this.gameState };
  }

  /**
   * Reset session state
   */
  reset() {
    this.gameState = {
      gameId: null,
      gameType: null,
      players: [],
      currentPlayer: null,
      questionNumber: 0,
      totalQuestions: 0,
      progress: 0,
      started: false,
      finished: false,
      settings: {},
    };
    this.api.clearCurrentGame();
    this.notifyListeners();
  }
}

// Export classes and create default instances
export { GameAPI, GameSession, API_CONFIG };

// Default instances for easy use
export const gameAPI = new GameAPI();
export const gameSession = new GameSession(gameAPI);

export default GameAPI;
