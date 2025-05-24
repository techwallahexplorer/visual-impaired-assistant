import os
import sys
import logging
import threading
import queue
import pyttsx3
import speech_recognition as sr
from transformers import pipeline
from wake_word import WakeWordDetector

class AwesomeAssistant:
    def __init__(self):
        """Initialize the Awesome Assistant with all required components"""
        # Setup logging
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        try:
            # Initialize components
            self.name = "Awesome"
            self._initialize_core_components()
            self._initialize_ml_models()
            self._configure_voice()
            
            self.logger.info("Assistant initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing assistant: {e}")
            raise
            
    def _initialize_core_components(self):
        """Initialize core components with error handling"""
        try:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Initialize text-to-speech
            self.engine = pyttsx3.init()
            
            # Initialize command queue for thread safety
            self.command_queue = queue.Queue()
            self._lock = threading.Lock()
            
            self.logger.info("Core components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing core components: {e}")
            raise
            
    def listen(self):
        """Listen for user input with error handling"""
        try:
            with sr.Microphone() as source:
                self.logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.logger.info(f"Recognized: {text}")
                    return text
                except sr.UnknownValueError:
                    self.logger.info("Could not understand audio")
                    return None
                except sr.RequestError as e:
                    self.logger.error(f"Error with speech recognition service: {e}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error in listen function: {e}")
            return None
            
    def speak(self, text, lang='en'):
        """Speak text with error handling and threading safety"""
        try:
            with self._lock:  # Thread safety for voice engine
                self.logger.info(f"Speaking: {text}")
                if hasattr(self, 'gui_callback_fn'):
                    self.gui_callback_fn(text)
                
                # Handle different languages
                if lang != 'en':
                    voices = self.engine.getProperty('voices')
                    for voice in voices:
                        if lang in voice.languages:
                            self.engine.setProperty('voice', voice.id)
                            break
                
                self.engine.say(text)
                self.engine.runAndWait()
                
        except Exception as e:
            self.logger.error(f"Error in speak function: {e}")
            
    def execute_command(self, command):
        """Execute user command with improved response handling"""
        try:
            self.logger.info(f"Executing command: {command}")
            
            # Check if it's a question
            if any(q in command.lower() for q in ['what', 'why', 'how', 'when', 'where', 'who']):
                answer = self._handle_question(command)
                if answer:
                    self.speak(answer)
                    return
            
            # Handle other commands
            response = self._process_command(command)
            # Always speak the response if available
            if response:
                self.speak(response)
                return response
                
        except Exception as e:
            self.logger.error(f"Error executing command: {e}")
            self.speak("I'm sorry, I couldn't process that command.")
            
    def _process_command(self, command):
        """Process and execute a command"""
        try:
            command = command.lower()
            
            # Basic commands
            if 'hello' in command or 'hi' in command:
                return "Hello! How can I help you today?"
                
            elif 'how are you' in command:
                return "I'm doing well, thank you for asking! How can I assist you?"
                
            elif 'goodbye' in command or 'bye' in command:
                return "Goodbye! Have a great day!"
                
            elif 'thank you' in command or 'thanks' in command:
                return "You're welcome!"
                
            # System commands
            elif 'open' in command:
                if 'whatsapp' in command:
                    # Try multiple common WhatsApp installation paths
                    whatsapp_paths = [
                        os.path.expandvars('%LocalAppData%\\WhatsApp\\WhatsApp.exe'),
                        os.path.expandvars('%LocalAppData%\\Programs\\WhatsApp\\WhatsApp.exe'),
                        os.path.expandvars('%ProgramFiles%\\WindowsApps\\5319275A.WhatsAppDesktop_*\\WhatsApp.exe'),
                        os.path.expandvars('%ProgramFiles(x86)%\\WindowsApps\\5319275A.WhatsAppDesktop_*\\WhatsApp.exe')
                    ]
                    
                    for path in whatsapp_paths:
                        # Handle wildcard paths
                        if '*' in path:
                            import glob
                            matching_paths = glob.glob(path)
                            if matching_paths:
                                path = matching_paths[0]
                        
                        if os.path.exists(path):
                            try:
                                os.startfile(path)
                                return "Opening WhatsApp"
                            except Exception as e:
                                self.logger.error(f"Error opening WhatsApp: {e}")
                                continue
                    
                    return "I couldn't find WhatsApp on your system. Please make sure it's installed."
                elif 'settings' in command:
                    os.system('start ms-settings:')
                    return "Opening Windows Settings"
                elif 'chrome' in command:
                    os.startfile('chrome')
                    return "Opening Chrome"
                elif 'edge' in command:
                    os.startfile('msedge')
                    return "Opening Microsoft Edge"
                elif 'file explorer' in command or 'explorer' in command:
                    os.startfile('explorer')
                    return "Opening File Explorer"
                elif 'control panel' in command:
                    os.system('control panel')
                    return "Opening Control Panel"
                
            elif 'close' in command or 'stop' in command or 'exit' in command:
                if 'listening' in command:
                    return "stop_listening"
                
            return "I'm not sure how to help with that yet. Is there something else I can do for you?"
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return "I encountered an error processing your command."
            
    def _handle_question(self, question):
        """Handle questions with improved context and knowledge"""
        try:
            if not self.qa_pipeline:
                return "I'm sorry, I'm having trouble with my question answering system."
            
            # Get context from knowledge base
            context = self._get_relevant_context(question)
            
            # Use QA pipeline
            result = self.qa_pipeline(
                question=question,
                context=context,
                max_answer_length=100
            )
            
            return result['answer'] if result['score'] > 0.5 else None
            
        except Exception as e:
            self.logger.error(f"Error handling question: {e}")
            return None
            
    def _get_relevant_context(self, question):
        """Get relevant context for question answering"""
        # Add your knowledge base here
        knowledge_base = {
            "general": "I am an AI assistant called Awesome, designed to help with various tasks.",
            "capabilities": "I can answer questions, perform tasks, and help you with your computer.",
            "weather": "I can check the weather for you using online weather services.",
            "time": "I can tell you the current time and help you manage your schedule.",
        }
        
        # Find relevant context
        relevant_contexts = []
        for topic, context in knowledge_base.items():
            if any(word in question.lower() for word in topic.split()):
                relevant_contexts.append(context)
        
        return " ".join(relevant_contexts) if relevant_contexts else knowledge_base["general"]
        
    def gui_callback(self, callback_function):
        """Set the GUI callback function for updating the interface"""
        try:
            self.logger.info("Setting GUI callback function")
            self.gui_callback_fn = callback_function
        except Exception as e:
            self.logger.error(f"Error setting GUI callback: {e}")
            self.gui_callback_fn = None
            
    def _initialize_ml_models(self):
        """Initialize ML models with better question handling"""
        try:
            self.logger.info("Initializing ML models...")
            
            # Load models locally from cache if available
            cache_dir = "model_cache"
            os.makedirs(cache_dir, exist_ok=True)
            
            model_config = {
                "cache_dir": cache_dir,
                "local_files_only": True  # Try to use cached files first
            }
            
            try:
                # Initialize sentiment analyzer
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    **model_config
                )
            except Exception as e:
                self.logger.warning(f"Error loading sentiment analyzer, downloading: {e}")
                # Fallback to downloading
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            
            try:
                # Initialize QA pipeline
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="deepset/roberta-base-squad2",
                    **model_config
                )
            except Exception as e:
                self.logger.warning(f"Error loading QA pipeline, downloading: {e}")
                # Fallback to downloading
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="deepset/roberta-base-squad2"
                )
                
            # Download and cache models for future use
            self._cache_models()
            
        except Exception as e:
            self.logger.error(f"Error in ML model initialization: {e}")
            self._initialize_ml_models_fallback()
    
    def _cache_models(self):
        """Download and cache models for offline use"""
        try:
            cache_dir = "model_cache"
            models = [
                "distilbert-base-uncased-finetuned-sst-2-english",
                "deepset/roberta-base-squad2"
            ]
            
            for model in models:
                self.logger.info(f"Caching model: {model}")
                pipeline("question-answering", model=model, cache_dir=cache_dir)
                
        except Exception as e:
            self.logger.warning(f"Error caching models: {e}")
    
    def _initialize_ml_models_fallback(self):
        """Fallback initialization for ML models when primary initialization fails"""
        try:
            self.logger.warning("Using fallback ML model initialization")
            
            # Initialize with minimal settings
            model_config = {
                "device": "cpu",
                "low_cpu_mem_usage": True
            }
            
            # Try loading smaller models
            try:
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased",
                    **model_config
                )
            except:
                self.logger.error("Failed to load sentiment analyzer in fallback mode")
                self.sentiment_analyzer = None
                
            try:
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="distilbert-base-cased",
                    **model_config
                )
            except:
                self.logger.error("Failed to load QA pipeline in fallback mode")
                self.qa_pipeline = None
                
        except Exception as e:
            self.logger.error(f"Error in fallback ML model initialization: {e}")
            self.sentiment_analyzer = None
            self.qa_pipeline = None
            
    def _configure_voice(self):
        """Configure voice settings for a premium female voice similar to Siri"""
        try:
            # Get available voices
            voices = self.engine.getProperty('voices')
            self.logger.info(f"Found {len(voices)} voices")
            
            # Premium voice keywords (in order of preference)
            priority_keywords = [
                'samantha',  # Premium US female voice (similar to Siri)
                'eva',       # Premium female voice
                'zira',      # Microsoft Zira (high quality)
                'cortana',   # Microsoft Cortana
                'hazel',     # UK English female
                'amy',       # Premium British female
                'emma',      # Premium British female
                'female'     # Any female voice
            ]
            
            # Log available voices for debugging
            self.logger.info("Available voices:")
            for voice in voices:
                self.logger.info(f"- {voice.name} ({voice.id})")
            
            # Try to find a premium female voice
            female_voice = None
            for keyword in priority_keywords:
                for voice in voices:
                    if keyword in voice.name.lower():
                        female_voice = voice
                        self.logger.info(f"Selected premium voice: {voice.name} (matched keyword: {keyword})")
                        break
                if female_voice:
                    break
            
            # Set voice with optimized properties
            if female_voice:
                self.logger.info(f"Setting voice to: {female_voice.name}")
                self.engine.setProperty('voice', female_voice.id)
                
                # Configure properties for Siri-like voice
                self.engine.setProperty('rate', 175)     # Slightly faster for natural feel
                self.engine.setProperty('volume', 0.95)  # Clear volume
                self.engine.setProperty('pitch', 165)    # Balanced pitch for premium feel
                
                # Test voice
                self.engine.say("Hello, I'm your virtual assistant. How can I help you today?")
                self.engine.runAndWait()
            else:
                self.logger.warning("No premium voice found, checking Windows OneCore voices...")
                
                # Try Windows OneCore voices (often higher quality)
                onecore_found = False
                for voice in voices:
                    if 'onecore' in voice.id.lower():
                        self.logger.info(f"Found Windows OneCore voice: {voice.name}")
                        self.engine.setProperty('voice', voice.id)
                        onecore_found = True
                        break
                
                if not onecore_found and len(voices) > 1:
                    self.logger.info(f"Using alternative voice: {voices[1].name}")
                    self.engine.setProperty('voice', voices[1].id)
                else:
                    self.logger.warning("Using default voice")
                
                # Set properties for best possible quality
                self.engine.setProperty('rate', 170)
                self.engine.setProperty('volume', 0.9)
                self.engine.setProperty('pitch', 160)
            
        except Exception as e:
            self.logger.error(f"Error configuring voice: {e}")
            try:
                # Fallback to safe settings
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.8)
                self.engine.setProperty('pitch', 150)
            except Exception as fallback_error:
                self.logger.error(f"Error setting fallback voice properties: {fallback_error}")
                
        # Provide information about installing additional voices
        self.logger.info("\nTo install more premium voices:")
        self.logger.info("1. Open Windows Settings > Time & Language > Speech")
        self.logger.info("2. Click 'Add voices'")
        self.logger.info("3. Select and install additional voices")
        self.logger.info("4. Restart the application to use new voices")
        
if __name__ == "__main__":
    assistant = AwesomeAssistant()
    wake_word_detector = WakeWordDetector()
    while True:
        try:
            # Listen for wake word with timeout
            if wake_word_detector.detect(no_response_timeout=60):  
                assistant.speak("Yes, I'm listening")
                command = assistant.listen()
                if command:
                    print(f"You said: {command}")
                    response = assistant.execute_command(command)
                    if response == "stop_listening":
                        assistant.speak("Goodbye! Call me when you need me.")
                        break
        except Exception as e:
            print(f"Error: {str(e)}")
            continue