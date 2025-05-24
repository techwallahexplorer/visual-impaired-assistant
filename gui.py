import sys
import logging
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath

class AssistantWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize window
        self.setWindowTitle("Awesome Assistant")
        self.setGeometry(100, 100, 400, 200)
        
        # Make window frameless and transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create status label
        self.status_label = QLabel("Say 'Hey Awesome' to start")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-family: Arial;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px;
                border-radius: 10px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Create response label
        self.response_label = QLabel("")
        self.response_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-family: Arial;
                background-color: rgba(0, 0, 0, 120);
                padding: 10px;
                border-radius: 10px;
            }
        """)
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.response_label.setWordWrap(True)
        layout.addWidget(self.response_label)
        
        # Animation properties
        self.pulse_radius = 50
        self.pulse_opacity = 1.0
        self.pulse_growing = True
        
        # Setup animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_pulse)
        self.animation_timer.start(50)  # 50ms = 20fps
        
        # Track mouse for dragging
        self.dragging = False
        self.drag_position = None
        
    def update_pulse(self):
        """Update pulse animation"""
        try:
            if self.pulse_growing:
                self.pulse_radius += 1
                self.pulse_opacity -= 0.02
                if self.pulse_radius >= 60:
                    self.pulse_growing = False
            else:
                self.pulse_radius -= 1
                self.pulse_opacity += 0.02
                if self.pulse_radius <= 40:
                    self.pulse_growing = True
                    
            self.pulse_opacity = max(0.4, min(1.0, self.pulse_opacity))
            self.update()  # Trigger repaint
            
        except Exception as e:
            self.logger.error(f"Error in pulse animation: {e}")
            
    def paintEvent(self, event):
        """Paint the window background and pulse animation"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw pulse circle
            center = QPoint(self.width() // 2, 60)
            color = QColor(0, 122, 255, int(255 * self.pulse_opacity))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            
            # Draw main circle
            painter.drawEllipse(center, self.pulse_radius, self.pulse_radius)
            
            # Draw inner circle
            inner_color = QColor(0, 122, 255, 255)
            painter.setBrush(inner_color)
            painter.drawEllipse(center, 30, 30)
            
        except Exception as e:
            self.logger.error(f"Error in paint event: {e}")
            
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            
    def update_status(self, text):
        """Update status label text"""
        try:
            self.status_label.setText(text)
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
            
    def update_response(self, text):
        """Update response label text"""
        try:
            self.response_label.setText(text)
        except Exception as e:
            self.logger.error(f"Error updating response: {e}")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec())
