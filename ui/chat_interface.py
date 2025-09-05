"""
Modern Chat Interface for Gmail RAG Assistant
This module provides a beautiful chat interface with message bubbles and animations
"""

import threading
import speech_recognition as sr
import pyttsx3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
    QScrollArea, QFrame, QLabel, QSizePolicy, QLineEdit, QSplitter
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QTimer, QThread, QPropertyAnimation, 
    QEasingCurve, QRect, QSize, QEvent
)
from PyQt6.QtGui import QFont, QTextCursor, QIcon, QPainter, QColor, QKeyEvent

from ui.components import ChatBubble, TypingIndicator, LoadingSpinner
from ui.styles import ModernStyles

class VoiceInputThread(QThread):
    """Thread for handling voice input without blocking UI"""
    
    voice_recognized = pyqtSignal(str)
    voice_error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recognizer = sr.Recognizer()
    
    def run(self):
        """Run voice recognition in background"""
        try:
            # Check if recognize_google method exists
            if not hasattr(self.recognizer, 'recognize_google'):
                self.voice_error.emit("Google Speech Recognition not available. Please check SpeechRecognition library installation.")
                return
                
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                
                # Use getattr as a safer way to call the method
                recognize_method = getattr(self.recognizer, 'recognize_google', None)
                if recognize_method is None:
                    self.voice_error.emit("Google Speech Recognition method not found")
                    return
                    
                text = recognize_method(audio)
                self.voice_recognized.emit(text)
        except sr.WaitTimeoutError:
            self.voice_error.emit("Listening timeout - please try again")
        except sr.UnknownValueError:
            self.voice_error.emit("Could not understand audio - please speak clearly")
        except sr.RequestError as e:
            self.voice_error.emit(f"Voice recognition error: {str(e)}")
        except AttributeError as e:
            self.voice_error.emit(f"Speech recognition method not available: {str(e)}")
        except Exception as e:
            self.voice_error.emit(f"Unexpected error: {str(e)}")

class ChatResponseThread(QThread):
    """Thread for handling chat responses without blocking UI"""
    
    response_ready = pyqtSignal(str, object)  # response, messages
    response_error = pyqtSignal(str)
    
    def __init__(self, query, messages=None, parent=None):
        super().__init__(parent)
        self.query = query
        self.messages = messages
    
    def run(self):
        """Process chat response in background"""
        try:
            # Import here to avoid circular imports
            from RAG_Gmail import ask_question
            
            messages, response = ask_question(self.query, self.messages)
            self.response_ready.emit(response, messages)
        except Exception as e:
            self.response_error.emit(f"Error processing your question: {str(e)}")

class TextToSpeechThread(QThread):
    """Thread for text-to-speech without blocking UI"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.engine = None
    
    def run(self):
        """Run text-to-speech in background"""
        try:
            if not self.engine:
                self.engine = pyttsx3.init()
                
            # Configure voice settings
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate
            self.engine.setProperty('rate', 180)  # Slightly slower for clarity
            
            self.engine.say(self.text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Text-to-speech error: {str(e)}")

class ModernChatInput(QFrame):
    """Modern chat input widget with send button and voice input"""
    
    message_sent = pyqtSignal(str)
    voice_input_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the chat input UI"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-top: 1px solid #585b70;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        
        # Text input
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your message here... (Press Enter to send, Shift+Enter for new line)")
        self.text_input.setFixedHeight(50)
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 25px;
                padding: 12px 20px;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QTextEdit:focus {
                border-color: #89b4fa;
                outline: none;
            }
        """)
        
        # Connect text input signals
        self.text_input.installEventFilter(self)
        
        # Voice input button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setFixedSize(50, 50)
        self.voice_button.setToolTip("Voice Input (Click and speak)")
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
        """)
        self.voice_button.clicked.connect(self.voice_input_requested.emit)
        
        # Send button
        self.send_button = QPushButton("➤")
        self.send_button.setFixedSize(50, 50)
        self.send_button.setToolTip("Send Message")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:pressed {
                background-color: #585b70;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        # Add widgets to layout
        layout.addWidget(self.text_input)
        layout.addWidget(self.voice_button)
        layout.addWidget(self.send_button)
    
    def eventFilter(self, a0, a1):
        """Handle key events for text input"""
        if a0 == self.text_input and a1 is not None and a1.type() == QEvent.Type.KeyPress:
            # Check if it's a QKeyEvent by checking type
            if isinstance(a1, QKeyEvent):
                if a1.key() == Qt.Key.Key_Return and not a1.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    self.send_message()
                    return True
        return super().eventFilter(a0, a1)
    
    def send_message(self):
        """Send the current message"""
        message = self.text_input.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.text_input.clear()
    
    def set_voice_button_state(self, listening=False):
        """Update voice button appearance based on state"""
        if listening:
            self.voice_button.setText("⏹")
            self.voice_button.setToolTip("Listening... (Click to stop)")
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 18px;
                    font-weight: bold;
                }
            """)
        else:
            self.voice_button.setText("🎤")
            self.voice_button.setToolTip("Voice Input (Click and speak)")
            self.voice_button.setStyleSheet("""
                QPushButton {
                    background-color: #89b4fa;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-size: 18px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #74c7ec;
                }
                QPushButton:pressed {
                    background-color: #585b70;
                }
            """)
    
    def set_enabled(self, enabled):
        """Enable/disable the input controls"""
        self.text_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        self.voice_button.setEnabled(enabled)

class ChatMessagesArea(QScrollArea):
    """Scrollable chat messages area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        
        self.setWidget(self.messages_widget)
        
        # Track components
        self.typing_indicator = None
    
    def setup_ui(self):
        """Set up the scroll area"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e2e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #313244;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c7086;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #89b4fa;
            }
        """)
    
    def add_message(self, message, is_user=False, animate=True):
        """Add a message bubble to the chat"""
        bubble = ChatBubble(message, is_user)
        
        if animate and not is_user:
            # Start with opacity 0 for animation
            bubble.setStyleSheet(bubble.styleSheet() + "QFrame { opacity: 0; }")
        
        self.messages_layout.addWidget(bubble)
        
        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Animate bubble appearance for assistant messages
        if animate and not is_user:
            self.animate_bubble_in(bubble)
        
        return bubble
    
    def animate_bubble_in(self, bubble):
        """Animate bubble appearance with fade-in effect"""
        # Remove opacity style to show the bubble
        QTimer.singleShot(200, lambda: bubble.setStyleSheet(
            bubble.styleSheet().replace("QFrame { opacity: 0; }", "")
        ))
    
    def show_typing_indicator(self):
        """Show typing indicator"""
        if not self.typing_indicator:
            self.typing_indicator = TypingIndicator()
            self.messages_layout.addWidget(self.typing_indicator)
            self.typing_indicator.start_animation()
            QTimer.singleShot(100, self.scroll_to_bottom)
    
    def hide_typing_indicator(self):
        """Hide typing indicator"""
        if self.typing_indicator:
            self.typing_indicator.stop_animation()
            self.messages_layout.removeWidget(self.typing_indicator)
            self.typing_indicator.deleteLater()
            self.typing_indicator = None
    
    def add_system_message(self, message):
        """Add a system message"""
        system_label = QLabel(message)
        system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_label.setStyleSheet("""
            background-color: #313244;
            color: #6c7086;
            border-radius: 12px;
            padding: 8px 16px;
            margin: 8px 40px;
            font-size: 12px;
            font-style: italic;
        """)
        system_label.setWordWrap(True)
        
        self.messages_layout.addWidget(system_label)
        QTimer.singleShot(100, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        scrollbar = self.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_messages(self):
        """Clear all messages"""
        while self.messages_layout.count():
            child = self.messages_layout.takeAt(0)
            if child and child.widget():
                widget = child.widget()
                if widget:
                    widget.deleteLater()
        
        self.typing_indicator = None

class ChatInterface(QWidget):
    """Main chat interface widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.conversation_messages = None
        self.new_conversation = True
        
        # Initialize threads
        self.voice_thread = None
        self.response_thread = None
        self.tts_thread = None
        
        self.setup_ui()
        self.connect_signals()
        
        # Show welcome message
        self.show_welcome_message()
    
    def setup_ui(self):
        """Set up the chat interface UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Chat header
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-bottom: 1px solid #585b70;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Title and subtitle
        title_label = QLabel("AI Chat Assistant")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #cdd6f4;
        """)
        
        subtitle_label = QLabel("Ask questions about your emails")
        subtitle_label.setStyleSheet("""
            font-size: 12px;
            color: #6c7086;
        """)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Action buttons
        self.new_chat_button = QPushButton("New Chat")
        self.new_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #585b70;
                border-color: #89b4fa;
            }
        """)
        
        self.speech_toggle = QPushButton("🔊")
        self.speech_toggle.setCheckable(True)
        self.speech_toggle.setChecked(True)
        self.speech_toggle.setFixedSize(30, 30)
        self.speech_toggle.setToolTip("Toggle Text-to-Speech")
        self.speech_toggle.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
            QPushButton:checked {
                background-color: #89b4fa;
                color: white;
            }
        """)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.new_chat_button)
        header_layout.addWidget(self.speech_toggle)
        
        # Messages area
        self.messages_area = ChatMessagesArea()
        
        # Input area
        self.input_area = ModernChatInput()
        
        # Add to main layout
        layout.addWidget(header)
        layout.addWidget(self.messages_area)
        layout.addWidget(self.input_area)
    
    def connect_signals(self):
        """Connect UI signals"""
        self.input_area.message_sent.connect(self.send_message)
        self.input_area.voice_input_requested.connect(self.start_voice_input)
        self.new_chat_button.clicked.connect(self.start_new_conversation)
    
    def show_welcome_message(self):
        """Show welcome message when chat opens"""
        welcome_text = """
        👋 Hi! I'm your Gmail AI assistant. I can help you:
        
        • Find specific emails by content, sender, or date
        • Summarize email conversations
        • Answer questions about your email history
        • Search for information across your messages
        
        To get started, make sure your emails are loaded, then ask me anything!
        """
        
        self.messages_area.add_system_message("Welcome to Gmail RAG Assistant")
        self.messages_area.add_message(welcome_text.strip(), is_user=False, animate=True)
    
    def send_message(self, message):
        """Send a user message and get AI response"""
        # Add user message to chat
        self.messages_area.add_message(message, is_user=True)
        
        # Disable input while processing
        self.input_area.set_enabled(False)
        
        # Show typing indicator
        self.messages_area.show_typing_indicator()
        
        # Start response processing in background
        self.response_thread = ChatResponseThread(message, self.conversation_messages)
        self.response_thread.response_ready.connect(self.handle_response)
        self.response_thread.response_error.connect(self.handle_response_error)
        self.response_thread.start()
    
    def handle_response(self, response, messages):
        """Handle successful AI response"""
        # Update conversation state
        self.conversation_messages = messages
        self.new_conversation = False
        
        # Hide typing indicator
        self.messages_area.hide_typing_indicator()
        
        # Add response to chat
        self.messages_area.add_message(response, is_user=False, animate=True)
        
        # Re-enable input
        self.input_area.set_enabled(True)
        
        # Start text-to-speech if enabled
        if self.speech_toggle.isChecked():
            self.start_text_to_speech(response)
    
    def handle_response_error(self, error_message):
        """Handle AI response error"""
        # Hide typing indicator
        self.messages_area.hide_typing_indicator()
        
        # Add error message
        self.messages_area.add_message(f"Sorry, I encountered an error: {error_message}", is_user=False)
        
        # Re-enable input
        self.input_area.set_enabled(True)
    
    def start_voice_input(self):
        """Start voice input recognition"""
        if self.voice_thread and self.voice_thread.isRunning():
            return
        
        # Update UI
        self.input_area.set_voice_button_state(listening=True)
        
        # Start voice recognition
        self.voice_thread = VoiceInputThread()
        self.voice_thread.voice_recognized.connect(self.handle_voice_recognized)
        self.voice_thread.voice_error.connect(self.handle_voice_error)
        self.voice_thread.finished.connect(lambda: self.input_area.set_voice_button_state(listening=False))
        self.voice_thread.start()
    
    def handle_voice_recognized(self, text):
        """Handle successful voice recognition"""
        # Set text in input and send
        self.input_area.text_input.setPlainText(text)
        self.send_message(text)
    
    def handle_voice_error(self, error_message):
        """Handle voice recognition error"""
        # Show error in chat
        self.messages_area.add_system_message(f"Voice input error: {error_message}")
    
    def start_text_to_speech(self, text):
        """Start text-to-speech for response"""
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.terminate()
        
        self.tts_thread = TextToSpeechThread(text)
        self.tts_thread.start()
    
    def start_new_conversation(self):
        """Start a new conversation"""
        self.conversation_messages = None
        self.new_conversation = True
        self.messages_area.clear_messages()
        
        # Show system message
        self.messages_area.add_system_message("Started new conversation")
        
        # Show welcome message again
        self.show_welcome_message()
    
    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def update_status(self, message):
        """Update status if callback is set"""
        if hasattr(self, 'status_callback') and self.status_callback:
            self.status_callback(message)