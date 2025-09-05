const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App information
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Dialog methods
  showErrorDialog: (title, content) => ipcRenderer.invoke('show-error-dialog', title, content),
  showInfoDialog: (title, content) => ipcRenderer.invoke('show-info-dialog', title, content),
  
  // Navigation
  onNavigateTo: (callback) => ipcRenderer.on('navigate-to', callback),
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // System information
  platform: process.platform,
  
  // Environment
  isDev: process.env.NODE_ENV === 'development'
});

// Expose a safe HTTP client for backend communication
contextBridge.exposeInMainWorld('backendAPI', {
  // Backend server base URL
  baseURL: 'http://localhost:5000',
  
  // Make HTTP requests to Python backend
  request: async (method, endpoint, data = null) => {
    const url = `http://localhost:5000${endpoint}`;
    const options = {
      method: method.toUpperCase(),
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    if (data && method.toLowerCase() !== 'get') {
      options.body = JSON.stringify(data);
    }
    
    try {
      const response = await fetch(url, options);
      const responseData = await response.json();
      
      if (!response.ok) {
        throw new Error(responseData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      return responseData;
    } catch (error) {
      console.error('Backend API Error:', error);
      throw error;
    }
  },
  
  // Convenience methods for common operations
  get: (endpoint) => {
    return fetch(`http://localhost:5000${endpoint}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      });
  },
  
  post: (endpoint, data) => {
    return fetch(`http://localhost:5000${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      });
  }
});