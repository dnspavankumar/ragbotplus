"""
Modern UI Components for Gmail RAG Assistant
This module provides reusable modern UI components
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QGraphicsOpacityEffect, QProgressBar
)
from PyQt6.QtCore import (
    QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, 
    QRect, QPoint, QSize, Qt, QThread, QByteArray
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPixmap, QIcon

class NotificationToast(QWidget):
    """Modern notification toast widget"""
    
    def __init__(self, message, notification_type="info", parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.notification_type = notification_type
        self.setup_ui(message)
        
        # Animation setup
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        opacity_property = QByteArray()
        opacity_property.append(b"opacity")
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, opacity_property)
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, opacity_property)
        
        # Auto-hide timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_notification)
        
    def setup_ui(self, message):
        self.setFixedSize(350, 80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon based on notification type
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✕",
            "info": "ℹ"
        }
        
        icon_label.setText(icons.get(self.notification_type, "ℹ"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {"#a6e3a1" if self.notification_type == "success" else 
                   "#f9e2af" if self.notification_type == "warning" else
                   "#f38ba8" if self.notification_type == "error" else "#89b4fa"};
        """)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            font-size: 14px;
            color: #cdd6f4;
            font-weight: 500;
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        
        # Style the toast
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #313244;
                border: 1px solid #585b70;
                border-radius: 12px;
            }}
        """)
    
    def show_notification(self, duration=3000):
        """Show the notification with fade-in animation"""
        self.show()
        
        # Fade in
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.fade_in_animation.start()
        
        # Start auto-hide timer
        self.timer.start(duration)
    
    def hide_notification(self):
        """Hide the notification with fade-out animation"""
        self.timer.stop()
        
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InQuart)
        self.fade_out_animation.finished.connect(self.hide)
        self.fade_out_animation.start()

class LoadingSpinner(QWidget):
    """Modern loading spinner widget"""
    
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.spinner_size = size
        self.setFixedSize(size, size)
        
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def start_spinning(self):
        """Start the spinning animation"""
        self.timer.start(50)  # 20 FPS
        self.show()
    
    def stop_spinning(self):
        """Stop the spinning animation"""
        self.timer.stop()
        self.hide()
    
    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, a0):
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set up the pen
        pen = QPen(QColor("#89b4fa"))
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw the spinner
        rect = QRect(5, 5, self.spinner_size - 10, self.spinner_size - 10)
        painter.drawArc(rect, self.angle * 16, 120 * 16)

class ModernProgressBar(QProgressBar):
    """Custom modern progress bar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #45475a;
                border: none;
                border-radius: 8px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #89b4fa, stop:1 #74c7ec);
                border-radius: 8px;
            }
        """)

class ChatBubble(QFrame):
    """Modern chat message bubble"""
    
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setup_ui(message)
    
    def setup_ui(self, message):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if self.is_user:
            message_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.setStyleSheet("""
                QFrame {
                    background-color: #89b4fa;
                    border-radius: 18px 18px 4px 18px;
                    margin: 8px 60px 8px 20px;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                    line-height: 1.4;
                }
            """)
        else:
            message_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.setStyleSheet("""
                QFrame {
                    background-color: #45475a;
                    border-radius: 18px 18px 18px 4px;
                    margin: 8px 20px 8px 60px;
                }
                QLabel {
                    color: #cdd6f4;
                    font-size: 14px;
                    line-height: 1.4;
                }
            """)
        
        layout.addWidget(message_label)

class TypingIndicator(QFrame):
    """Animated typing indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_dots)
        self.dot_count = 0
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        self.label = QLabel("Assistant is typing")
        self.label.setStyleSheet("""
            color: #6c7086;
            font-size: 14px;
            font-style: italic;
        """)
        
        layout.addWidget(self.label)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #45475a;
                border-radius: 18px;
                margin: 8px 20px 8px 60px;
            }
        """)
    
    def start_animation(self):
        """Start the typing animation"""
        self.animation_timer.start(500)
        self.show()
    
    def stop_animation(self):
        """Stop the typing animation"""
        self.animation_timer.stop()
        self.hide()
    
    def animate_dots(self):
        """Animate the typing dots"""
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.label.setText(f"Assistant is typing{dots}")

class ModernCard(QFrame):
    """Modern card widget with shadow effect"""
    
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        self.setup_ui(title, content)
    
    def setup_ui(self, title, content):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 1px solid #585b70;
                border-radius: 12px;
                margin: 8px;
                padding: 16px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: 600;
                color: #cdd6f4;
                margin-bottom: 8px;
            """)
            layout.addWidget(title_label)
        
        if content:
            content_label = QLabel(content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet("""
                font-size: 14px;
                color: #bac2de;
                line-height: 1.4;
            """)
            layout.addWidget(content_label)

class EmailCard(ModernCard):
    """Specialized card for displaying email information"""
    
    clicked = pyqtSignal(dict)
    
    def __init__(self, email_data, parent=None):
        self.email_data = email_data
        super().__init__(parent=parent)
        self.setup_email_ui()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def setup_email_ui(self):
        """Set up the email-specific UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Subject
        subject = self.email_data.get('subject', 'No Subject')
        subject_label = QLabel(subject)
        subject_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #cdd6f4;
            margin-bottom: 4px;
        """)
        layout.addWidget(subject_label)
        
        # From
        from_email = self.email_data.get('from', 'Unknown')
        from_label = QLabel(f"From: {from_email}")
        from_label.setStyleSheet("""
            font-size: 12px;
            color: #89b4fa;
            margin-bottom: 4px;
        """)
        layout.addWidget(from_label)
        
        # Date
        date = self.email_data.get('date', '')
        date_label = QLabel(date)
        date_label.setStyleSheet("""
            font-size: 12px;
            color: #6c7086;
            margin-bottom: 8px;
        """)
        layout.addWidget(date_label)
        
        # Preview
        preview = self.email_data.get('preview', '')[:100] + "..." if len(self.email_data.get('preview', '')) > 100 else self.email_data.get('preview', '')
        preview_label = QLabel(preview)
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet("""
            font-size: 14px;
            color: #bac2de;
            line-height: 1.3;
        """)
        layout.addWidget(preview_label)
    
    def mousePressEvent(self, a0):
        """Handle mouse click"""
        if a0 is not None and a0.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.email_data)
        super().mousePressEvent(a0)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.setStyleSheet(self.styleSheet() + """
            QFrame {
                background-color: #494d64;
                border-color: #89b4fa;
            }
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, a0):
        """Handle mouse leave"""
        self.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border: 1px solid #585b70;
                border-radius: 12px;
                margin: 8px;
                padding: 16px;
            }
        """)
        super().leaveEvent(a0)

class NotificationManager:
    """Manages notification toasts"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.notifications = []
    
    def show_notification(self, message, notification_type="info", duration=3000):
        """Show a notification toast"""
        toast = NotificationToast(message, notification_type, self.parent)
        
        # Position the toast
        parent_rect = self.parent.geometry()
        toast_x = parent_rect.right() - toast.width() - 20
        toast_y = parent_rect.top() + 20 + (len(self.notifications) * 90)
        
        toast.move(toast_x, toast_y)
        toast.show_notification(duration)
        
        self.notifications.append(toast)
        
        # Remove from list after hiding
        QTimer.singleShot(duration + 500, lambda: self.remove_notification(toast))
    
    def remove_notification(self, toast):
        """Remove a notification from the list"""
        if toast in self.notifications:
            self.notifications.remove(toast)
            toast.deleteLater()
            
            # Reposition remaining notifications
            for i, notification in enumerate(self.notifications):
                parent_rect = self.parent.geometry()
                toast_x = parent_rect.right() - notification.width() - 20
                toast_y = parent_rect.top() + 20 + (i * 90)
                notification.move(toast_x, toast_y)