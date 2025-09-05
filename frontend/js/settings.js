// ===== SETTINGS INTERFACE MODULE =====

class SettingsInterface {
    constructor() {
        this.currentConfig = {};
        this.hasUnsavedChanges = false;
        
        this.elements = {
            groqApiKey: document.getElementById('groqApiKey'),
            toggleApiKey: document.getElementById('toggleApiKey'),
            credentialsStatus: document.getElementById('credentialsStatus'),
            tokenStatus: document.getElementById('tokenStatus'),
            saveSettingsBtn: document.getElementById('saveSettingsBtn'),
            resetSettingsBtn: document.getElementById('resetSettingsBtn'),
            themeOptions: document.querySelectorAll('.theme-option')
        };
        
        this.init();
    }

    /**
     * Initialize settings interface
     */
    init() {
        this.setupEventListeners();
        this.loadConfiguration();
        this.setupFormValidation();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // API key toggle visibility
        this.elements.toggleApiKey.addEventListener('click', () => this.toggleApiKeyVisibility());
        
        // API key input changes
        this.elements.groqApiKey.addEventListener('input', () => this.handleConfigChange());
        
        // Save settings
        this.elements.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        
        // Reset settings
        this.elements.resetSettingsBtn.addEventListener('click', () => this.resetSettings());
        
        // Theme selection
        this.elements.themeOptions.forEach(option => {
            option.addEventListener('click', () => this.selectTheme(option.dataset.theme));
        });
        
        // Prevent form submission on enter
        this.elements.groqApiKey.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.saveSettings();
            }
        });
        
        // Warn about unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
                return '';
            }
        });
        
        // Connection status listener
        connectionManager.addListener((isOnline) => this.handleConnectionChange(isOnline));
    }

    /**
     * Load current configuration from backend
     */
    async loadConfiguration() {
        try {
            showLoading('Loading configuration...');
            
            const [config, systemStatus] = await Promise.all([
                api.getConfig(),
                api.getSystemStatus()
            ]);
            
            this.currentConfig = config.config || {};
            this.updateConfigurationDisplay(systemStatus.config_status || {});
            this.updateFormFields();
            
        } catch (error) {
            console.error('Error loading configuration:', error);
            APIErrorHandler.handle(error, 'Configuration Loading');
            
            // Set default values on error
            this.updateConfigurationDisplay({
                credentials_json: false,
                token_json: false,
                groq_api_key: false
            });
        } finally {
            hideLoading();
        }
    }

    /**
     * Update configuration display
     * @param {Object} configStatus - Configuration status from backend
     */
    updateConfigurationDisplay(configStatus) {
        // Update credentials status
        this.updateStatusBadge(
            this.elements.credentialsStatus,
            configStatus.credentials_json,
            'Configured',
            'Not Set'
        );
        
        // Update token status
        this.updateStatusBadge(
            this.elements.tokenStatus,
            configStatus.token_json,
            'Valid',
            'Not Set'
        );
        
        // Update API key indication (don't show actual key)
        if (configStatus.groq_api_key) {
            this.elements.groqApiKey.placeholder = 'API key is configured';
        } else {
            this.elements.groqApiKey.placeholder = 'Enter your Groq API key';
        }
    }

    /**
     * Update a status badge
     * @param {HTMLElement} element - Badge element
     * @param {boolean} isValid - Whether the status is valid
     * @param {string} validText - Text to show when valid
     * @param {string} invalidText - Text to show when invalid
     */
    updateStatusBadge(element, isValid, validText, invalidText) {
        if (!element) return;
        
        element.textContent = isValid ? validText : invalidText;
        element.className = `status-badge ${isValid ? 'success' : 'error'}`;
    }

    /**
     * Update form fields with current configuration
     */
    updateFormFields() {
        // Don't populate API key field for security reasons
        // Just indicate if it's set
        if (this.currentConfig.groq_api_key_set) {
            this.elements.groqApiKey.placeholder = 'API key is configured (enter new key to change)';
        }
        
        // Load theme preference from local storage
        const savedTheme = storage.get('theme', 'dark');
        this.selectTheme(savedTheme);
    }

    /**
     * Set up form validation
     */
    setupFormValidation() {
        // Real-time API key validation
        this.elements.groqApiKey.addEventListener('input', () => {
            const apiKey = this.elements.groqApiKey.value.trim();
            this.validateApiKey(apiKey);
        });
        
        // API key formatting
        this.elements.groqApiKey.addEventListener('paste', (e) => {
            setTimeout(() => {
                const apiKey = this.elements.groqApiKey.value.trim();
                this.elements.groqApiKey.value = apiKey;
                this.validateApiKey(apiKey);
            }, 0);
        });
    }

    /**
     * Validate API key format
     * @param {string} apiKey - API key to validate
     * @returns {boolean} True if valid format
     */
    validateApiKey(apiKey) {
        if (!apiKey) {
            this.setApiKeyValidation(null, '');
            return false;
        }
        
        // Basic Groq API key format validation
        // Groq API keys typically start with 'gsk_' and are followed by alphanumeric characters
        const groqKeyPattern = /^gsk_[a-zA-Z0-9]+$/;
        
        if (groqKeyPattern.test(apiKey)) {
            this.setApiKeyValidation(true, 'Valid API key format');
            return true;
        } else {
            this.setApiKeyValidation(false, 'Invalid API key format. Groq keys start with "gsk_"');
            return false;
        }
    }

    /**
     * Set API key validation state
     * @param {boolean|null} isValid - Validation state (null for neutral)
     * @param {string} message - Validation message
     */
    setApiKeyValidation(isValid, message) {
        const input = this.elements.groqApiKey;
        const existingHelper = input.parentNode.querySelector('.validation-message');
        
        // Remove existing validation message
        if (existingHelper) {
            existingHelper.remove();
        }
        
        // Reset input styling
        input.style.borderColor = '';
        
        if (isValid !== null && message) {
            // Add validation message
            const helperEl = document.createElement('small');
            helperEl.className = `validation-message ${isValid ? 'success' : 'error'}`;
            helperEl.textContent = message;
            helperEl.style.color = isValid ? 'var(--color-success)' : 'var(--color-danger)';
            helperEl.style.marginTop = 'var(--spacing-xs)';
            helperEl.style.display = 'block';
            
            input.parentNode.appendChild(helperEl);
            
            // Update input border color
            input.style.borderColor = isValid ? 'var(--color-success)' : 'var(--color-danger)';
        }
    }

    /**
     * Toggle API key visibility
     */
    toggleApiKeyVisibility() {
        const input = this.elements.groqApiKey;
        const button = this.elements.toggleApiKey;
        
        if (input.type === 'password') {
            input.type = 'text';
            button.innerHTML = '<i class="fas fa-eye-slash"></i>';
            button.title = 'Hide API key';
        } else {
            input.type = 'password';
            button.innerHTML = '<i class="fas fa-eye"></i>';
            button.title = 'Show API key';
        }
    }

    /**
     * Handle configuration changes
     */
    handleConfigChange() {
        this.hasUnsavedChanges = true;
        this.updateSaveButtonState();
    }

    /**
     * Update save button state
     */
    updateSaveButtonState() {
        const hasChanges = this.hasUnsavedChanges;
        const isOnline = connectionManager.getStatus();
        
        this.elements.saveSettingsBtn.disabled = !hasChanges || !isOnline;
        
        if (hasChanges && isOnline) {
            this.elements.saveSettingsBtn.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        } else if (!isOnline) {
            this.elements.saveSettingsBtn.innerHTML = '<i class="fas fa-save"></i> No Connection';
        } else {
            this.elements.saveSettingsBtn.innerHTML = '<i class="fas fa-save"></i> Save Settings';
        }
    }

    /**
     * Select theme
     * @param {string} theme - Theme name
     */
    selectTheme(theme) {
        // Update theme options
        this.elements.themeOptions.forEach(option => {
            option.classList.toggle('active', option.dataset.theme === theme);
        });
        
        // Apply theme (for now just save preference)
        storage.set('theme', theme);
        
        // Apply theme to document
        this.applyTheme(theme);
        
        showNotification(`Switched to ${theme} theme`, 'success', 2000);
    }

    /**
     * Apply theme to document
     * @param {string} theme - Theme name
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // For now, we only have dark theme implemented
        // Light theme would require additional CSS variables
        if (theme === 'light') {
            // TODO: Implement light theme
            showNotification('Light theme coming soon! Using dark theme for now.', 'info', 4000);
        }
    }

    /**
     * Save settings to backend
     */
    async saveSettings() {
        if (!this.hasUnsavedChanges) {
            showNotification('No changes to save', 'info');
            return;
        }
        
        if (!connectionManager.getStatus()) {
            showNotification('No connection. Cannot save settings.', 'warning');
            return;
        }
        
        const apiKey = this.elements.groqApiKey.value.trim();
        
        // Validate API key if provided
        if (apiKey && !this.validateApiKey(apiKey)) {
            showNotification('Please enter a valid API key', 'error');
            return;
        }
        
        try {
            showLoading('Saving settings...');
            this.elements.saveSettingsBtn.disabled = true;
            
            const configUpdates = {};
            
            // Add API key if provided
            if (apiKey) {
                configUpdates.groq_api_key = apiKey;
            }
            
            // Save configuration
            if (Object.keys(configUpdates).length > 0) {
                await api.updateConfig(configUpdates);
            }
            
            // Clear API key field for security
            this.elements.groqApiKey.value = '';
            this.elements.groqApiKey.placeholder = 'API key saved successfully';
            
            // Mark as saved
            this.hasUnsavedChanges = false;
            this.updateSaveButtonState();
            
            // Reload configuration to get updated status
            setTimeout(() => this.loadConfiguration(), 1000);
            
            showNotification('Settings saved successfully', 'success');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            APIErrorHandler.handle(error, 'Settings Save');
        } finally {
            hideLoading();
            this.elements.saveSettingsBtn.disabled = false;
        }
    }

    /**
     * Reset settings to default
     */
    resetSettings() {
        const message = 'Are you sure you want to reset all settings to default? This will:\n\n' +
                       '• Clear your API key\n' +
                       '• Reset theme to dark\n' +
                       '• Clear all preferences\n\n' +
                       'This action cannot be undone.';
        
        if (!confirm(message)) {
            return;
        }
        
        try {
            // Clear form fields
            this.elements.groqApiKey.value = '';
            this.elements.groqApiKey.placeholder = 'Enter your Groq API key';
            
            // Reset theme
            this.selectTheme('dark');
            
            // Clear local storage
            storage.remove('theme');
            storage.remove('chatHistory');
            storage.remove('userPreferences');
            
            // Mark as changed
            this.hasUnsavedChanges = true;
            this.updateSaveButtonState();
            
            showNotification('Settings reset to default. Click "Save Settings" to apply.', 'info', 5000);
            
        } catch (error) {
            console.error('Error resetting settings:', error);
            showNotification('Error resetting settings', 'error');
        }
    }

    /**
     * Handle connection status changes
     * @param {boolean} isOnline - Current connection status
     */
    handleConnectionChange(isOnline) {
        this.updateSaveButtonState();
        
        if (!isOnline) {
            showNotification('Connection lost. Settings cannot be saved until connection is restored.', 'warning', 5000);
        } else {
            // Reload configuration when connection is restored
            this.loadConfiguration();
        }
    }

    /**
     * Export settings for backup
     */
    exportSettings() {
        const settings = {
            timestamp: new Date().toISOString(),
            theme: storage.get('theme', 'dark'),
            userPreferences: storage.get('userPreferences', {}),
            appVersion: '1.0.0'
        };
        
        const dataStr = JSON.stringify(settings, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `gmail-rag-settings-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showNotification('Settings exported successfully', 'success', 2000);
    }

    /**
     * Import settings from backup
     * @param {File} file - Settings file to import
     */
    async importSettings(file) {
        try {
            const text = await file.text();
            const settings = JSON.parse(text);
            
            // Validate settings structure
            if (!settings.timestamp || !settings.theme) {
                throw new Error('Invalid settings file format');
            }
            
            // Apply imported settings
            if (settings.theme) {
                this.selectTheme(settings.theme);
            }
            
            if (settings.userPreferences) {
                storage.set('userPreferences', settings.userPreferences);
            }
            
            showNotification('Settings imported successfully', 'success', 3000);
            
        } catch (error) {
            console.error('Error importing settings:', error);
            showNotification('Error importing settings: ' + error.message, 'error');
        }
    }

    /**
     * Open API key help
     */
    openApiKeyHelp() {
        const helpModal = document.createElement('div');
        helpModal.className = 'help-modal-overlay';
        helpModal.innerHTML = `
            <div class="help-modal">
                <div class="help-modal-header">
                    <h3><i class="fas fa-question-circle"></i> Groq API Key Help</h3>
                    <button class="btn btn-icon close-help">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="help-modal-content">
                    <h4>What is a Groq API Key?</h4>
                    <p>The Groq API key is required to access Groq's fast AI language models for processing your email queries and generating intelligent responses.</p>
                    
                    <h4>How to get your API key:</h4>
                    <ol>
                        <li>Visit <a href="https://console.groq.com" target="_blank">console.groq.com</a></li>
                        <li>Sign up for a free account or log in</li>
                        <li>Navigate to the API Keys section</li>
                        <li>Create a new API key</li>
                        <li>Copy the key and paste it here</li>
                    </ol>
                    
                    <h4>Security:</h4>
                    <ul>
                        <li>Your API key is stored securely on your local machine</li>
                        <li>Never share your API key with others</li>
                        <li>You can revoke and regenerate keys at any time</li>
                    </ul>
                    
                    <h4>Pricing:</h4>
                    <p>Groq offers generous free tier usage. Check their pricing page for current rates and limits.</p>
                </div>
                <div class="help-modal-actions">
                    <button class="btn btn-primary" onclick="window.open('https://console.groq.com/keys', '_blank')">
                        <i class="fas fa-external-link-alt"></i> Get API Key
                    </button>
                    <button class="btn btn-secondary close-help">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(helpModal);
        
        // Add event listeners
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal || e.target.classList.contains('close-help')) {
                document.body.removeChild(helpModal);
            }
        });
        
        // Animate in
        setTimeout(() => {
            helpModal.classList.add('active');
        }, 10);
    }
}

// Add help modal styles
const helpModalStyles = `
    <style>
        .help-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .help-modal-overlay.active {
            opacity: 1;
        }
        
        .help-modal {
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            max-width: 600px;
            max-height: 80%;
            width: 90%;
            display: flex;
            flex-direction: column;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        
        .help-modal-overlay.active .help-modal {
            transform: scale(1);
        }
        
        .help-modal-header {
            padding: var(--spacing-lg);
            border-bottom: 1px solid var(--color-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .help-modal-content {
            flex: 1;
            padding: var(--spacing-lg);
            overflow-y: auto;
        }
        
        .help-modal-content h4 {
            color: var(--color-accent);
            margin: var(--spacing-lg) 0 var(--spacing-md) 0;
        }
        
        .help-modal-content h4:first-child {
            margin-top: 0;
        }
        
        .help-modal-content ol, .help-modal-content ul {
            margin-left: var(--spacing-lg);
            line-height: 1.6;
        }
        
        .help-modal-content li {
            margin-bottom: var(--spacing-sm);
        }
        
        .help-modal-content a {
            color: var(--color-accent);
            text-decoration: none;
        }
        
        .help-modal-content a:hover {
            text-decoration: underline;
        }
        
        .help-modal-actions {
            padding: var(--spacing-lg);
            border-top: 1px solid var(--color-border);
            display: flex;
            gap: var(--spacing-md);
            justify-content: flex-end;
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', helpModalStyles);

// Add help button to API key section
document.addEventListener('DOMContentLoaded', () => {
    const apiKeySection = document.querySelector('#groqApiKey').closest('.form-group');
    if (apiKeySection) {
        const helpText = apiKeySection.querySelector('.help-text');
        if (helpText) {
            helpText.innerHTML += ` <button type="button" class="btn-link" onclick="settingsInterface.openApiKeyHelp()" style="color: var(--color-accent); text-decoration: underline; background: none; border: none; cursor: pointer; padding: 0;">Need help?</button>`;
        }
    }
});

// Initialize settings interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.settingsInterface = new SettingsInterface();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SettingsInterface;
}