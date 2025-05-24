import speech_recognition as sr
import logging

class WakeWordDetector:
    def __init__(self, wake_word="hey awesome", callback=None):
        """Initialize wake word detector"""
        # Setup logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Initialize components
        self.wake_word = wake_word.lower()
        self.callback = callback
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Lower threshold for better detection
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        self.running = True
        
    def start(self):
        """Start listening for wake word"""
        self.running = True
        self.logger.info("Wake word detector started")
        self.detect()
        
    def stop(self):
        """Stop listening for wake word"""
        self.running = False
        self.logger.info("Wake word detector stopped")
        
    def detect(self):
        """Listen for wake word"""
        try:
            with sr.Microphone() as source:
                self.logger.info("Listening for wake word...")
                
                while self.running:
                    try:
                        # Listen for audio
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                        
                        try:
                            # Convert speech to text
                            text = self.recognizer.recognize_google(audio).lower()
                            self.logger.info(f"Heard: {text}")
                            
                            # Check for wake word
                            if self.wake_word in text:
                                self.logger.info("Wake word detected!")
                                if self.callback:
                                    self.callback()
                                return True
                                
                        except sr.UnknownValueError:
                            # Speech was unintelligible
                            continue
                        except sr.RequestError as e:
                            self.logger.error(f"Could not request results; {e}")
                            continue
                            
                    except sr.WaitTimeoutError:
                        # Timeout occurred, continue listening
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error in wake word detection: {e}")
            return False
            
        return False
