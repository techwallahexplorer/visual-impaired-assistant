import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from awesome_assistant import AwesomeAssistant
from gui import AssistantWindow
from wake_word import WakeWordDetector

class AssistantThread(QThread):
    """Thread for running the assistant"""
    status_update = pyqtSignal(str)
    response_update = pyqtSignal(str)

    def __init__(self, window):
        super().__init__()
        self.window = window
        self.running = True
        self.assistant = AwesomeAssistant()
        self.wake_detector = WakeWordDetector(callback=self.on_wake_word)
        
    def run(self):
        """Main assistant loop"""
        try:
            # Start wake word detection
            self.wake_detector.start()
            
            # Initial greeting
            self.status_update.emit("Say 'Hey Awesome' to start")
            
            while self.running:
                try:
                    # Keep thread alive but don't consume CPU
                    self.msleep(100)
                except Exception as e:
                    print(f"Error in assistant loop: {e}")
                    
        except Exception as e:
            print(f"Critical error in assistant thread: {e}")
        finally:
            self.cleanup()
            
    def on_wake_word(self):
        """Handle wake word detection"""
        try:
            # Update status
            self.status_update.emit("Yes, I'm listening...")
            self.response_update.emit("")  # Clear previous response
            
            # Get command
            command = self.assistant.listen()
            if command:
                # Show what was heard
                self.status_update.emit(f"You said: {command}")
                
                # Execute command
                self.assistant.execute_command(command)
                
                # Reset status
                self.status_update.emit("Say 'Hey Awesome' to start")
                
        except Exception as e:
            print(f"Error handling wake word: {e}")
            self.status_update.emit("Say 'Hey Awesome' to start")
            
    def stop(self):
        """Stop the assistant thread"""
        self.running = False
        if hasattr(self, 'wake_detector'):
            self.wake_detector.stop()
            
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'wake_detector'):
                self.wake_detector.stop()
            if hasattr(self, 'assistant'):
                # Clean up assistant resources if needed
                pass
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    # Enable high DPI scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Enable High DPI display with Qt6
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # Create and show main window
    window = AssistantWindow()
    window.show()
    
    # Create and start assistant thread
    assistant_thread = AssistantThread(window)
    assistant_thread.status_update.connect(window.update_status)
    assistant_thread.response_update.connect(window.update_response)
    assistant_thread.start()
    
    # Run application
    result = app.exec()
    
    # Clean up
    assistant_thread.stop()
    assistant_thread.wait()
    sys.exit(result)

if __name__ == "__main__":
    main()