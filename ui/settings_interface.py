"""
Settings and Configuration Interface for Gmail RAG Assistant
This module provides settings management and configuration options
"""

import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QScrollArea, QFrame, QLabel, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QTextEdit, QFileDialog, QSlider, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ui.components import ModernCard

class SettingsGroup(QGroupBox):
    """Custom settings group widget"""
    
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #313244;
                border: 1px solid #585b70;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: 600;
                font-size: 16px;
                color: #cdd6f4;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: #313244;
            }
        """)

class APIConfigurationTab(QWidget):
    """API Configuration tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Set up the API configuration UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Groq API Settings
        groq_group = SettingsGroup("Groq API Configuration")
        groq_layout = QVBoxLayout(groq_group)
        groq_layout.setSpacing(12)
        
        # API Key
        api_key_label = QLabel("Groq API Key:")
        api_key_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Groq API key...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border-color: #89b4fa;
            }
        """)
        
        # Show/Hide API Key
        api_key_actions_layout = QHBoxLayout()
        self.show_api_key_btn = QPushButton("Show")
        self.show_api_key_btn.setCheckable(True)
        self.show_api_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: 1px solid #585b70;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
            QPushButton:checked {
                background-color: #89b4fa;
                color: white;
            }
        """)
        self.show_api_key_btn.clicked.connect(self.toggle_api_key_visibility)
        
        self.test_api_btn = QPushButton("Test Connection")
        self.test_api_btn.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #94d3a2;
            }
        """)
        self.test_api_btn.clicked.connect(self.test_api_connection)
        
        api_key_actions_layout.addWidget(self.show_api_key_btn)
        api_key_actions_layout.addWidget(self.test_api_btn)
        api_key_actions_layout.addStretch()
        
        # Model Selection
        model_label = QLabel("AI Model:")
        model_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "deepseek-r1-distill-llama-70b",
            "llama-3.1-70b-versatile", 
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ])
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 200px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #89b4fa;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 12px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #bac2de;
                border-top: none;
                border-right: none;
                width: 6px;
                height: 6px;
            }
        """)
        
        # Temperature Setting
        temp_label = QLabel("Temperature (Creativity):")
        temp_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(30)
        self.temperature_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #45475a;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: none;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)
        
        self.temperature_value = QLabel("0.3")
        self.temperature_value.setStyleSheet("color: #89b4fa; font-weight: 600; min-width: 30px;")
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_value.setText(f"{v/100:.1f}")
        )
        
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_value)
        
        groq_layout.addWidget(api_key_label)
        groq_layout.addWidget(self.api_key_input)
        groq_layout.addLayout(api_key_actions_layout)
        groq_layout.addWidget(model_label)
        groq_layout.addWidget(self.model_combo)
        groq_layout.addWidget(temp_label)
        groq_layout.addLayout(temp_layout)
        
        # Gmail API Settings
        gmail_group = SettingsGroup("Gmail API Configuration")
        gmail_layout = QVBoxLayout(gmail_group)
        gmail_layout.setSpacing(12)
        
        # Credentials file
        creds_label = QLabel("Credentials File:")
        creds_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        creds_layout = QHBoxLayout()
        self.creds_path_input = QLineEdit()
        self.creds_path_input.setPlaceholderText("Path to credentials.json file...")
        self.creds_path_input.setReadOnly(True)
        self.creds_path_input.setStyleSheet("""
            QLineEdit {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
        """)
        
        self.browse_creds_btn = QPushButton("Browse")
        self.browse_creds_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #74c7ec;
            }
        """)
        self.browse_creds_btn.clicked.connect(self.browse_credentials_file)
        
        creds_layout.addWidget(self.creds_path_input)
        creds_layout.addWidget(self.browse_creds_btn)
        
        # Email fetch settings
        fetch_label = QLabel("Email Fetching:")
        fetch_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        self.auto_load_checkbox = QCheckBox("Auto-load emails on startup")
        self.auto_load_checkbox.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #585b70;
                border-radius: 4px;
                background-color: #45475a;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        
        gmail_layout.addWidget(creds_label)
        gmail_layout.addLayout(creds_layout)
        gmail_layout.addWidget(fetch_label)
        gmail_layout.addWidget(self.auto_load_checkbox)
        
        # Add groups to main layout
        layout.addWidget(groq_group)
        layout.addWidget(gmail_group)
        layout.addStretch()
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_api_key_btn.isChecked():
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_key_btn.setText("Show")
    
    def test_api_connection(self):
        """Test API connection"""
        # Implement API connection testing
        api_key = self.api_key_input.text().strip()
        if not api_key:
            return
        
        # Here you would test the Groq API connection
        # For now, just show a placeholder message
        self.test_api_btn.setText("Testing...")
        self.test_api_btn.setEnabled(False)
        
        # Simulate test (replace with actual API test)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.test_complete(True))
    
    def test_complete(self, success):
        """Handle test completion"""
        self.test_api_btn.setEnabled(True)
        if success:
            self.test_api_btn.setText("✓ Connected")
            self.test_api_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
            """)
        else:
            self.test_api_btn.setText("✗ Failed")
            self.test_api_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f38ba8;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
            """)
        
        # Reset after 3 seconds
        from PyQt6.QtCore import QTimer
        def reset_button():
            self.test_api_btn.setText("Test Connection")
            self.test_api_btn.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #94d3a2;
                }
            """)
        QTimer.singleShot(3000, reset_button)
    
    def browse_credentials_file(self):
        """Browse for credentials file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Gmail Credentials File",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.creds_path_input.setText(file_path)
            self.settings_changed.emit()
    
    def load_settings(self):
        """Load settings from configuration"""
        # Load from environment variables and config files
        api_key = os.getenv('GROQ_API_KEY', '')
        self.api_key_input.setText(api_key)
        
        # Load credentials path
        if os.path.exists('credentials.json'):
            self.creds_path_input.setText(os.path.abspath('credentials.json'))
    
    def save_settings(self):
        """Save current settings"""
        settings = QSettings()
        settings.setValue("groq_api_key", self.api_key_input.text())
        settings.setValue("groq_model", self.model_combo.currentText())
        settings.setValue("temperature", self.temperature_slider.value() / 100.0)
        settings.setValue("credentials_path", self.creds_path_input.text())
        settings.setValue("auto_load_emails", self.auto_load_checkbox.isChecked())
        
        # Also update environment variable
        os.environ['GROQ_API_KEY'] = self.api_key_input.text()
        
        self.settings_changed.emit()

class AppearanceTab(QWidget):
    """Appearance and UI settings tab"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the appearance settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Theme Settings
        theme_group = SettingsGroup("Theme & Appearance")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(12)
        
        # Theme selection
        theme_label = QLabel("Color Theme:")
        theme_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Auto (System)"])
        self.theme_combo.setCurrentText("Dark Theme")
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #45475a;
                color: #cdd6f4;
                border: 2px solid #585b70;
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 200px;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #89b4fa;
            }
        """)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        
        # Font size
        font_label = QLabel("Font Size:")
        font_label.setStyleSheet("color: #bac2de; font-weight: 500;")
        
        font_layout = QHBoxLayout()
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(10, 18)
        self.font_slider.setValue(14)
        self.font_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #45475a;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #89b4fa;
                border: none;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #89b4fa;
                border-radius: 4px;
            }
        """)
        
        self.font_value = QLabel("14px")
        self.font_value.setStyleSheet("color: #89b4fa; font-weight: 600; min-width: 40px;")
        self.font_slider.valueChanged.connect(
            lambda v: self.font_value.setText(f"{v}px")
        )
        
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(self.font_value)
        
        # Animation settings
        self.animations_checkbox = QCheckBox("Enable animations and transitions")
        self.animations_checkbox.setChecked(True)
        self.animations_checkbox.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #585b70;
                border-radius: 4px;
                background-color: #45475a;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addWidget(font_label)
        theme_layout.addLayout(font_layout)
        theme_layout.addWidget(self.animations_checkbox)
        
        # Chat Settings
        chat_group = SettingsGroup("Chat Interface")
        chat_layout = QVBoxLayout(chat_group)
        chat_layout.setSpacing(12)
        
        self.auto_speech_checkbox = QCheckBox("Enable text-to-speech for responses")
        self.auto_speech_checkbox.setChecked(True)
        self.auto_speech_checkbox.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #585b70;
                border-radius: 4px;
                background-color: #45475a;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        
        self.sound_notifications_checkbox = QCheckBox("Play sound notifications")
        self.sound_notifications_checkbox.setStyleSheet("""
            QCheckBox {
                color: #cdd6f4;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #585b70;
                border-radius: 4px;
                background-color: #45475a;
            }
            QCheckBox::indicator:checked {
                background-color: #89b4fa;
                border-color: #89b4fa;
            }
        """)
        
        chat_layout.addWidget(self.auto_speech_checkbox)
        chat_layout.addWidget(self.sound_notifications_checkbox)
        
        # Add groups to main layout
        layout.addWidget(theme_group)
        layout.addWidget(chat_group)
        layout.addStretch()
    
    def on_theme_changed(self, theme_name):
        """Handle theme change"""
        theme_map = {
            "Dark Theme": "dark",
            "Light Theme": "light",
            "Auto (System)": "auto"
        }
        theme = theme_map.get(theme_name, "dark")
        self.theme_changed.emit(theme)

class AboutTab(QWidget):
    """About and information tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the about tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # App info
        app_icon = QLabel("🤖")
        app_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon.setStyleSheet("font-size: 64px;")
        
        app_name = QLabel("Gmail RAG Assistant")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #cdd6f4;
            margin: 20px 0px;
        """)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 16px;
            color: #6c7086;
            margin-bottom: 20px;
        """)
        
        # Description
        description = QLabel("""
        <p style="text-align: center; line-height: 1.6;">
        An AI-powered desktop application that helps you manage and interact with your Gmail emails using advanced RAG (Retrieval-Augmented Generation) technology.
        </p>
        
        <p style="text-align: center; line-height: 1.6; margin-top: 20px;">
        <b>Key Features:</b><br>
        • Natural language email search and querying<br>
        • AI-powered email summarization and analysis<br>
        • Voice input and text-to-speech capabilities<br>
        • Modern, intuitive user interface<br>
        • Secure local email processing
        </p>
        """)
        description.setWordWrap(True)
        description.setStyleSheet("""
            color: #bac2de;
            font-size: 14px;
            max-width: 600px;
            background-color: #313244;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #585b70;
        """)
        
        # Credits
        credits = QLabel("""
        <p style="text-align: center;">
        <b>Powered by:</b><br>
        PyQt6 • Groq AI • FAISS • LangChain<br>
        Google Gmail API • Python
        </p>
        """)
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits.setStyleSheet("""
            color: #6c7086;
            font-size: 12px;
            margin-top: 20px;
        """)
        
        layout.addWidget(app_icon)
        layout.addWidget(app_name)
        layout.addWidget(version_label)
        layout.addWidget(description)
        layout.addWidget(credits)
        layout.addStretch()

class SettingsInterface(QWidget):
    """Main settings interface with tabbed layout"""
    
    theme_changed = pyqtSignal(str)
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Set up the settings interface UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
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
        
        title_label = QLabel("Settings & Configuration")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #cdd6f4;
        """)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #94d3a2;
            }
        """)
        self.save_button.clicked.connect(self.save_all_settings)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.save_button)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                background-color: #1e1e2e;
                border: none;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #bac2de;
                padding: 12px 20px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: 500;
            }
            QTabBar::tab:hover {
                background-color: #494d64;
                color: #cdd6f4;
            }
            QTabBar::tab:selected {
                background-color: #89b4fa;
                color: white;
                font-weight: 600;
            }
        """)
        
        # Create tabs
        self.api_tab = APIConfigurationTab()
        self.appearance_tab = AppearanceTab()
        self.about_tab = AboutTab()
        
        self.tab_widget.addTab(self.api_tab, "🔑  API & Integration")
        self.tab_widget.addTab(self.appearance_tab, "🎨  Appearance")
        self.tab_widget.addTab(self.about_tab, "ℹ️  About")
        
        # Add to main layout
        layout.addWidget(header)
        layout.addWidget(self.tab_widget)
    
    def connect_signals(self):
        """Connect tab signals"""
        self.api_tab.settings_changed.connect(self.settings_changed.emit)
        self.appearance_tab.theme_changed.connect(self.theme_changed.emit)
    
    def save_all_settings(self):
        """Save all settings"""
        self.api_tab.save_settings()
        
        # Visual feedback
        original_text = self.save_button.text()
        self.save_button.setText("✓ Saved!")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 14px;
            }
        """)
        
        # Reset after 2 seconds
        from PyQt6.QtCore import QTimer
        def reset_save_button():
            self.save_button.setText(original_text)
            self.save_button.setStyleSheet("""
                QPushButton {
                    background-color: #a6e3a1;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-weight: 600;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #94d3a2;
                }
            """)
        QTimer.singleShot(2000, reset_save_button)
        
        self.settings_changed.emit()