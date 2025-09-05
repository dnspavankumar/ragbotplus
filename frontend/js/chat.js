// ===== CHAT INTERFACE MODULE =====

class ChatInterface {
    constructor() {
        this.sessionId = null;
        this.isProcessing = false;
        this.messageHistory = [];
        this.voiceRecognition = null;
        this.speechSynthesis = null;
        this.autoScrollEnabled = true;
        
        this.elements = {
            messagesContainer: document.getElementById('chatMessages'),
            messageInput: document.getElementById('messageInput'),
            sendButton: document.getElementById('sendBtn'),
            voiceButton: document.getElementById('voiceBtn'),
            newChatButton: document.getElementById('newChatBtn')
        };
        
        this.init();
    }

    /**
     * Initialize chat interface
     */
    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.setupSpeechSynthesis();
        this.loadChatHistory();
        this.updateWelcomeTime();
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Send button click
        this.elements.sendButton.addEventListener('click', () => this.handleSendMessage());
        
        // Enter key in textarea (Shift+Enter for new line)
        this.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        // Auto-resize textarea
        this.elements.messageInput.addEventListener('input', () => this.autoResizeTextarea());
        
        // Voice button click
        this.elements.voiceButton.addEventListener('click', () => this.handleVoiceInput());
        
        // New chat button
        this.elements.newChatButton.addEventListener('click', () => this.startNewChat());
        
        // Connection status listener
        connectionManager.addListener((isOnline) => this.handleConnectionChange(isOnline));
        
        // Auto-scroll detection
        this.elements.messagesContainer.addEventListener('scroll', () => {
            const container = this.elements.messagesContainer;
            const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 50;
            this.autoScrollEnabled = isNearBottom;
        });
    }

    /**
     * Set up voice recognition
     */
    setupVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech recognition not supported');
            this.elements.voiceButton.disabled = true;
            this.elements.voiceButton.title = 'Speech recognition not supported';
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.voiceRecognition = new SpeechRecognition();
        
        this.voiceRecognition.continuous = false;
        this.voiceRecognition.interimResults = false;
        this.voiceRecognition.lang = 'en-US';
        
        this.voiceRecognition.onstart = () => {
            this.elements.voiceButton.classList.add('recording');
            this.elements.voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
            showNotification('Listening... Speak now', 'info', 3000);
        };
        
        this.voiceRecognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.elements.messageInput.value = transcript;
            this.autoResizeTextarea();
            showNotification('Voice input received', 'success', 2000);
        };
        
        this.voiceRecognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            let message = 'Voice input failed';
            
            switch (event.error) {
                case 'no-speech':
                    message = 'No speech detected. Please try again.';
                    break;
                case 'audio-capture':
                    message = 'Microphone access denied or not available.';
                    break;
                case 'not-allowed':
                    message = 'Microphone permission denied.';
                    break;
                case 'network':
                    message = 'Network error during voice input.';
                    break;
            }
            
            showNotification(message, 'error', 4000);
        };
        
        this.voiceRecognition.onend = () => {
            this.elements.voiceButton.classList.remove('recording');
            this.elements.voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        };
    }

    /**
     * Set up speech synthesis
     */
    setupSpeechSynthesis() {
        if (!('speechSynthesis' in window)) {
            console.warn('Speech synthesis not supported');
            return;
        }
        
        this.speechSynthesis = window.speechSynthesis;
    }

    /**
     * Handle sending a message
     */
    async handleSendMessage() {
        const message = this.elements.messageInput.value.trim();
        if (!message || this.isProcessing) return;
        
        if (!connectionManager.getStatus()) {
            showNotification('No connection. Please check your internet connection.', 'warning');
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.elements.messageInput.value = '';
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            this.isProcessing = true;
            this.updateButtonStates();
            
            // Send message to backend
            const response = await api.sendChatMessage(message, this.sessionId);
            
            // Update session ID
            if (response.session_id) {
                this.sessionId = response.session_id;
            }
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add assistant response
            this.addMessage(response.response, 'assistant');
            
            // Save to history
            this.saveChatHistory();
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            const errorMsg = 'I apologize, but I encountered an error processing your message. Please try again.';
            this.addMessage(errorMsg, 'assistant', true);
            
            APIErrorHandler.handle(error, 'Chat Message');
        } finally {
            this.isProcessing = false;
            this.updateButtonStates();
        }
    }

    /**
     * Handle voice input
     */
    handleVoiceInput() {
        if (!this.voiceRecognition) {
            showNotification('Voice input not supported', 'error');
            return;
        }
        
        if (this.elements.voiceButton.classList.contains('recording')) {
            this.voiceRecognition.stop();
            return;
        }
        
        try {
            this.voiceRecognition.start();
        } catch (error) {
            console.error('Voice recognition error:', error);
            showNotification('Failed to start voice input', 'error');
        }
    }

    /**
     * Add a message to the chat
     * @param {string} content - Message content
     * @param {string} type - Message type ('user' or 'assistant')
     * @param {boolean} isError - Whether this is an error message
     */
    addMessage(content, type, isError = false) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}-message`;
        
        const timestamp = new Date();
        const timeString = formatTime(timestamp);
        
        const avatarIcon = type === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        const parsedContent = parseMarkdown(content);
        
        messageEl.innerHTML = `
            <div class="message-avatar">
                ${avatarIcon}
            </div>
            <div class="message-content">
                <div class="message-bubble ${isError ? 'error' : ''}">
                    ${parsedContent}
                </div>
                <div class="message-time">
                    <span>${timeString}</span>
                </div>
            </div>
        `;
        
        // Add copy functionality to assistant messages
        if (type === 'assistant') {
            const bubble = messageEl.querySelector('.message-bubble');
            bubble.addEventListener('dblclick', () => {
                copyToClipboard(content);
            });
            bubble.title = 'Double-click to copy';
            bubble.style.cursor = 'pointer';
        }
        
        // Add message to container
        this.elements.messagesContainer.appendChild(messageEl);
        
        // Store in history
        this.messageHistory.push({
            content,
            type,
            timestamp: timestamp.toISOString(),
            isError
        });
        
        // Auto-scroll to bottom if enabled
        if (this.autoScrollEnabled) {
            setTimeout(() => this.scrollToBottom(), 100);
        }
        
        // Speak assistant messages if enabled
        if (type === 'assistant' && !isError && this.speechSynthesis) {
            this.speakMessage(content);
        }
    }

    /**
     * Show typing indicator
     */
    showTypingIndicator() {
        // Remove existing typing indicator
        this.hideTypingIndicator();
        
        const typingEl = document.createElement('div');
        typingEl.className = 'typing-indicator';
        typingEl.id = 'typingIndicator';
        typingEl.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.elements.messagesContainer.appendChild(typingEl);
        this.scrollToBottom();
    }

    /**
     * Hide typing indicator
     */
    hideTypingIndicator() {
        const typingEl = document.getElementById('typingIndicator');
        if (typingEl) {
            typingEl.remove();
        }
    }

    /**
     * Auto-resize textarea based on content
     */
    autoResizeTextarea() {
        const textarea = this.elements.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    /**
     * Scroll to bottom of messages
     */
    scrollToBottom() {
        const container = this.elements.messagesContainer;
        container.scrollTop = container.scrollHeight;
    }

    /**
     * Start a new chat session
     */
    startNewChat() {
        if (this.sessionId && this.messageHistory.length > 1) {
            // Ask for confirmation if there's an active conversation
            if (!confirm('Are you sure you want to start a new chat? Current conversation will be saved.')) {
                return;
            }
        }
        
        // Save current chat if it exists
        this.saveChatHistory();
        
        // Reset chat state
        this.sessionId = null;
        this.messageHistory = [];
        
        // Clear messages except welcome message
        const messages = this.elements.messagesContainer.querySelectorAll('.message:not(.welcome-message)');
        messages.forEach(msg => msg.remove());
        
        // Update welcome time
        this.updateWelcomeTime();
        
        // Clear input
        this.elements.messageInput.value = '';
        this.autoResizeTextarea();
        
        showNotification('New chat started', 'success', 2000);
    }

    /**
     * Update welcome message time
     */
    updateWelcomeTime() {
        const welcomeTimeEl = document.getElementById('welcomeTime');
        if (welcomeTimeEl) {
            welcomeTimeEl.textContent = formatTime(new Date());
        }
    }

    /**
     * Update button states based on current state
     */
    updateButtonStates() {
        this.elements.sendButton.disabled = this.isProcessing;
        this.elements.voiceButton.disabled = this.isProcessing;
        
        const hasText = this.elements.messageInput.value.trim().length > 0;
        this.elements.sendButton.style.opacity = (hasText && !this.isProcessing) ? '1' : '0.6';
    }

    /**
     * Handle connection status changes
     * @param {boolean} isOnline - Current connection status
     */
    handleConnectionChange(isOnline) {
        if (!isOnline) {
            this.elements.sendButton.disabled = true;
            this.elements.voiceButton.disabled = true;
        } else {
            this.updateButtonStates();
        }
    }

    /**
     * Speak a message using text-to-speech
     * @param {string} text - Text to speak
     */
    speakMessage(text) {
        if (!this.speechSynthesis || !text) return;
        
        // Cancel any ongoing speech
        this.speechSynthesis.cancel();
        
        // Create utterance
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.8;
        utterance.pitch = 1.0;
        utterance.volume = 0.8;
        
        // Use a pleasant voice if available
        const voices = this.speechSynthesis.getVoices();
        const femaleVoice = voices.find(voice => 
            voice.name.toLowerCase().includes('female') || 
            voice.name.toLowerCase().includes('zira') ||
            voice.name.toLowerCase().includes('hazel')
        );
        
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }
        
        this.speechSynthesis.speak(utterance);
    }

    /**
     * Save chat history to local storage
     */
    saveChatHistory() {
        if (this.messageHistory.length === 0) return;
        
        const chatData = {
            sessionId: this.sessionId,
            messages: this.messageHistory,
            timestamp: new Date().toISOString()
        };
        
        // Save to local storage
        const chatHistory = storage.get('chatHistory', []);
        
        // Update existing session or add new one
        const existingIndex = chatHistory.findIndex(chat => chat.sessionId === this.sessionId);
        if (existingIndex >= 0) {
            chatHistory[existingIndex] = chatData;
        } else {
            chatHistory.push(chatData);
        }
        
        // Keep only last 50 chats
        if (chatHistory.length > 50) {
            chatHistory.splice(0, chatHistory.length - 50);
        }
        
        storage.set('chatHistory', chatHistory);
    }

    /**
     * Load chat history from local storage
     */
    loadChatHistory() {
        const chatHistory = storage.get('chatHistory', []);
        
        // Get the most recent chat if available
        if (chatHistory.length > 0) {
            const lastChat = chatHistory[chatHistory.length - 1];
            const lastChatTime = new Date(lastChat.timestamp);
            const now = new Date();
            
            // Only restore if it's less than 24 hours old
            if (now - lastChatTime < 24 * 60 * 60 * 1000) {
                this.sessionId = lastChat.sessionId;
                this.messageHistory = lastChat.messages || [];
                
                // Restore messages (except welcome message which is already in HTML)
                this.messageHistory.forEach(msg => {
                    if (msg.type !== 'welcome') {
                        const messageEl = this.createMessageElement(msg);
                        this.elements.messagesContainer.appendChild(messageEl);
                    }
                });
            }
        }
    }

    /**
     * Create a message element from history data
     * @param {Object} messageData - Message data from history
     * @returns {HTMLElement} Message element
     */
    createMessageElement(messageData) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${messageData.type}-message`;
        
        const timeString = formatTime(new Date(messageData.timestamp));
        const avatarIcon = messageData.type === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        const parsedContent = parseMarkdown(messageData.content);
        
        messageEl.innerHTML = `
            <div class="message-avatar">
                ${avatarIcon}
            </div>
            <div class="message-content">
                <div class="message-bubble ${messageData.isError ? 'error' : ''}">
                    ${parsedContent}
                </div>
                <div class="message-time">
                    <span>${timeString}</span>
                </div>
            </div>
        `;
        
        return messageEl;
    }

    /**
     * Clear all chat history
     */
    clearHistory() {
        if (confirm('Are you sure you want to clear all chat history? This action cannot be undone.')) {
            storage.remove('chatHistory');
            this.startNewChat();
            showNotification('Chat history cleared', 'success', 2000);
        }
    }

    /**
     * Export chat history
     */
    exportHistory() {
        const chatHistory = storage.get('chatHistory', []);
        if (chatHistory.length === 0) {
            showNotification('No chat history to export', 'warning');
            return;
        }
        
        const dataStr = JSON.stringify(chatHistory, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `gmail-rag-chat-history-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showNotification('Chat history exported', 'success', 2000);
    }
}

// Initialize chat interface when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatInterface = new ChatInterface();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatInterface;
}