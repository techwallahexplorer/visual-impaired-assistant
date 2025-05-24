import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread
from awesome_assistant import AwesomeAssistant
import pystray
from PIL import Image
import threading
import os

class AssistantThread(QThread):
    def __init__(self):
        super().__init__()
        self.assistant = AwesomeAssistant()
        self.running = True

    def run(self):
        print("Awesome Assistant is ready! Say 'hey awesome' to wake me up.")
        while self.running:
            try:
                # Listen for wake word
                if self.assistant.wake_word_detector.listen_for_wake_word():
                    # Wake word detected, greet the user
                    self.assistant.speak(self.assistant.get_response('greeting', 'en').format(self.assistant.name))
                    
                    # Listen for command
                    command = self.assistant.listen()
                    if command:
                        # Execute the command
                        self.assistant.execute_command(command)
            except Exception as e:
                print(f"Error: {str(e)}")

    def stop(self):
        self.running = False
        self.wait()

class SystemTrayIcon:
    def __init__(self, assistant):
        self.assistant = assistant
        self.icon = None
        self.is_running = True
        
    def create_icon(self):
        # Create a simple icon (you can replace this with your own .ico file)
        icon_path = os.path.join(os.path.dirname(__file__), "awesome_icon.png")
        if not os.path.exists(icon_path):
            # Create a simple colored image if icon doesn't exist
            img = Image.new('RGB', (64, 64), color='purple')
            img.save(icon_path)
        
        image = Image.open(icon_path)
        
        menu = (
            pystray.MenuItem("Activate Assistant", self.activate_assistant),
            pystray.MenuItem("Exit", self.stop_assistant)
        )
        
        self.icon = pystray.Icon("Awesome Assistant", image, "Awesome Assistant", menu)
        
    def activate_assistant(self, icon, item):
        # This simulates the wake word being detected
        self.assistant.speak("Yes, I'm listening")
        command = self.assistant.listen()
        if command:
            print(f"You said: {command}")
            self.assistant.execute_command(command)
    
    def stop_assistant(self, icon, item):
        self.is_running = False
        icon.stop()
        
    def run(self):
        self.create_icon()
        self.icon.run()

class SystemTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tray_icon = QSystemTrayIcon()
        self.assistant_thread = None
        self.system_tray_icon = SystemTrayIcon(AssistantThread().assistant)
        self.setup_tray()

    def setup_tray(self):
        # Create the tray icon
        self.tray_icon.setIcon(QIcon("icon.svg"))
        self.tray_icon.setToolTip('Awesome Assistant')

        # Create the menu
        menu = QMenu()
        start_action = menu.addAction('Start Assistant')
        stop_action = menu.addAction('Stop Assistant')
        exit_action = menu.addAction('Exit')

        # Connect actions
        start_action.triggered.connect(self.start_assistant)
        stop_action.triggered.connect(self.stop_assistant)
        exit_action.triggered.connect(self.exit_app)

        # Set the menu
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def start_assistant(self):
        if not self.assistant_thread or not self.assistant_thread.isRunning():
            self.assistant_thread = AssistantThread()
            self.assistant_thread.start()
            self.tray_icon.showMessage('Awesome Assistant', 'Assistant is now active and listening', QSystemTrayIcon.MessageIcon.Information)
            self.system_tray_icon.run()

    def stop_assistant(self):
        if self.assistant_thread and self.assistant_thread.isRunning():
            self.assistant_thread.stop()
            self.tray_icon.showMessage('Awesome Assistant', 'Assistant has been stopped', QSystemTrayIcon.MessageIcon.Information)

    def exit_app(self):
        if self.assistant_thread:
            self.assistant_thread.stop()
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        # Start the assistant automatically when the app launches
        self.start_assistant()
        sys.exit(self.app.exec())

if __name__ == '__main__':
    app = SystemTrayApp()
    app.run()