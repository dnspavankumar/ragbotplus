"""
Modern Main Window for Gmail RAG Assistant
This module provides the main application window with sidebar navigation
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame, QSplitter,
    QScrollArea, QLineEdit, QTextEdit, QStatusBar, QMenuBar,
    QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QThread
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QAction

# Import our custom UI components
from ui.styles import ModernStyles
from ui.components import NotificationManager, LoadingSpinner

class SidebarButton(QPushButton):
    """Custom sidebar navigation button"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {text}")
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setObjectName("sidebar-button")
        
        # Style the button
        self.setStyleSheet("""
            QPushButton#sidebar-button {
                background-color: transparent;
                color: #cdd6f4;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                text-align: left;
                margin: 4px 12px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton#sidebar-button:hover {
                background-color: #494d64;
            }
            QPushButton#sidebar-button:checked {
                background-color: #89b4fa;
                color: white;
                font-weight: 600;
            }
        """)

class ModernSidebar(QFrame):
    """Modern sidebar with navigation buttons"""
    
    page_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setObjectName("sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)
        
        # App title
        title_label = QLabel("Gmail RAG Assistant")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            color: #cdd6f4;
            margin: 20px 0px;
            padding: 10px;
        """)
        layout.addWidget(title_label)
        
        # Navigation buttons
        self.chat_button = SidebarButton("Chat", "💬")
        self.email_button = SidebarButton("Emails", "📧")
        self.settings_button = SidebarButton("Settings", "⚙️")
        self.about_button = SidebarButton("About", "ℹ️")
        
        # Button group for exclusive selection
        self.buttons = [self.chat_button, self.email_button, self.settings_button, self.about_button]
        
        # Connect signals
        self.chat_button.clicked.connect(lambda: self.select_page("chat"))
        self.email_button.clicked.connect(lambda: self.select_page("emails"))
        self.settings_button.clicked.connect(lambda: self.select_page("settings"))
        self.about_button.clicked.connect(lambda: self.select_page("about"))
        
        # Add buttons to layout
        layout.addWidget(self.chat_button)
        layout.addWidget(self.email_button)
        layout.addWidget(self.settings_button)
        layout.addWidget(self.about_button)
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
        # Status section
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            background-color: #45475a;
            border-radius: 8px;
            margin: 12px;
            padding: 12px;
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            color: #a6e3a1;
            font-size: 12px;
            font-weight: 600;
        """)
        
        self.connection_label = QLabel("Connected")
        self.connection_label.setStyleSheet("""
            color: #6c7086;
            font-size: 11px;
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.connection_label)
        layout.addWidget(status_frame)
        
        # Select chat by default
        self.select_page("chat")
    
    def select_page(self, page_name):
        """Select a page and update button states"""
        # Uncheck all buttons
        for button in self.buttons:
            button.setChecked(False)
        
        # Check the selected button
        if page_name == "chat":
            self.chat_button.setChecked(True)
        elif page_name == "emails":
            self.email_button.setChecked(True)
        elif page_name == "settings":
            self.settings_button.setChecked(True)
        elif page_name == "about":
            self.about_button.setChecked(True)
        
        # Emit signal
        self.page_changed.emit(page_name)
    
    def update_status(self, status, connection="Connected"):
        """Update the status display"""
        self.status_label.setText(status)
        self.connection_label.setText(connection)
        
        # Color based on status
        if "error" in status.lower() or "failed" in status.lower():
            color = "#f38ba8"  # Error red
        elif "loading" in status.lower() or "processing" in status.lower():
            color = "#f9e2af"  # Warning yellow
        else:
            color = "#a6e3a1"  # Success green
        
        self.status_label.setStyleSheet(f"""
            color: {color};
            font-size: 12px;
            font-weight: 600;
        """)

class ModernTitleBar(QFrame):
    """Custom title bar with window controls"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setObjectName("title-bar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # App icon and title
        icon_label = QLabel("🤖")
        icon_label.setStyleSheet("font-size: 20px;")
        
        title_label = QLabel("Gmail RAG Assistant")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #cdd6f4;
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Window control buttons would go here
        # For now, we'll use the standard window controls
        
        self.setStyleSheet("""
            QFrame#title-bar {
                background-color: #1e1e2e;
                border-bottom: 1px solid #585b70;
            }
        """)

class WelcomePage(QWidget):
    """Welcome/Getting Started page"""
    
    # Signal to notify main window when email loading is requested
    load_emails_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome message
        welcome_label = QLabel("Welcome to Gmail RAG Assistant! 🚀")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #cdd6f4;
            margin-bottom: 20px;
        """)
        
        subtitle_label = QLabel("Your AI-powered email assistant is ready to help!")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #bac2de;
            margin-bottom: 40px;
        """)
        
        # Feature highlights
        features_label = QLabel("""
        ✨ <b>Key Features:</b><br><br>
        💬 <b>Smart Chat</b> - Ask questions about your emails using natural language<br>
        📧 <b>Email Management</b> - View, search, and organize your Gmail messages<br>
        🤖 <b>AI-Powered</b> - Advanced RAG technology for intelligent responses<br>
        🎤 <b>Voice Input</b> - Speak your questions naturally<br>
        🔒 <b>Secure</b> - Your emails stay private and secure
        """)
        features_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_label.setStyleSheet("""
            font-size: 14px;
            color: #bac2de;
            line-height: 1.6;
            background-color: #313244;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #585b70;
        """)
        
        # Get started button
        get_started_button = QPushButton("Get Started - Load Emails")
        get_started_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 16px 32px;
                font-weight: 600;
                font-size: 16px;
                margin-top: 30px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        
        # Connect button to signal
        get_started_button.clicked.connect(self.load_emails_requested.emit)
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(features_label)
        layout.addWidget(get_started_button)
        layout.addStretch()

class MainWindow(QMainWindow):
    """Main application window with modern design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gmail RAG Assistant")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Initialize notification manager
        self.notification_manager = NotificationManager(self)
        
        # Set up the UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
        # Apply dark theme
        self.apply_theme()
        
        # Center the window
        self.center_window()
    
    def setup_ui(self):
        """Set up the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = ModernSidebar()
        self.sidebar.page_changed.connect(self.change_page)
        
        # Create main content area
        self.main_content = QStackedWidget()
        self.main_content.setObjectName("main-content")
        
        # Create splitter for resizable layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.main_content)
        splitter.setStretchFactor(0, 0)  # Sidebar doesn't stretch
        splitter.setStretchFactor(1, 1)  # Main content stretches
        splitter.setHandleWidth(1)
        
        main_layout.addWidget(splitter)
        
        # Add welcome page initially
        self.welcome_page = WelcomePage()
        self.welcome_page.load_emails_requested.connect(self.start_email_loading)
        self.main_content.addWidget(self.welcome_page)
        self.main_content.setCurrentWidget(self.welcome_page)
    
    def setup_menu(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()
        
        # Check if menubar is available
        if menubar is None:
            return
        
        # File menu
        file_menu = menubar.addMenu("File")
        if file_menu is not None:
            new_chat_action = QAction("New Chat", self)
            new_chat_action.setShortcut("Ctrl+N")
            file_menu.addAction(new_chat_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(QApplication.quit)
            file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        if view_menu is not None:
            toggle_sidebar_action = QAction("Toggle Sidebar", self)
            toggle_sidebar_action.setShortcut("Ctrl+B")
            toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
            view_menu.addAction(toggle_sidebar_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        if help_menu is not None:
            about_action = QAction("About", self)
            about_action.triggered.connect(lambda: self.sidebar.select_page("about"))
            help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets to status bar
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        self.status_bar.addPermanentWidget(QLabel("Gmail RAG Assistant v1.0"))
    
    def apply_theme(self, theme='dark'):
        """Apply the application theme"""
        stylesheet = ModernStyles.get_main_stylesheet(theme)
        self.setStyleSheet(stylesheet)
    
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen()
        if screen is not None:
            screen_geometry = screen.availableGeometry()
            
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            
            self.move(x, y)
    
    def change_page(self, page_name):
        """Change the current page"""
        # For now, we'll just update the status
        self.update_status(f"Switched to {page_name.title()}")
        
        # Clear current widgets (except welcome page)
        while self.main_content.count() > 1:
            widget = self.main_content.widget(1)
            if widget is not None:
                self.main_content.removeWidget(widget)
                widget.deleteLater()
        
        # Add appropriate page widget
        if page_name == "chat":
            # Create and add chat interface
            from ui.chat_interface import ChatInterface
            chat_interface = ChatInterface()
            # Set up status callback
            chat_interface.set_status_callback(self.update_status)
            self.main_content.addWidget(chat_interface)
            self.main_content.setCurrentWidget(chat_interface)
        elif page_name == "emails":
            # Create and add email management interface
            from ui.email_management import EmailManagementInterface
            email_interface = EmailManagementInterface()
            self.main_content.addWidget(email_interface)
            self.main_content.setCurrentWidget(email_interface)
        elif page_name == "settings":
            # Create and add settings interface
            from ui.settings_interface import SettingsInterface
            settings_interface = SettingsInterface()
            self.main_content.addWidget(settings_interface)
            self.main_content.setCurrentWidget(settings_interface)
        elif page_name == "about":
            # Create and add about page from settings interface
            from ui.settings_interface import AboutTab
            about_page = AboutTab()
            self.main_content.addWidget(about_page)
            self.main_content.setCurrentWidget(about_page)
    
    def start_email_loading(self):
        """Start the email loading process with progress dialog"""
        try:
            # Import EmailLoaderThread here to avoid circular imports
            from ui.email_management import EmailLoaderThread
            
            # Create progress dialog
            self.progress_dialog = QProgressDialog("Loading emails...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle("Gmail RAG Assistant")
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setAutoReset(True)
            
            # Create and start email loader thread
            self.email_loader = EmailLoaderThread()
            self.email_loader.progress_updated.connect(self.update_loading_progress)
            self.email_loader.emails_loaded.connect(self.on_emails_loaded)
            
            # Connect progress dialog cancel to thread termination
            self.progress_dialog.canceled.connect(self.email_loader.terminate)
            
            # Update status and start
            self.update_status("Starting email loading...")
            self.progress_dialog.show()
            self.email_loader.start()
            
        except ImportError as e:
            self.show_notification(f"Error importing email loader: {str(e)}", "error")
            self.update_status("Failed to start email loading")
        except Exception as e:
            self.show_notification(f"Error starting email loading: {str(e)}", "error")
            self.update_status("Failed to start email loading")
    
    def update_loading_progress(self, progress, message):
        """Update the loading progress dialog"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(message)
        
        self.update_status(message)
    
    def on_emails_loaded(self, success, message):
        """Handle completion of email loading"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        if success:
            self.show_notification("Emails loaded successfully! You can now start chatting.", "success")
            self.update_status("Emails loaded - Ready to chat")
            # Switch to chat page
            self.sidebar.select_page("chat")
            # Show a helpful message in chat
            QTimer.singleShot(1000, self.show_chat_ready_message)
        else:
            self.show_notification(f"Failed to load emails: {message}", "error")
            self.update_status("Email loading failed")
        
        # Clean up thread
        if hasattr(self, 'email_loader'):
            self.email_loader.deleteLater()
    
    def show_chat_ready_message(self):
        """Show a ready message in the chat interface after emails are loaded"""
        # Find the chat interface in the stacked widget
        for i in range(self.main_content.count()):
            widget = self.main_content.widget(i)
            # Check if this is the chat interface by looking for the specific attribute
            if hasattr(widget, 'messages_area') and hasattr(widget, 'input_area'):
                messages_area = getattr(widget, 'messages_area', None)
                if messages_area is not None:
                    messages_area.add_system_message("✅ Your emails have been loaded and indexed! You can now ask me questions about your emails.")
                break
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility"""
        self.sidebar.setVisible(not self.sidebar.isVisible())
    
    def update_status(self, message):
        """Update the status bar and sidebar status"""
        self.status_label.setText(message)
        if hasattr(self, 'sidebar'):
            self.sidebar.update_status(message)
    
    def show_notification(self, message, notification_type="info", duration=3000):
        """Show a notification toast"""
        self.notification_manager.show_notification(message, notification_type, duration)
    
    def closeEvent(self, a0):
        """Handle application close event"""
        self.update_status("Shutting down...")
        if a0 is not None:
            a0.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Gmail RAG Assistant")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Gmail RAG Assistant")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())