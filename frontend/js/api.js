// ===== API COMMUNICATION MODULE =====

class APIClient {
    constructor() {
        this.baseURL = 'http://localhost:5000';
        this.timeout = 30000; // 30 seconds timeout
        this.retryCount = 3;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Make an HTTP request with retry logic
     * @param {string} method - HTTP method
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Response data
     */
    async request(method, endpoint, data = null, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        if (data && method.toLowerCase() !== 'get') {
            config.body = JSON.stringify(data);
        }

        let lastError;
        for (let attempt = 1; attempt <= this.retryCount; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                
                config.signal = controller.signal;
                
                const response = await fetch(url, config);
                clearTimeout(timeoutId);
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
                }
                
                const result = await response.json();
                return result;
                
            } catch (error) {
                lastError = error;
                console.error(`API request attempt ${attempt} failed:`, error);
                
                // Don't retry on client errors (4xx) or abort errors
                if (error.name === 'AbortError' || 
                    (error.message.includes('HTTP 4') && !error.message.includes('HTTP 408'))) {
                    throw error;
                }
                
                // Wait before retrying (except on last attempt)
                if (attempt < this.retryCount) {
                    await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
                }
            }
        }
        
        throw lastError;
    }

    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async get(endpoint, options = {}) {
        return this.request('GET', endpoint, null, options);
    }

    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async post(endpoint, data = null, options = {}) {
        return this.request('POST', endpoint, data, options);
    }

    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request data
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async put(endpoint, data = null, options = {}) {
        return this.request('PUT', endpoint, data, options);
    }

    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async delete(endpoint, options = {}) {
        return this.request('DELETE', endpoint, null, options);
    }

    /**
     * Health check
     * @returns {Promise<boolean>} True if server is healthy
     */
    async healthCheck() {
        try {
            const response = await this.get('/api/health');
            return response.status === 'healthy';
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Send chat message
     * @param {string} message - User message
     * @param {string} sessionId - Session ID (optional)
     * @returns {Promise<Object>} Response with AI reply and session ID
     */
    async sendChatMessage(message, sessionId = null) {
        const data = { message };
        if (sessionId) {
            data.session_id = sessionId;
        }
        
        return this.post('/api/chat/message', data);
    }

    /**
     * Delete chat session
     * @param {string} sessionId - Session ID to delete
     * @returns {Promise<Object>} Response
     */
    async deleteChatSession(sessionId) {
        return this.delete(`/api/chat/session/${sessionId}`);
    }

    /**
     * Get chat sessions
     * @returns {Promise<Object>} List of chat sessions
     */
    async getChatSessions() {
        return this.get('/api/chat/sessions');
    }

    /**
     * Load emails from Gmail
     * @returns {Promise<Object>} Response
     */
    async loadEmails() {
        return this.post('/api/emails/load');
    }

    /**
     * Search emails
     * @param {string} query - Search query
     * @param {number} k - Number of results to return
     * @returns {Promise<Object>} Search results
     */
    async searchEmails(query, k = 25) {
        return this.post('/api/emails/search', { query, k });
    }

    /**
     * Get email status
     * @returns {Promise<Object>} Email status information
     */
    async getEmailStatus() {
        return this.get('/api/emails/status');
    }

    /**
     * Get system status
     * @returns {Promise<Object>} System status and configuration
     */
    async getSystemStatus() {
        return this.get('/api/system/status');
    }

    /**
     * Get configuration
     * @returns {Promise<Object>} Current configuration
     */
    async getConfig() {
        return this.get('/api/config');
    }

    /**
     * Update configuration
     * @param {Object} config - Configuration to update
     * @returns {Promise<Object>} Response
     */
    async updateConfig(config) {
        return this.post('/api/config', config);
    }
}

// Connection manager for handling connectivity
class ConnectionManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.checkInterval = null;
        this.checkFrequency = 5000; // 5 seconds
        this.listeners = [];
        
        // Listen for online/offline events
        window.addEventListener('online', () => this.setOnlineStatus(true));
        window.addEventListener('offline', () => this.setOnlineStatus(false));
        
        // Start periodic health checks
        this.startHealthCheck();
    }

    /**
     * Set online status
     * @param {boolean} status - Online status
     */
    setOnlineStatus(status) {
        const wasOnline = this.isOnline;
        this.isOnline = status;
        
        if (wasOnline !== status) {
            this.notifyListeners(status);
            this.updateUI(status);
        }
    }

    /**
     * Add status change listener
     * @param {Function} callback - Callback function
     */
    addListener(callback) {
        this.listeners.push(callback);
    }

    /**
     * Remove status change listener
     * @param {Function} callback - Callback function to remove
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter(cb => cb !== callback);
    }

    /**
     * Notify all listeners of status change
     * @param {boolean} isOnline - Current online status
     */
    notifyListeners(isOnline) {
        this.listeners.forEach(callback => {
            try {
                callback(isOnline);
            } catch (error) {
                console.error('Error in connection status listener:', error);
            }
        });
    }

    /**
     * Update UI based on connection status
     * @param {boolean} isOnline - Current online status
     */
    updateUI(isOnline) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (statusDot) {
            statusDot.className = `status-dot ${isOnline ? 'connected' : 'disconnected'}`;
        }
        
        if (statusText) {
            statusText.textContent = isOnline ? 'Connected' : 'Disconnected';
        }
        
        // Show notification for status changes
        if (isOnline) {
            showNotification('Connection restored', 'success', 3000);
        } else {
            showNotification('Connection lost', 'warning', 5000);
        }
    }

    /**
     * Start periodic health checks
     */
    startHealthCheck() {
        if (this.checkInterval) return;
        
        this.checkInterval = setInterval(async () => {
            if (!navigator.onLine) {
                this.setOnlineStatus(false);
                return;
            }
            
            try {
                const isHealthy = await api.healthCheck();
                this.setOnlineStatus(isHealthy);
            } catch (error) {
                this.setOnlineStatus(false);
            }
        }, this.checkFrequency);
    }

    /**
     * Stop health checks
     */
    stopHealthCheck() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
    }

    /**
     * Get current connection status
     * @returns {boolean} True if online
     */
    getStatus() {
        return this.isOnline;
    }
}

// Error handler for API requests
class APIErrorHandler {
    /**
     * Handle API errors with user-friendly messages
     * @param {Error} error - The error to handle
     * @param {string} context - Context where the error occurred
     */
    static handle(error, context = '') {
        console.error(`API Error in ${context}:`, error);
        
        let message = 'An unexpected error occurred';
        let type = 'error';
        
        if (error.name === 'AbortError') {
            message = 'Request timed out. Please try again.';
            type = 'warning';
        } else if (error.message.includes('HTTP 401')) {
            message = 'Authentication failed. Please check your credentials.';
        } else if (error.message.includes('HTTP 403')) {
            message = 'Access denied. Insufficient permissions.';
        } else if (error.message.includes('HTTP 404')) {
            message = 'Service not found. Please check your connection.';
        } else if (error.message.includes('HTTP 429')) {
            message = 'Too many requests. Please wait and try again.';
            type = 'warning';
        } else if (error.message.includes('HTTP 500')) {
            message = 'Server error. Please try again later.';
        } else if (error.message.includes('NetworkError') || error.message.includes('Failed to fetch')) {
            message = 'Network connection failed. Please check your internet connection.';
            type = 'warning';
        } else if (error.message) {
            message = error.message;
        }
        
        showNotification(message, type, 6000);
        return { message, type };
    }
}

// Create global API client instance
const api = new APIClient();
const connectionManager = new ConnectionManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, ConnectionManager, APIErrorHandler };
}

// Global error handling
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    APIErrorHandler.handle(event.reason, 'Unhandled Promise');
    event.preventDefault();
});

window.addEventListener('error', (event) => {
    console.error('Unhandled error:', event.error);
    if (event.error instanceof Error) {
        APIErrorHandler.handle(event.error, 'Unhandled Error');
    }
});