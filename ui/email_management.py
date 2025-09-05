"""
Email Management Interface for Gmail RAG Assistant
This module provides email browsing, searching, and management capabilities
"""

import json
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QScrollArea, QFrame, QLabel, QSplitter, QComboBox, QDateEdit,
    QProgressBar, QListWidget, QListWidgetItem, QTextEdit, QGroupBox,
    QCheckBox, QSpinBox
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QTimer, QThread, QDate, QSize
)
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ui.components import EmailCard, ModernCard, LoadingSpinner, ModernProgressBar
from ui.styles import ModernStyles

class EmailLoaderThread(QThread):
    """Thread for loading emails without blocking UI"""
    
    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    emails_loaded = pyqtSignal(bool, str)    # success, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def run(self):
        """Load emails in background"""
        try:
            self.progress_updated.emit(10, "Authenticating with Gmail...")
            
            # Import here to avoid circular imports
            from RAG_Gmail import load_emails
            
            self.progress_updated.emit(30, "Loading emails from Gmail...")
            
            # Load emails
            load_emails()
            
            self.progress_updated.emit(80, "Processing email data...")
            
            # Small delay to show completion
            self.msleep(500)
            
            self.progress_updated.emit(100, "Emails loaded successfully!")
            self.emails_loaded.emit(True, "Emails loaded and indexed successfully")
            
        except Exception as e:
            self.emails_loaded.emit(False, f"Failed to load emails: {str(e)}")

class EmailSearchThread(QThread):
    """Thread for searching emails without blocking UI"""
    
    search_completed = pyqtSignal(list)  # list of matching emails
    search_error = pyqtSignal(str)
    
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query
    
    def run(self):
        """Search emails in background"""
        try:
            # Import here to avoid circular imports
            from RAG_Gmail import Vector_Search
            
            # Perform vector search
            results = Vector_Search(self.query, demo=False, k=20)
            
            # Parse results into email objects
            emails = []
            for result in results:
                email_data = self.parse_email_text(result)
                if email_data:
                    emails.append(email_data)
            
            self.search_completed.emit(emails)
            
        except Exception as e:
            self.search_error.emit(f"Search error: {str(e)}")
    
    def parse_email_text(self, email_text):
        """Parse email text into structured data"""
        try:
            lines = email_text.strip().split('\n')
            email_data = {
                'subject': 'No Subject',
                'from': 'Unknown',
                'cc': '',
                'date': '',
                'preview': '',
                'full_text': email_text
            }
            
            current_section = None
            content_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('<Email Start>'):
                    continue
                elif line.startswith('<Email End>'):
                    break
                elif line.startswith('Date and Time:'):
                    email_data['date'] = line.replace('Date and Time:', '').strip()
                elif line.startswith('Sender:'):
                    email_data['from'] = line.replace('Sender:', '').strip()
                elif line.startswith('CC:'):
                    email_data['cc'] = line.replace('CC:', '').strip()
                elif line.startswith('Subject:'):
                    email_data['subject'] = line.replace('Subject:', '').strip()
                elif line.startswith('Email Context:'):
                    current_section = 'content'
                    content_text = line.replace('Email Context:', '').strip()
                    if content_text:
                        content_lines.append(content_text)
                elif current_section == 'content' and line:
                    content_lines.append(line)
            
            # Join content lines for preview
            if content_lines:
                email_data['preview'] = ' '.join(content_lines)
            
            return email_data
            
        except Exception as e:
            print(f"Error parsing email: {str(e)}")
            return None

class EmailListWidget(QScrollArea):
    """Custom email list widget"""
    
    email_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.emails = []
    
    def setup_ui(self):
        """Set up the email list UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(8)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.setWidget(self.content_widget)
        
        # Styling
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e2e;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #313244;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c7086;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #89b4fa;
            }
        """)
    
    def add_emails(self, emails):
        """Add emails to the list"""
        self.clear_emails()
        self.emails = emails
        
        if not emails:
            # Show empty state
            empty_label = QLabel("No emails found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("""
                color: #6c7086;
                font-size: 16px;
                font-style: italic;
                padding: 40px;
            """)
            self.content_layout.addWidget(empty_label)
            return
        
        for email in emails:
            email_card = EmailCard(email)
            email_card.clicked.connect(self.email_selected.emit)
            self.content_layout.addWidget(email_card)
        
        # Add stretch to push cards to top
        self.content_layout.addStretch()
    
    def clear_emails(self):
        """Clear all emails from the list"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child:
                widget = child.widget()
                if widget:
                    widget.deleteLater()

class EmailDetailViewer(QFrame):
    """Detailed email viewer"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_email = None
    
    def setup_ui(self):
        """Set up the email detail viewer"""
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 12px;
                border: 1px solid #585b70;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(8)
        
        self.subject_label = QLabel("Select an email to view details")
        self.subject_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #cdd6f4;
            margin-bottom: 8px;
        """)
        self.subject_label.setWordWrap(True)
        
        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet("""
            font-size: 12px;
            color: #6c7086;
            margin-bottom: 8px;
        """)
        self.meta_label.setWordWrap(True)
        
        self.from_label = QLabel("")
        self.from_label.setStyleSheet("""
            font-size: 14px;
            color: #89b4fa;
            font-weight: 500;
        """)
        self.from_label.setWordWrap(True)
        
        header_layout.addWidget(self.subject_label)
        header_layout.addWidget(self.from_label)
        header_layout.addWidget(self.meta_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #585b70;")
        
        # Content
        self.content_area = QTextEdit()
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet("""
            QTextEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 8px;
                padding: 16px;
                font-size: 14px;
                line-height: 1.5;
                font-family: 'Segoe UI', sans-serif;
            }
        """)
        
        # Action buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(12)
        
        self.ask_about_button = QPushButton("Ask about this email")
        self.ask_about_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
            QPushButton:disabled {
                background-color: #45475a;
                color: #6c7086;
            }
        """)
        self.ask_about_button.setEnabled(False)
        
        self.copy_button = QPushButton("Copy Content")
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #585b70;
                border-color: #89b4fa;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
        """)
        self.copy_button.setEnabled(False)
        
        button_layout.addWidget(self.ask_about_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addStretch()
        
        # Add to main layout
        layout.addWidget(header_frame)
        layout.addWidget(separator)
        layout.addWidget(self.content_area)
        layout.addWidget(button_frame)
    
    def display_email(self, email_data):
        """Display email details"""
        self.current_email = email_data
        
        # Update header
        self.subject_label.setText(email_data.get('subject', 'No Subject'))
        self.from_label.setText(f"From: {email_data.get('from', 'Unknown')}")
        
        # Build meta info
        meta_parts = []
        if email_data.get('date'):
            meta_parts.append(f"Date: {email_data['date']}")
        if email_data.get('cc') and email_data['cc'].strip():
            meta_parts.append(f"CC: {email_data['cc']}")
        
        self.meta_label.setText(" | ".join(meta_parts))
        
        # Update content
        content = email_data.get('preview', email_data.get('full_text', 'No content available'))
        self.content_area.setPlainText(content)
        
        # Enable buttons
        self.ask_about_button.setEnabled(True)
        self.copy_button.setEnabled(True)
    
    def clear_display(self):
        """Clear the email display"""
        self.current_email = None
        self.subject_label.setText("Select an email to view details")
        self.from_label.setText("")
        self.meta_label.setText("")
        self.content_area.clear()
        self.ask_about_button.setEnabled(False)
        self.copy_button.setEnabled(False)

class EmailSearchPanel(QFrame):
    """Email search and filter panel"""
    
    search_requested = pyqtSignal(str)
    load_emails_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the search panel"""
        self.setFixedHeight(120)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-bottom: 1px solid #585b70;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel("Email Management")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #cdd6f4;
        """)
        
        # Search and actions row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search emails by content, sender, or subject...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
        """)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        self.search_button.clicked.connect(self.perform_search)
        
        # Load emails button
        self.load_button = QPushButton("Load Emails")
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #94d3a2;
            }
        """)
        self.load_button.clicked.connect(self.load_emails_requested.emit)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #585b70;
                border-color: #89b4fa;
            }
        """)
        self.clear_button.clicked.connect(self.clear_search)
        
        actions_layout.addWidget(self.search_input)
        actions_layout.addWidget(self.search_button)
        actions_layout.addWidget(self.load_button)
        actions_layout.addWidget(self.clear_button)
        
        layout.addWidget(title_label)
        layout.addLayout(actions_layout)
    
    def perform_search(self):
        """Perform email search"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def clear_search(self):
        """Clear search input"""
        self.search_input.clear()

class EmailManagementInterface(QWidget):
    """Main email management interface"""
    
    ask_about_email = pyqtSignal(str)  # Signal to switch to chat with email question
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        
        # Threads
        self.loader_thread = None
        self.search_thread = None
    
    def setup_ui(self):
        """Set up the email management UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search panel
        self.search_panel = EmailSearchPanel()
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Email list (left side)
        list_frame = QFrame()
        list_frame.setMinimumWidth(400)
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Email count label
        self.email_count_label = QLabel("Ready to load emails")
        self.email_count_label.setStyleSheet("""
            background-color: #45475a;
            color: #bac2de;
            padding: 8px 16px;
            font-size: 12px;
            border-bottom: 1px solid #585b70;
        """)
        
        # Email list
        self.email_list = EmailListWidget()
        
        # Progress bar (initially hidden)
        self.progress_bar = ModernProgressBar()
        self.progress_bar.hide()
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("""
            color: #bac2de;
            font-size: 12px;
            padding: 4px 16px;
        """)
        self.progress_label.hide()
        
        list_layout.addWidget(self.email_count_label)
        list_layout.addWidget(self.progress_bar)
        list_layout.addWidget(self.progress_label)
        list_layout.addWidget(self.email_list)
        
        # Email detail viewer (right side)
        self.email_viewer = EmailDetailViewer()
        self.email_viewer.setMinimumWidth(500)
        
        # Add to splitter
        splitter.addWidget(list_frame)
        splitter.addWidget(self.email_viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        # Add to main layout
        layout.addWidget(self.search_panel)
        layout.addWidget(splitter)
    
    def connect_signals(self):
        """Connect UI signals"""
        self.search_panel.search_requested.connect(self.search_emails)
        self.search_panel.load_emails_requested.connect(self.load_emails)
        self.email_list.email_selected.connect(self.email_viewer.display_email)
        self.email_viewer.ask_about_button.clicked.connect(self.ask_about_current_email)
        self.email_viewer.copy_button.clicked.connect(self.copy_email_content)
    
    def load_emails(self):
        """Load emails from Gmail"""
        if self.loader_thread and self.loader_thread.isRunning():
            return
        
        # Show progress
        self.progress_bar.show()
        self.progress_label.show()
        self.progress_bar.setValue(0)
        
        # Update UI state
        self.search_panel.load_button.setEnabled(False)
        self.email_count_label.setText("Loading emails...")
        
        # Start loading thread
        self.loader_thread = EmailLoaderThread()
        self.loader_thread.progress_updated.connect(self.update_load_progress)
        self.loader_thread.emails_loaded.connect(self.handle_emails_loaded)
        self.loader_thread.start()
    
    def update_load_progress(self, percentage, message):
        """Update loading progress"""
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)
    
    def handle_emails_loaded(self, success, message):
        """Handle email loading completion"""
        # Hide progress
        self.progress_bar.hide()
        self.progress_label.hide()
        
        # Re-enable button
        self.search_panel.load_button.setEnabled(True)
        
        if success:
            self.email_count_label.setText("Emails loaded successfully! Use search to find specific emails.")
            # You could also trigger a search to show recent emails
        else:
            self.email_count_label.setText(f"Failed to load emails: {message}")
    
    def search_emails(self, query):
        """Search emails by query"""
        if self.search_thread and self.search_thread.isRunning():
            return
        
        # Update UI
        self.email_count_label.setText(f"Searching for: {query}")
        self.email_list.clear_emails()
        self.email_viewer.clear_display()
        
        # Start search thread
        self.search_thread = EmailSearchThread(query)
        self.search_thread.search_completed.connect(self.handle_search_results)
        self.search_thread.search_error.connect(self.handle_search_error)
        self.search_thread.start()
    
    def handle_search_results(self, emails):
        """Handle search results"""
        self.email_list.add_emails(emails)
        self.email_count_label.setText(f"Found {len(emails)} matching emails")
    
    def handle_search_error(self, error_message):
        """Handle search error"""
        self.email_count_label.setText(f"Search error: {error_message}")
    
    def ask_about_current_email(self):
        """Ask about the currently selected email"""
        if self.email_viewer.current_email:
            subject = self.email_viewer.current_email.get('subject', 'this email')
            question = f"Tell me about the email with subject: {subject}"
            self.ask_about_email.emit(question)
    
    def copy_email_content(self):
        """Copy email content to clipboard"""
        if self.email_viewer.current_email:
            from PyQt6.QtWidgets import QApplication
            content = self.email_viewer.current_email.get('full_text', '')
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(content)
            # Show notification would go here
    
    def set_status_callback(self, callback):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def update_status(self, message):
        """Update status if callback is set"""
        if hasattr(self, 'status_callback') and self.status_callback:
            self.status_callback(message)