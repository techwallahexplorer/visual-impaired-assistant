import soundfile as sf
import numpy as np
import speech_recognition as sr
import time
from transformers import pipeline
from animation_window import initialize_animation_window, show_wake_animation

class WakeWordDetector:
    def __init__(self):
        self.wake_word = "hey awesome"
        self.recognizer = sr.Recognizer()
        self.animation_window = initialize_animation_window()
        # Enhanced recognition parameters for better accuracy and noise handling
        self.recognizer.energy_threshold = 3500  # Adjusted for better sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15  # Smoother energy level adjustments
        self.recognizer.dynamic_energy_ratio = 1.5  # Increased for better noise distinction
        self.recognizer.pause_threshold = 0.6  # Optimized for wake word detection
        self.recognizer.phrase_threshold = 0.3  # Shorter phrases are ignored
        self.recognizer.non_speaking_duration = 0.4  # Faster response to wake word
        self.nlp = pipeline("text-classification", model="distilbert-base-uncased", device="cpu")  # Explicit CPU usage
        
    def detect(self, wake_word=None, max_retries=50, no_response_timeout=60):
        with sr.Microphone() as source:
            print("Listening for wake word...")
            try:
                # Enhanced ambient noise adjustment
                print("Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduced calibration time
                print("Calibration complete")
                
                retry_count = 0
                last_activity_time = time.time()
                
                while retry_count < max_retries:  # Limited retry attempts
                    try:
                        print("Ready for wake word...")
                        audio = self.recognizer.listen(
                            source,
                            timeout=1.0,  # Reduced timeout for faster response
                            phrase_time_limit=1.5  # Adjusted for wake word length
                        )
                        
                        # Update activity time when audio is detected
                        last_activity_time = time.time()
                        
                        # Check for inactivity timeout
                        if time.time() - last_activity_time > no_response_timeout:
                            print("No activity detected for too long, stopping wake word detection")
                            return False
                        
                        try:
                            # Try Google Speech Recognition
                            text = self.recognizer.recognize_google(audio).lower()
                            print(f"Heard: {text}")
                            
                            # Enhanced wake word variation detection
                            wake_variations = [
                                "hey awesome",
                                "hi awesome",
                                "hello awesome",
                                "hay awesome",
                                "hey awsome",
                            ]
                            
                            # Improved matching logic with exact and partial matches
                            text_words = text.split()
                            for variation in wake_variations:
                                variation_words = variation.split()
                                if all(word in text_words for word in variation_words) and \
                                   abs(len(text_words) - len(variation_words)) <= 1:
                                    print(f"Wake word detected: {text}")
                                    show_wake_animation()
                                    return True
                            
                            # Additional check for close matches
                            if any(variation.replace(" ", "") in text.replace(" ", "") for variation in wake_variations):
                                print(f"Close wake word match detected: {text}")
                                show_wake_animation()
                                return True
                                
                        except sr.UnknownValueError:
                            retry_count += 1
                            if retry_count >= max_retries:
                                print("Maximum retry attempts reached")
                                return False
                            continue
                        except sr.RequestError:
                            print("Could not request results; check your internet connection")
                            retry_count += 1
                            if retry_count >= max_retries:
                                print("Maximum retry attempts reached")
                                return False
                            continue
                            
                    except sr.WaitTimeoutError:
                        retry_count += 1
                        if retry_count >= max_retries:
                            print("Maximum retry attempts reached")
                            return False
                        continue
                        
                print("Detection timeout reached")
                return False
                        
            except KeyboardInterrupt:
                print("\nStopping wake word detection...")
                return False
            except Exception as e:
                print(f"Error in wake word detection: {str(e)}")
                return False