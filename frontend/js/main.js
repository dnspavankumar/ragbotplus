// ===== MAIN APPLICATION MODULE =====

class GmailRagApplication {
    constructor() {
        this.currentPage = 'chat';
        this.isInitialized = false;
        this.modules = {};
        
        this.elements = {
            navLinks: document.querySelectorAll('.nav-link'),
            pages: document.querySelectorAll('.page'),
            pageTitle: document.getElementById('pageTitle'),
            refreshBtn: document.getElementById('refreshBtn'),
            settingsBtn: document.getElementById('settingsBtn'),
            appVersion: document.getElementById('appVersion')
        };
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Show loading
            showLoading('Initializing Gmail RAG Assistant...');
            
            // Set up core functionality
            this.setupEventListeners();
            this.setupKeyboardShortcuts();
            this.loadAppVersion();
            
            // Initialize modules
            await this.initializeModules();
            
            // Set up inter-module communication
            this.setupModuleCommunication();
            
            // Check backend connectivity
            await this.checkBackendConnection();
            
            // Load user preferences
            this.loadUserPreferences();
            
            // Show initial page
            this.showPage(this.currentPage);
            
            this.isInitialized = true;
            
            // Show welcome notification
            setTimeout(() => {
                showNotification('Welcome to Gmail RAG Assistant! 🚀', 'success', 4000);
            }, 1000);
            
        } catch (error) {
            console.error('Application initialization error:', error);
            showNotification('Failed to initialize application. Please refresh the page.', 'error', 8000);
        } finally {
            hideLoading();
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Navigation links
        this.elements.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                if (page) {
                    this.navigateToPage(page);
                }
            });
        });
        
        // Refresh button
        this.elements.refreshBtn.addEventListener('click', () => this.refreshCurrentPage());
        
        // Settings button (secondary way to access settings)
        this.elements.settingsBtn.addEventListener('click', () => this.navigateToPage('settings'));
        
        // Handle Electron navigation events
        if (window.electronAPI) {
            window.electronAPI.onNavigateTo((event, page) => {
                this.navigateToPage(page);
            });
        }
        
        // Handle window focus/blur
        window.addEventListener('focus', () => this.handleWindowFocus());
        window.addEventListener('blur', () => this.handleWindowBlur());
        
        // Handle online/offline events
        window.addEventListener('online', () => this.handleOnlineStatusChange(true));
        window.addEventListener('offline', () => this.handleOnlineStatusChange(false));
    }

    /**
     * Set up keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + number for page navigation
            if ((e.ctrlKey || e.metaKey) && !e.shiftKey && !e.altKey) {
                switch (e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToPage('chat');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToPage('emails');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateToPage('settings');
                        break;
                    case ',':
                        e.preventDefault();
                        this.navigateToPage('settings');
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshCurrentPage();
                        break;
                }
            }
            
            // Escape key to close modals or clear search
            if (e.key === 'Escape') {
                this.handleEscapeKey();
            }
        });
    }

    /**
     * Load app version
     */
    async loadAppVersion() {
        try {
            if (window.electronAPI) {
                const version = await window.electronAPI.getAppVersion();
                if (this.elements.appVersion) {
                    this.elements.appVersion.textContent = `v${version}`;
                }
            }
        } catch (error) {
            console.error('Error loading app version:', error);
        }
    }

    /**
     * Initialize all modules
     */
    async initializeModules() {
        // Modules are already initialized in their respective files
        // Here we just store references for inter-module communication
        this.modules = {
            chat: window.chatInterface,
            email: window.emailManagement,
            settings: window.settingsInterface,
            connection: connectionManager,
            api: api
        };
    }

    /**
     * Set up communication between modules
     */
    setupModuleCommunication() {
        // Listen for events from modules
        window.eventEmitter.on('navigate-to-chat', (question) => {
            this.navigateToPage('chat');
            if (question && this.modules.chat) {
                // Set the question in the chat input
                setTimeout(() => {
                    const input = document.getElementById('messageInput');
                    if (input) {
                        input.value = question;
                        input.dispatchEvent(new Event('input'));
                        // Optionally auto-send the message
                        // this.modules.chat.handleSendMessage();
                    }
                }, 100);
            }
        });
        
        // Connection status changes
        window.eventEmitter.on('connection-changed', (isOnline) => {
            this.handleConnectionStatusChange(isOnline);
        });
        
        // Settings changes
        window.eventEmitter.on('settings-changed', (settings) => {
            this.handleSettingsChange(settings);
        });
    }

    /**
     * Check backend connection
     */
    async checkBackendConnection() {
        try {
            const isHealthy = await api.healthCheck();
            if (!isHealthy) {
                throw new Error('Backend health check failed');
            }
            
            showNotification('Connected to backend successfully', 'success', 3000);
        } catch (error) {
            console.error('Backend connection error:', error);
            showNotification('Backend connection failed. Some features may not work.', 'warning', 6000);
        }
    }

    /**
     * Load user preferences
     */
    loadUserPreferences() {
        const preferences = storage.get('userPreferences', {});
        
        // Apply saved preferences
        if (preferences.lastPage && ['chat', 'emails', 'settings'].includes(preferences.lastPage)) {
            this.currentPage = preferences.lastPage;
        }
        
        // Apply theme
        const theme = storage.get('theme', 'dark');
        document.documentElement.setAttribute('data-theme', theme);
    }

    /**
     * Save user preferences
     */
    saveUserPreferences() {
        const preferences = {
            lastPage: this.currentPage,
            timestamp: new Date().toISOString()
        };
        
        storage.set('userPreferences', preferences);
    }

    /**
     * Navigate to a specific page
     * @param {string} page - Page name to navigate to
     */
    navigateToPage(page) {
        if (!['chat', 'emails', 'settings'].includes(page)) {
            console.error('Invalid page:', page);
            return;
        }
        
        if (this.currentPage === page) {
            return; // Already on this page
        }
        
        // Update navigation state
        this.updateNavigation(page);
        
        // Show the page
        this.showPage(page);
        
        // Update current page
        this.currentPage = page;
        
        // Save preference
        this.saveUserPreferences();
        
        // Emit navigation event
        window.eventEmitter.emit('page-changed', page);
        
        // Page-specific actions
        this.handlePageSpecificActions(page);
    }

    /**
     * Update navigation UI
     * @param {string} activePage - Page to mark as active
     */
    updateNavigation(activePage) {
        // Update nav links
        this.elements.navLinks.forEach(link => {
            const isActive = link.dataset.page === activePage;
            link.classList.toggle('active', isActive);
        });
        
        // Update page title
        const pageTitles = {
            chat: 'Chat',
            emails: 'Email Management',
            settings: 'Settings'
        };
        
        if (this.elements.pageTitle) {
            this.elements.pageTitle.textContent = pageTitles[activePage] || 'Gmail RAG Assistant';
        }
    }

    /**
     * Show a specific page
     * @param {string} page - Page to show
     */
    showPage(page) {
        // Hide all pages
        this.elements.pages.forEach(pageEl => {
            pageEl.classList.remove('active');
        });
        
        // Show target page
        const targetPage = document.getElementById(`${page}Page`);
        if (targetPage) {
            targetPage.classList.add('active');
            
            // Add animation class
            targetPage.classList.add('animate-fade-in');
            setTimeout(() => {
                targetPage.classList.remove('animate-fade-in');
            }, 300);
        }
    }

    /**
     * Handle page-specific actions
     * @param {string} page - Page that was navigated to
     */
    handlePageSpecificActions(page) {
        switch (page) {
            case 'chat':
                // Focus chat input
                setTimeout(() => {
                    const input = document.getElementById('messageInput');
                    if (input) input.focus();
                }, 100);
                break;
                
            case 'emails':
                // Refresh email status
                if (this.modules.email) {
                    this.modules.email.loadEmailStatus();
                }
                break;
                
            case 'settings':
                // Reload configuration
                if (this.modules.settings) {
                    this.modules.settings.loadConfiguration();
                }
                break;
        }
    }

    /**
     * Refresh current page
     */
    refreshCurrentPage() {
        showNotification('Refreshing...', 'info', 1000);
        
        switch (this.currentPage) {
            case 'chat':
                // Reload chat interface
                if (this.modules.chat) {
                    this.modules.chat.loadChatHistory();
                }
                break;
                
            case 'emails':
                // Reload email status
                if (this.modules.email) {
                    this.modules.email.loadEmailStatus();
                }
                break;
                
            case 'settings':
                // Reload configuration
                if (this.modules.settings) {
                    this.modules.settings.loadConfiguration();
                }
                break;
        }
    }

    /**
     * Handle escape key press
     */
    handleEscapeKey() {
        // Close any open modals
        const modals = document.querySelectorAll('.email-modal-overlay, .help-modal-overlay');
        modals.forEach(modal => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        });
        
        // Clear search in email page
        if (this.currentPage === 'emails' && this.modules.email) {
            const searchContainer = document.getElementById('searchContainer');
            if (searchContainer && searchContainer.style.display !== 'none') {
                this.modules.email.toggleSearch();
            }
        }
    }

    /**
     * Handle window focus
     */
    handleWindowFocus() {
        // Check for updates when window regains focus
        if (this.isInitialized) {
            // Refresh current page data if it's been more than 5 minutes
            const lastRefresh = storage.get('lastRefresh', 0);
            const now = Date.now();
            
            if (now - lastRefresh > 5 * 60 * 1000) { // 5 minutes
                this.refreshCurrentPage();
                storage.set('lastRefresh', now);
            }
        }
    }

    /**
     * Handle window blur
     */
    handleWindowBlur() {
        // Save any pending data when window loses focus
        this.saveUserPreferences();
    }

    /**
     * Handle online/offline status changes
     * @param {boolean} isOnline - Current online status
     */
    handleOnlineStatusChange(isOnline) {
        if (isOnline) {
            showNotification('Connection restored', 'success', 3000);
            // Refresh current page when coming back online
            setTimeout(() => this.refreshCurrentPage(), 1000);
        } else {
            showNotification('Connection lost', 'warning', 5000);
        }
    }

    /**
     * Handle connection status changes from connection manager
     * @param {boolean} isOnline - Current connection status
     */
    handleConnectionStatusChange(isOnline) {
        // Update UI elements based on connection status
        const onlineElements = document.querySelectorAll('[data-requires-connection]');
        onlineElements.forEach(element => {
            element.disabled = !isOnline;
        });
    }

    /**
     * Handle settings changes
     * @param {Object} settings - Changed settings
     */
    handleSettingsChange(settings) {
        if (settings.theme) {
            document.documentElement.setAttribute('data-theme', settings.theme);
        }
        
        // Refresh modules that depend on settings
        if (settings.groqApiKey && this.modules.chat) {
            showNotification('API key updated. New conversations will use the updated key.', 'info', 4000);
        }
    }

    /**
     * Show application info
     */
    showAppInfo() {
        const info = {
            name: 'Gmail RAG Assistant',
            version: this.elements.appVersion?.textContent || 'v1.0.0',
            description: 'Modern AI-powered email assistant with Retrieval-Augmented Generation',
            features: [
                'Natural language email querying',
                'Vector-based email search',
                'AI-powered responses with Groq',
                'Voice input and text-to-speech',
                'Modern Electron interface',
                'Secure local data processing'
            ]
        };
        
        let message = `${info.name} ${info.version}\n\n${info.description}\n\nKey Features:\n`;
        message += info.features.map(feature => `• ${feature}`).join('\n');
        
        if (window.electronAPI) {
            window.electronAPI.showInfoDialog('About Gmail RAG Assistant', message);
        } else {
            alert(message);
        }
    }

    /**
     * Handle critical errors
     * @param {Error} error - The error that occurred
     * @param {string} context - Context where error occurred
     */
    handleCriticalError(error, context) {
        console.error(`Critical error in ${context}:`, error);
        
        const message = `A critical error occurred in ${context}. The application may not function correctly. Please restart the application.`;
        
        if (window.electronAPI) {
            window.electronAPI.showErrorDialog('Critical Error', message);
        } else {
            showNotification(message, 'error', 10000);
        }
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        // Save current state
        this.saveUserPreferences();
        
        // Stop any running processes
        if (this.modules.connection) {
            this.modules.connection.stopHealthCheck();
        }
        
        // Clear timeouts and intervals
        // (Specific modules handle their own cleanup)
    }
}

// Global error handlers
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    if (window.app) {
        window.app.handleCriticalError(event.error, 'Global Error Handler');
    }
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    if (window.app) {
        window.app.handleCriticalError(event.reason, 'Unhandled Promise Rejection');
    }
    event.preventDefault();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.cleanup();
    }
});

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GmailRagApplication();
});

// Export for debugging purposes
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GmailRagApplication;
}

// Global helper functions
window.navigateToPage = (page) => {
    if (window.app) {
        window.app.navigateToPage(page);
    }
};

window.refreshPage = () => {
    if (window.app) {
        window.app.refreshCurrentPage();
    }
};

window.showAppInfo = () => {
    if (window.app) {
        window.app.showAppInfo();
    }
};