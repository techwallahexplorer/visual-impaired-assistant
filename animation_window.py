import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView

class AnimationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create web view for Lottie animation
        self.web_view = QWebEngineView(self)
        self.web_view.setFixedSize(300, 300)
        self.web_view.setStyleSheet("background: transparent;")
        self.setCentralWidget(self.web_view)
        
        # Load the Lottie animation HTML
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { background-color: transparent; margin: 0; }
            </style>
            <script src="https://unpkg.com/@dotlottie/player-component@2.7.12/dist/dotlottie-player.mjs" type="module"></script>
        </head>
        <body>
            <dotlottie-player
                src="https://lottie.host/ee04d6c3-d324-4397-9ec8-5af43b307f3d/H9L7slmmsg.lottie"
                background="transparent"
                speed="1"
                style="width: 300px; height: 300px"
                autoplay
            ></dotlottie-player>
        </body>
        </html>
        '''
        self.web_view.setHtml(html_content)
        
        # Set window size and position
        self.setFixedSize(300, 300)
        self.position_window()
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("audio-input-microphone"))
        self.tray_icon.setVisible(True)
        
        # Create tray menu
        tray_menu = QMenu()
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(app.quit)
        self.tray_icon.setContextMenu(tray_menu)
    
    def position_window(self):
        """Position the window in the top-right corner of the screen"""
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20,
                 screen.height() // 4)
    
    def show_animation(self):
        """Show the animation window and automatically hide after animation"""
        self.show()
        self.web_view.page().runJavaScript(
            'document.querySelector("dotlottie-player").play();'
        )
        # Hide window after animation duration (adjust as needed)
        QTimer.singleShot(2000, self.hide)

app = None
window = None

def initialize_animation_window():
    global app, window
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    window = AnimationWindow()
    return window

def show_wake_animation():
    """Show the wake word animation"""
    if window:
        window.show_animation()