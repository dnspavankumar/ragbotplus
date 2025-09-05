// ===== EMAIL MANAGEMENT MODULE =====

class EmailManagement {
    constructor() {
        this.isLoading = false;
        this.searchResults = [];
        this.emailStatus = null;
        
        this.elements = {
            loadEmailsBtn: document.getElementById('loadEmailsBtn'),
            searchEmailsBtn: document.getElementById('searchEmailsBtn'),
            searchContainer: document.getElementById('searchContainer'),
            emailSearchInput: document.getElementById('emailSearchInput'),
            executeSearchBtn: document.getElementById('executeSearchBtn'),
            emailStatus: document.getElementById('emailStatus'),
            emailStatusText: document.getElementById('emailStatusText'),
            lastUpdated: document.getElementById('lastUpdated'),
            searchResults: document.getElementById('searchResults'),
            resultsList: document.getElementById('resultsList')
        };
        
        this.init();
    }

    /**
     * Initialize email management interface
     */
    init() {
        this.setupEventListeners();
        this.loadEmailStatus();
        this.setupPeriodicStatusUpdate();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Load emails button
        this.elements.loadEmailsBtn.addEventListener('click', () => this.loadEmails());
        
        // Search toggle button
        this.elements.searchEmailsBtn.addEventListener('click', () => this.toggleSearch());
        
        // Execute search button
        this.elements.executeSearchBtn.addEventListener('click', () => this.executeSearch());
        
        // Search input enter key
        this.elements.emailSearchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.executeSearch();
            }
        });
        
        // Search input real-time validation
        this.elements.emailSearchInput.addEventListener('input', () => {
            const query = this.elements.emailSearchInput.value.trim();
            this.elements.executeSearchBtn.disabled = query.length === 0;
        });
        
        // Connection status listener
        connectionManager.addListener((isOnline) => this.handleConnectionChange(isOnline));
    }

    /**
     * Load email status from backend
     */
    async loadEmailStatus() {
        try {
            const status = await api.getEmailStatus();
            this.updateEmailStatus(status);
        } catch (error) {
            console.error('Error loading email status:', error);
            this.updateEmailStatus({
                status: 'error',
                last_checked: null
            });
        }
    }

    /**
     * Update email status display
     * @param {Object} status - Status object from backend
     */
    updateEmailStatus(status) {
        this.emailStatus = status;
        
        let statusText = 'Unknown';
        let statusClass = 'text-muted';
        
        switch (status.status) {
            case 'ready':
                statusText = 'Ready to load emails';
                statusClass = 'text-success';
                break;
            case 'processing':
                statusText = 'Loading emails in progress...';
                statusClass = 'text-warning';
                break;
            case 'error':
                statusText = 'Error loading emails';
                statusClass = 'text-danger';
                break;
        }
        
        this.elements.emailStatusText.textContent = statusText;
        this.elements.emailStatusText.className = statusClass;
        
        // Update last checked time
        if (status.last_checked) {
            const lastChecked = new Date(status.last_checked);
            this.elements.lastUpdated.textContent = formatDate(lastChecked);
        } else {
            this.elements.lastUpdated.textContent = 'Never';
        }
    }

    /**
     * Set up periodic status updates
     */
    setupPeriodicStatusUpdate() {
        // Check status every 30 seconds
        setInterval(() => {
            if (connectionManager.getStatus() && !this.isLoading) {
                this.loadEmailStatus();
            }
        }, 30000);
    }

    /**
     * Load emails from Gmail
     */
    async loadEmails() {
        if (this.isLoading) {
            showNotification('Email loading already in progress', 'warning');
            return;
        }
        
        if (!connectionManager.getStatus()) {
            showNotification('No connection. Please check your internet connection.', 'warning');
            return;
        }
        
        try {
            this.isLoading = true;
            this.updateLoadingState(true);
            
            showLoading('Loading emails from Gmail...');
            showNotification('Started loading emails from Gmail', 'info', 3000);
            
            const response = await api.loadEmails();
            
            if (response.status === 'processing') {
                showNotification('Email loading started in background. This may take a few minutes.', 'info', 6000);
                
                // Update status to show processing
                this.updateEmailStatus({
                    status: 'processing',
                    last_checked: new Date().toISOString()
                });
                
                // Poll for completion
                this.pollEmailLoadingProgress();
            } else {
                showNotification('Emails loaded successfully', 'success');
                this.loadEmailStatus();
            }
            
        } catch (error) {
            console.error('Error loading emails:', error);
            APIErrorHandler.handle(error, 'Email Loading');
            
            this.updateEmailStatus({
                status: 'error',
                last_checked: null
            });
        } finally {
            hideLoading();
            this.isLoading = false;
            this.updateLoadingState(false);
        }
    }

    /**
     * Poll for email loading progress
     */
    pollEmailLoadingProgress() {
        const pollInterval = setInterval(async () => {
            try {
                const status = await api.getEmailStatus();
                this.updateEmailStatus(status);
                
                if (status.status !== 'processing') {
                    clearInterval(pollInterval);
                    
                    if (status.status === 'ready') {
                        showNotification('Emails loaded successfully', 'success');
                    } else if (status.status === 'error') {
                        showNotification('Email loading failed', 'error');
                    }
                }
            } catch (error) {
                console.error('Error polling email status:', error);
                clearInterval(pollInterval);
            }
        }, 5000); // Poll every 5 seconds
        
        // Stop polling after 10 minutes
        setTimeout(() => {
            clearInterval(pollInterval);
        }, 600000);
    }

    /**
     * Toggle search container visibility
     */
    toggleSearch() {
        const isVisible = this.elements.searchContainer.style.display !== 'none';
        
        if (isVisible) {
            this.elements.searchContainer.style.display = 'none';
            this.elements.searchEmailsBtn.innerHTML = '<i class="fas fa-search"></i> Search';
            this.elements.searchResults.style.display = 'none';
        } else {
            this.elements.searchContainer.style.display = 'block';
            this.elements.searchEmailsBtn.innerHTML = '<i class="fas fa-times"></i> Close';
            this.elements.emailSearchInput.focus();
        }
    }

    /**
     * Execute email search
     */
    async executeSearch() {
        const query = this.elements.emailSearchInput.value.trim();
        if (!query) {
            showNotification('Please enter a search query', 'warning');
            return;
        }
        
        if (!connectionManager.getStatus()) {
            showNotification('No connection. Please check your internet connection.', 'warning');
            return;
        }
        
        try {
            showLoading('Searching emails...');
            this.elements.executeSearchBtn.disabled = true;
            
            const response = await api.searchEmails(query);
            
            if (response.results && response.results.length > 0) {
                this.displaySearchResults(response.results, query);
                showNotification(`Found ${response.count} result(s)`, 'success', 3000);
            } else {
                this.displayNoResults(query);
                showNotification('No emails found matching your query', 'info', 4000);
            }
            
        } catch (error) {
            console.error('Error searching emails:', error);
            APIErrorHandler.handle(error, 'Email Search');
            this.displaySearchError(error.message);
        } finally {
            hideLoading();
            this.elements.executeSearchBtn.disabled = false;
        }
    }

    /**
     * Display search results
     * @param {Array} results - Array of email results
     * @param {string} query - Search query
     */
    displaySearchResults(results, query) {
        this.searchResults = results;
        this.elements.resultsList.innerHTML = '';
        
        results.forEach((result, index) => {
            const resultEl = this.createResultElement(result, index);
            this.elements.resultsList.appendChild(resultEl);
        });
        
        // Update results header
        const resultsHeader = this.elements.searchResults.querySelector('h4');
        if (resultsHeader) {
            resultsHeader.textContent = `Search Results for "${query}" (${results.length} found)`;
        }
        
        this.elements.searchResults.style.display = 'block';
        
        // Scroll to results
        setTimeout(() => {
            this.elements.searchResults.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }

    /**
     * Display no results message
     * @param {string} query - Search query
     */
    displayNoResults(query) {
        this.elements.resultsList.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">
                    <i class="fas fa-search"></i>
                </div>
                <h4>No Results Found</h4>
                <p>No emails found matching "${escapeHtml(query)}"</p>
                <div class="search-suggestions">
                    <h5>Try:</h5>
                    <ul>
                        <li>Checking your spelling</li>
                        <li>Using broader search terms</li>
                        <li>Making sure emails are loaded first</li>
                    </ul>
                </div>
            </div>
        `;
        
        const resultsHeader = this.elements.searchResults.querySelector('h4');
        if (resultsHeader) {
            resultsHeader.textContent = `Search Results for "${query}"`;
        }
        
        this.elements.searchResults.style.display = 'block';
    }

    /**
     * Display search error
     * @param {string} errorMessage - Error message
     */
    displaySearchError(errorMessage) {
        this.elements.resultsList.innerHTML = `
            <div class="search-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4>Search Error</h4>
                <p>An error occurred while searching: ${escapeHtml(errorMessage)}</p>
                <button class="btn btn-secondary" onclick="emailManagement.executeSearch()">
                    <i class="fas fa-retry"></i> Try Again
                </button>
            </div>
        `;
        
        this.elements.searchResults.style.display = 'block';
    }

    /**
     * Create a result element
     * @param {string} result - Email result text
     * @param {number} index - Result index
     * @returns {HTMLElement} Result element
     */
    createResultElement(result, index) {
        const resultEl = document.createElement('div');
        resultEl.className = 'result-item';
        resultEl.setAttribute('data-index', index);
        
        // Parse email content to extract structured information
        const emailInfo = this.parseEmailResult(result);
        
        resultEl.innerHTML = `
            <div class="result-header">
                <div class="result-title">${emailInfo.subject || `Email ${index + 1}`}</div>
                <div class="result-date">${emailInfo.date || 'Unknown Date'}</div>
            </div>
            <div class="result-meta">
                <div class="result-from">From: ${emailInfo.from || 'Unknown Sender'}</div>
                ${emailInfo.cc ? `<div class="result-cc">CC: ${emailInfo.cc}</div>` : ''}
            </div>
            <div class="result-content">${emailInfo.content || result}</div>
            <div class="result-actions">
                <button class="btn btn-sm btn-secondary" onclick="emailManagement.askAboutEmail(${index})">
                    <i class="fas fa-comments"></i> Ask AI
                </button>
                <button class="btn btn-sm btn-secondary" onclick="emailManagement.copyEmailContent(${index})">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="btn btn-sm btn-secondary" onclick="emailManagement.expandEmail(${index})">
                    <i class="fas fa-expand"></i> View Full
                </button>
            </div>
        `;
        
        // Add hover effects
        resultEl.addEventListener('mouseenter', () => {
            resultEl.style.transform = 'translateY(-2px)';
        });
        
        resultEl.addEventListener('mouseleave', () => {
            resultEl.style.transform = 'translateY(0)';
        });
        
        return resultEl;
    }

    /**
     * Parse email result to extract structured information
     * @param {string} result - Raw email result text
     * @returns {Object} Parsed email information
     */
    parseEmailResult(result) {
        const info = {};
        
        try {
            // Extract date and time
            const dateMatch = result.match(/Date and Time:\s*(.+)/i);
            if (dateMatch) {
                info.date = dateMatch[1].trim();
            }
            
            // Extract sender
            const fromMatch = result.match(/Sender:\s*(.+)/i);
            if (fromMatch) {
                info.from = fromMatch[1].trim();
            }
            
            // Extract CC
            const ccMatch = result.match(/CC:\s*(.+)/i);
            if (ccMatch && ccMatch[1].trim() !== 'None') {
                info.cc = ccMatch[1].trim();
            }
            
            // Extract subject
            const subjectMatch = result.match(/Subject:\s*(.+)/i);
            if (subjectMatch) {
                info.subject = subjectMatch[1].trim();
            }
            
            // Extract email context/content
            const contextMatch = result.match(/Email Context:\s*([\s\S]+?)(?=<Email End>|$)/i);
            if (contextMatch) {
                info.content = contextMatch[1].trim();
            }
            
        } catch (error) {
            console.error('Error parsing email result:', error);
        }
        
        return info;
    }

    /**
     * Ask AI about a specific email
     * @param {number} index - Email index in search results
     */
    askAboutEmail(index) {
        if (!this.searchResults[index]) return;
        
        const email = this.searchResults[index];
        const emailInfo = this.parseEmailResult(email);
        
        let question = `Tell me about this email: "${emailInfo.subject || 'Email'}"`;
        if (emailInfo.from) {
            question += ` from ${emailInfo.from}`;
        }
        
        // Switch to chat page and ask the question
        window.eventEmitter.emit('navigate-to-chat', question);
        showNotification('Switched to chat with your question', 'info', 3000);
    }

    /**
     * Copy email content to clipboard
     * @param {number} index - Email index in search results
     */
    copyEmailContent(index) {
        if (!this.searchResults[index]) return;
        
        copyToClipboard(this.searchResults[index]);
    }

    /**
     * Expand email to show full content
     * @param {number} index - Email index in search results
     */
    expandEmail(index) {
        if (!this.searchResults[index]) return;
        
        const email = this.searchResults[index];
        const emailInfo = this.parseEmailResult(email);
        
        // Create modal or expanded view
        this.showEmailModal(emailInfo, email);
    }

    /**
     * Show email in modal
     * @param {Object} emailInfo - Parsed email information
     * @param {string} fullContent - Full email content
     */
    showEmailModal(emailInfo, fullContent) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'email-modal-overlay';
        modal.innerHTML = `
            <div class="email-modal">
                <div class="email-modal-header">
                    <h3>${emailInfo.subject || 'Email Details'}</h3>
                    <button class="btn btn-icon close-modal">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="email-modal-content">
                    <div class="email-meta">
                        <div><strong>From:</strong> ${emailInfo.from || 'Unknown'}</div>
                        ${emailInfo.cc ? `<div><strong>CC:</strong> ${emailInfo.cc}</div>` : ''}
                        <div><strong>Date:</strong> ${emailInfo.date || 'Unknown'}</div>
                    </div>
                    <div class="email-content">
                        <pre>${escapeHtml(fullContent)}</pre>
                    </div>
                </div>
                <div class="email-modal-actions">
                    <button class="btn btn-primary ask-ai-modal">
                        <i class="fas fa-comments"></i> Ask AI About This
                    </button>
                    <button class="btn btn-secondary copy-modal">
                        <i class="fas fa-copy"></i> Copy Content
                    </button>
                    <button class="btn btn-secondary close-modal">
                        <i class="fas fa-times"></i> Close
                    </button>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
        
        // Add event listeners
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('close-modal')) {
                document.body.removeChild(modal);
            }
        });
        
        modal.querySelector('.ask-ai-modal').addEventListener('click', () => {
            const question = `Tell me about this email: "${emailInfo.subject || 'Email'}" from ${emailInfo.from || 'unknown sender'}`;
            window.eventEmitter.emit('navigate-to-chat', question);
            document.body.removeChild(modal);
        });
        
        modal.querySelector('.copy-modal').addEventListener('click', () => {
            copyToClipboard(fullContent);
        });
        
        // Animate in
        setTimeout(() => {
            modal.classList.add('active');
        }, 10);
    }

    /**
     * Update loading state
     * @param {boolean} loading - Loading state
     */
    updateLoadingState(loading) {
        this.elements.loadEmailsBtn.disabled = loading;
        
        if (loading) {
            this.elements.loadEmailsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        } else {
            this.elements.loadEmailsBtn.innerHTML = '<i class="fas fa-download"></i> Load Emails';
        }
    }

    /**
     * Handle connection status changes
     * @param {boolean} isOnline - Current connection status
     */
    handleConnectionChange(isOnline) {
        this.elements.loadEmailsBtn.disabled = !isOnline || this.isLoading;
        this.elements.executeSearchBtn.disabled = !isOnline || this.elements.emailSearchInput.value.trim().length === 0;
        
        if (!isOnline) {
            this.elements.emailStatusText.textContent = 'Connection lost';
            this.elements.emailStatusText.className = 'text-danger';
        } else {
            this.loadEmailStatus();
        }
    }

    /**
     * Clear search results
     */
    clearResults() {
        this.searchResults = [];
        this.elements.searchResults.style.display = 'none';
        this.elements.resultsList.innerHTML = '';
        this.elements.emailSearchInput.value = '';
    }

    /**
     * Export search results
     */
    exportResults() {
        if (this.searchResults.length === 0) {
            showNotification('No search results to export', 'warning');
            return;
        }
        
        const exportData = {
            query: this.elements.emailSearchInput.value,
            timestamp: new Date().toISOString(),
            results: this.searchResults
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `email-search-results-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showNotification('Search results exported', 'success', 2000);
    }
}

// Add modal styles dynamically
const modalStyles = `
    <style>
        .email-modal-overlay {
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
        
        .email-modal-overlay.active {
            opacity: 1;
        }
        
        .email-modal {
            background: var(--color-bg-secondary);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-lg);
            max-width: 80%;
            max-height: 80%;
            width: 600px;
            display: flex;
            flex-direction: column;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        }
        
        .email-modal-overlay.active .email-modal {
            transform: scale(1);
        }
        
        .email-modal-header {
            padding: var(--spacing-lg);
            border-bottom: 1px solid var(--color-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .email-modal-content {
            flex: 1;
            padding: var(--spacing-lg);
            overflow-y: auto;
        }
        
        .email-meta {
            background: var(--color-bg-tertiary);
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            margin-bottom: var(--spacing-lg);
        }
        
        .email-meta div {
            margin-bottom: var(--spacing-sm);
        }
        
        .email-content pre {
            background: var(--color-bg-primary);
            padding: var(--spacing-lg);
            border-radius: var(--radius-md);
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: inherit;
            font-size: var(--font-size-sm);
            line-height: 1.6;
        }
        
        .email-modal-actions {
            padding: var(--spacing-lg);
            border-top: 1px solid var(--color-border);
            display: flex;
            gap: var(--spacing-md);
            justify-content: flex-end;
        }
        
        .no-results, .search-error {
            text-align: center;
            padding: var(--spacing-xxl);
            color: var(--color-text-secondary);
        }
        
        .no-results-icon, .error-icon {
            font-size: var(--font-size-3xl);
            color: var(--color-text-muted);
            margin-bottom: var(--spacing-lg);
        }
        
        .search-suggestions {
            margin-top: var(--spacing-lg);
            text-align: left;
            display: inline-block;
        }
        
        .search-suggestions ul {
            list-style: none;
            padding-left: 0;
        }
        
        .search-suggestions li:before {
            content: "• ";
            color: var(--color-accent);
            font-weight: bold;
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', modalStyles);

// Initialize email management when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emailManagement = new EmailManagement();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EmailManagement;
}