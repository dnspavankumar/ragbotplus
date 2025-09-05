#!/usr/bin/env python3
"""
Gmail RAG Assistant - PyQt6 Interface (Legacy)
A beautiful, AI-powered email assistant with advanced RAG capabilities
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QStackedWidget, QSplashScreen
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont

# Import our modern UI components
from ui.main_window import MainWindow
from ui.chat_interface import ChatInterface
from ui.email_management import EmailManagementInterface
from ui.settings_interface import SettingsInterface
from ui.styles import ModernStyles
from ui.components import NotificationManager

class InitializationThread(QThread):
    """
    Background thread for application initialization
    """
    progress_updated = pyqtSignal(int, str)
    initialization_complete = pyqtSignal(bool, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def run(self):
        """
        Initialize the application components
        """
        try:
            self.progress_updated.emit(20, "Initializing application...")
            
            # Small delay to show splash screen
            self.msleep(500)
            
            self.progress_updated.emit(40, "Setting up UI components...")
            self.msleep(300)
            
            self.progress_updated.emit(60, "Loading configuration...")
            self.msleep(300)
            
            self.progress_updated.emit(80, "Preparing email backend...")
            self.msleep(300)
            
            self.progress_updated.emit(100, "Ready!")
            self.msleep(200)
            
            self.initialization_complete.emit(True, "Application ready")
            
        except Exception as e:
            self.initialization_complete.emit(False, f"Initialization failed: {str(e)}")

class ModernSplashScreen(QSplashScreen):
    """
    Modern splash screen for application startup
    """
    
    def __init__(self):
        # Create a custom pixmap for splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor("#1e1e2e"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw app icon
        painter.setPen(QColor("#89b4fa"))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🤖")
        
        # Draw app name
        painter.setPen(QColor("#cdd6f4"))
        painter.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        painter.drawText(50, 200, "Gmail RAG Assistant")
        
        # Draw version
        painter.setPen(QColor("#6c7086"))
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(50, 220, "Version 1.0 - Modern AI Email Assistant")
        
        painter.end()
        
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # Style the splash screen
        self.setStyleSheet("""
            QSplashScreen {
                border: 2px solid #89b4fa;
                border-radius: 12px;
            }
        """)
    
    def update_progress(self, percentage, message):
        """
        Update splash screen with progress information
        """
        self.showMessage(
            f"{message} ({percentage}%)",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
            QColor("#bac2de")
        )

class GmailRAGApplication(QApplication):
    """
    Main application class with modern PyQt6 interface
    """
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        self.setApplicationName("Gmail RAG Assistant")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Gmail RAG Assistant")
        self.setOrganizationDomain("gmail-rag-assistant.local")
        
        # Initialize components
        self.main_window = None
        self.splash = None
        self.init_thread = None
        
        # Show splash screen and initialize
        self.show_splash_and_initialize()
    
    def show_splash_and_initialize(self):
        """
        Show splash screen and initialize application in background
        """
        # Create and show splash screen
        self.splash = ModernSplashScreen()
        self.splash.show()
        
        # Start initialization thread
        self.init_thread = InitializationThread()
        self.init_thread.progress_updated.connect(self.splash.update_progress)
        self.init_thread.initialization_complete.connect(self.on_initialization_complete)
        self.init_thread.start()
    
    def on_initialization_complete(self, success, message):
        """
        Handle initialization completion
        """
        if success:
            # Create main window
            self.create_main_window()
            
            # Hide splash and show main window
            QTimer.singleShot(500, self.show_main_window)
        else:
            # Show error and exit
            if self.splash:
                self.splash.showMessage(
                    f"Error: {message}",
                    Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                    QColor("#f38ba8")
                )
            QTimer.singleShot(3000, self.quit)
    
    def create_main_window(self):
        """
        Create and configure the main application window
        """
        self.main_window = MainWindow()
        
        # Create page instances
        self.chat_interface = ChatInterface()
        self.email_management = EmailManagementInterface()
        self.settings_interface = SettingsInterface()
        
        # Set up page connections
        self.setup_page_connections()
        
        # Add pages to main window
        self.add_pages_to_main_window()
        
        # Connect main window signals
        self.connect_main_window_signals()
    
    def setup_page_connections(self):
        """
        Set up connections between different pages
        """
        if not self.main_window:
            return
            
        # Connect chat interface to main window for status updates
        self.chat_interface.set_status_callback(self.main_window.update_status)
        
        # Connect email management to main window for status updates
        self.email_management.set_status_callback(self.main_window.update_status)
        
        # Connect email management to chat interface
        self.email_management.ask_about_email.connect(self.switch_to_chat_with_question)
        
        # Connect settings to theme changes
        self.settings_interface.theme_changed.connect(self.change_theme)
        self.settings_interface.settings_changed.connect(
            lambda: self.main_window.show_notification("Settings saved successfully!", "success") if self.main_window else None
        )
    
    def add_pages_to_main_window(self):
        """
        Add page widgets to the main window
        """
        if not self.main_window:
            return
            
        # Clear existing widgets except welcome page
        while self.main_window.main_content.count() > 1:
            widget = self.main_window.main_content.widget(1)
            if widget is not None:
                self.main_window.main_content.removeWidget(widget)
                widget.deleteLater()
            else:
                # If widget is None, break to avoid infinite loop
                break
        
        # Add our pages
        self.main_window.main_content.addWidget(self.chat_interface)        # Index 1
        self.main_window.main_content.addWidget(self.email_management)      # Index 2
        self.main_window.main_content.addWidget(self.settings_interface)    # Index 3
    
    def connect_main_window_signals(self):
        """
        Connect main window navigation signals
        """
        if not self.main_window:
            return
            
        # Override the main window's change_page method
        self.main_window.change_page = self.handle_page_change
    
    def handle_page_change(self, page_name):
        """
        Handle page navigation in the main window
        """
        if not self.main_window:
            return
            
        # Update status
        self.main_window.update_status(f"Switched to {page_name.title()}")
        
        # Switch to appropriate page
        if page_name == "chat":
            self.main_window.main_content.setCurrentIndex(1)  # Chat interface
        elif page_name == "emails":
            self.main_window.main_content.setCurrentIndex(2)  # Email management
        elif page_name == "settings":
            self.main_window.main_content.setCurrentIndex(3)  # Settings
        elif page_name == "about":
            self.main_window.main_content.setCurrentIndex(3)  # Settings (about tab)
            # Switch to about tab in settings
            self.settings_interface.tab_widget.setCurrentIndex(2)
        
        # Show notification for page switch
        self.main_window.show_notification(f"Switched to {page_name.title()}", "info", 2000)
    
    def switch_to_chat_with_question(self, question):
        """
        Switch to chat interface and ask a specific question
        """
        if not self.main_window:
            return
            
        # Switch to chat page
        self.main_window.sidebar.select_page("chat")
        
        # Set the question in chat input and send it
        self.chat_interface.input_area.text_input.setPlainText(question)
        self.chat_interface.send_message(question)
    
    def change_theme(self, theme):
        """
        Change the application theme
        """
        if theme == "auto":
            # For now, default to dark theme
            theme = "dark"
        
        # Apply theme to main window
        if self.main_window:
            self.main_window.apply_theme(theme)
        
        # Show notification
        if self.main_window:
            self.main_window.show_notification(f"Switched to {theme} theme", "success", 2000)
    
    def show_main_window(self):
        """
        Show the main window and hide splash screen
        """
        if self.splash:
            self.splash.hide()
            self.splash.deleteLater()
            self.splash = None
        
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Show welcome notification
            QTimer.singleShot(1000, lambda: (
                self.main_window.show_notification(
                    "Welcome to Gmail RAG Assistant! 🚀", "success", 4000
                ) if self.main_window else None
            ))

def main():
    """
    Main entry point for the application
    """
    # Enable high DPI scaling (PyQt6 handles this automatically)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create and run application
    app = GmailRAGApplication(sys.argv)
    
    # Set global error handling
    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Handle uncaught exceptions
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        import traceback
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Uncaught exception: {error_msg}")
        
        # Show error to user if main window exists
        if hasattr(app, 'main_window') and app.main_window:
            app.main_window.show_notification(
                f"An unexpected error occurred: {str(exc_value)}", "error", 5000
            )
    
    sys.excepthook = handle_exception
    
    # Start the application
    try:
        exit_code = app.exec()
        return exit_code
    except Exception as e:
        print(f"Application error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 