"""
Modern UI Styles for Gmail RAG Assistant
This module provides beautiful dark/light themes and modern styling
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class ModernStyles:
    
    # Color Schemes
    DARK_THEME = {
        'primary': '#1e1e2e',          # Main background
        'secondary': '#313244',        # Secondary panels
        'accent': '#89b4fa',           # Accent color (blue)
        'accent_hover': '#74c7ec',     # Hover accent
        'surface': '#45475a',          # Surface elements
        'text_primary': '#cdd6f4',     # Primary text
        'text_secondary': '#bac2de',   # Secondary text
        'text_muted': '#6c7086',       # Muted text
        'success': '#a6e3a1',          # Success green
        'warning': '#f9e2af',          # Warning yellow
        'error': '#f38ba8',            # Error red
        'border': '#585b70',           # Border color
        'hover': '#494d64',            # Hover background
        'selected': '#7f849c'          # Selected items
    }
    
    LIGHT_THEME = {
        'primary': '#ffffff',          # Main background
        'secondary': '#f5f5f5',        # Secondary panels
        'accent': '#2563eb',           # Accent color (blue)
        'accent_hover': '#1d4ed8',     # Hover accent
        'surface': '#e5e7eb',          # Surface elements
        'text_primary': '#111827',     # Primary text
        'text_secondary': '#374151',   # Secondary text
        'text_muted': '#6b7280',       # Muted text
        'success': '#059669',          # Success green
        'warning': '#d97706',          # Warning orange
        'error': '#dc2626',            # Error red
        'border': '#d1d5db',           # Border color
        'hover': '#f3f4f6',            # Hover background
        'selected': '#e5e7eb'          # Selected items
    }
    
    @staticmethod
    def get_main_stylesheet(theme='dark'):
        """Get the main application stylesheet"""
        colors = ModernStyles.DARK_THEME if theme == 'dark' else ModernStyles.LIGHT_THEME
        
        return f"""
        /* Main Application Window */
        QMainWindow {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        
        /* Central Widget */
        QWidget {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
            font-size: 14px;
        }}
        
        /* Sidebar Styling */
        .sidebar {{
            background-color: {colors['secondary']};
            border-right: 1px solid {colors['border']};
            padding: 20px 0px;
        }}
        
        /* Main Content Area */
        .main-content {{
            background-color: {colors['primary']};
            border-radius: 12px;
            margin: 10px;
        }}
        
        /* Modern Buttons */
        QPushButton {{
            background-color: {colors['accent']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['accent_hover']};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background-color: {colors['accent']};
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background-color: {colors['surface']};
            color: {colors['text_muted']};
        }}
        
        /* Secondary Buttons */
        .secondary-button {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
        }}
        
        .secondary-button:hover {{
            background-color: {colors['hover']};
            border-color: {colors['accent']};
        }}
        
        /* Sidebar Buttons */
        .sidebar-button {{
            background-color: transparent;
            color: {colors['text_primary']};
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            text-align: left;
            margin: 4px 12px;
            font-weight: 500;
        }}
        
        .sidebar-button:hover {{
            background-color: {colors['hover']};
        }}
        
        .sidebar-button:checked {{
            background-color: {colors['accent']};
            color: white;
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors['accent']};
            outline: none;
        }}
        
        /* Labels */
        QLabel {{
            color: {colors['text_primary']};
            font-size: 14px;
        }}
        
        .title-label {{
            font-size: 24px;
            font-weight: 700;
            color: {colors['text_primary']};
            margin-bottom: 8px;
        }}
        
        .subtitle-label {{
            font-size: 16px;
            font-weight: 600;
            color: {colors['text_secondary']};
            margin-bottom: 12px;
        }}
        
        .muted-label {{
            color: {colors['text_muted']};
            font-size: 12px;
        }}
        
        /* List Widget */
        QListWidget {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px;
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 12px;
            border-radius: 6px;
            margin: 2px 0px;
        }}
        
        QListWidget::item:hover {{
            background-color: {colors['hover']};
        }}
        
        QListWidget::item:selected {{
            background-color: {colors['accent']};
            color: white;
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {colors['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['text_muted']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['accent']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {colors['surface']};
            border: none;
            border-radius: 4px;
            text-align: center;
            color: {colors['text_primary']};
            font-weight: 600;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['accent']};
            border-radius: 4px;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors['secondary']};
            color: {colors['text_secondary']};
            border-top: 1px solid {colors['border']};
            padding: 4px;
        }}
        
        /* Tool Tips */
        QToolTip {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-weight: 600;
        }}
        
        QGroupBox::title {{
            color: {colors['text_primary']};
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px 0 8px;
        }}
        
        /* Combo Box */
        QComboBox {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 12px;
            min-width: 120px;
        }}
        
        QComboBox:hover {{
            border-color: {colors['accent']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            padding-right: 12px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {colors['text_muted']};
            border-top: none;
            border-right: none;
            width: 6px;
            height: 6px;
            transform: rotate(45deg);
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {colors['secondary']};
            color: {colors['text_secondary']};
            padding: 12px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['hover']};
            color: {colors['text_primary']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['accent']};
            color: white;
        }}
        """
    
    @staticmethod
    def get_chat_stylesheet(theme='dark'):
        """Get chat-specific stylesheet"""
        colors = ModernStyles.DARK_THEME if theme == 'dark' else ModernStyles.LIGHT_THEME
        
        return f"""
        /* Chat Message Containers */
        .user-message {{
            background-color: {colors['accent']};
            color: white;
            border-radius: 18px 18px 4px 18px;
            padding: 12px 16px;
            margin: 8px 60px 8px 20px;
            font-size: 14px;
            line-height: 1.4;
        }}
        
        .assistant-message {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border-radius: 18px 18px 18px 4px;
            padding: 12px 16px;
            margin: 8px 20px 8px 60px;
            font-size: 14px;
            line-height: 1.4;
        }}
        
        .system-message {{
            background-color: {colors['secondary']};
            color: {colors['text_muted']};
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px 20px;
            font-size: 12px;
            font-style: italic;
            text-align: center;
        }}
        
        /* Chat Input Area */
        .chat-input {{
            background-color: {colors['surface']};
            border: 2px solid {colors['border']};
            border-radius: 24px;
            padding: 12px 20px;
            font-size: 14px;
            margin: 10px;
        }}
        
        .chat-input:focus {{
            border-color: {colors['accent']};
        }}
        
        /* Send Button */
        .send-button {{
            background-color: {colors['accent']};
            border: none;
            border-radius: 20px;
            width: 40px;
            height: 40px;
            margin: 10px;
        }}
        
        .send-button:hover {{
            background-color: {colors['accent_hover']};
        }}
        
        /* Typing Indicator */
        .typing-indicator {{
            background-color: {colors['surface']};
            border-radius: 18px;
            padding: 12px 16px;
            margin: 8px 20px 8px 60px;
            color: {colors['text_muted']};
            font-style: italic;
        }}
        """
    
    @staticmethod
    def get_notification_stylesheet(theme='dark'):
        """Get notification toast stylesheet"""
        colors = ModernStyles.DARK_THEME if theme == 'dark' else ModernStyles.LIGHT_THEME
        
        return f"""
        .notification {{
            background-color: {colors['surface']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border']};
            border-radius: 12px;
            padding: 16px 20px;
            margin: 10px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .notification-success {{
            border-left: 4px solid {colors['success']};
        }}
        
        .notification-warning {{
            border-left: 4px solid {colors['warning']};
        }}
        
        .notification-error {{
            border-left: 4px solid {colors['error']};
        }}
        
        .notification-info {{
            border-left: 4px solid {colors['accent']};
        }}
        """