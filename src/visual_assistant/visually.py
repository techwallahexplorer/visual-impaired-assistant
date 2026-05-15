import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import speech_recognition as sr
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import time
import sys
import pyttsx3
from colorama import init, Fore, Back, Style
from googletrans import Translator
from indicnlp.tokenize import indic_tokenize

# Download required NLTK resources
required_resources = [
    'punkt',
    'averaged_perceptron_tagger',
    'maxent_ne_chunker',
    'words',
    'vader_lexicon'
]

for resource in required_resources:
    try:
        nltk.download(resource, quiet=True)
    except Exception as e:
        print(f"Warning: Could not download {resource}: {e}")

def initialize_nltk():
    """Initialize NLTK resources"""
    required_resources = [
        'punkt',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'vader_lexicon'
    ]

    for resource in required_resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {resource}: {e}")

def initialize_components():
    """Initialize colorama, translator, and NLTK components"""
    init()
    translator = Translator()
    try:
        sentiment_analyzer = SentimentIntensityAnalyzer()
    except Exception as e:
        print(f"Warning: Could not initialize sentiment analyzer: {e}")
        sentiment_analyzer = None
    return translator, sentiment_analyzer

# Initialize components
translator, sentiment_analyzer = initialize_components()

# Define POS tag descriptions
POS_DESCRIPTIONS = {
    'CC': 'Coordinating conjunction',
    'CD': 'Cardinal number',
    'DT': 'Determiner',
    'EX': 'Existential there',
    'FW': 'Foreign word',
    'IN': 'Preposition/subordinating conjunction',
    'JJ': 'Adjective',
    'JJR': 'Adjective, comparative',
    'JJS': 'Adjective, superlative',
    'LS': 'List item marker',
    'MD': 'Modal',
    'NN': 'Noun, singular',
    'NNS': 'Noun, plural',
    'NNP': 'Proper noun, singular',
    'NNPS': 'Proper noun, plural',
    'PDT': 'Predeterminer',
    'POS': 'Possessive ending',
    'PRP': 'Personal pronoun',
    'PRP$': 'Possessive pronoun',
    'RB': 'Adverb',
    'RBR': 'Adverb, comparative',
    'RBS': 'Adverb, superlative',
    'RP': 'Particle',
    'TO': 'to',
    'UH': 'Interjection',
    'VB': 'Verb, base form',
    'VBD': 'Verb, past tense',
    'VBG': 'Verb, gerund/present participle',
    'VBN': 'Verb, past participle',
    'VBP': 'Verb, non-3rd person singular present',
    'VBZ': 'Verb, 3rd person singular present',
    'WDT': 'Wh-determiner',
    'WP': 'Wh-pronoun',
    'WP$': 'Possessive wh-pronoun',
    'WRB': 'Wh-adverb'
}


class VisuallyImpairedAssistant:
    def speak(self, text, is_hindi=False):
        """Speak the given text and print it with formatting"""
        # Print with formatting
        print(f"{Fore.GREEN}╔{'═' * 78}╗{Style.RESET_ALL}")
        words = text.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 76:  # Account for margins
                current_line += word + " "
            else:
                print(f"{Fore.GREEN}║{Style.RESET_ALL} {current_line:<76} {Fore.GREEN}║{Style.RESET_ALL}")
                current_line = word + " "
        if current_line:
            print(f"{Fore.GREEN}║{Style.RESET_ALL} {current_line:<76} {Fore.GREEN}║{Style.RESET_ALL}")
        print(f"{Fore.GREEN}╚{'═' * 78}╝{Style.RESET_ALL}")
        
        try:
            # If text is in Hindi, translate it for speech
            if is_hindi:
                try:
                    translated = translator.translate(text, src='hi', dest='en')
                    speak_text = translated.text
                except:
                    speak_text = text  # Fallback to original text if translation fails
            else:
                speak_text = text

            # Speak the text
            self.engine.say(speak_text)
            self.engine.runAndWait()
        except RuntimeError:
            # If the engine is stuck, reinitialize it
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            self.engine.say(speak_text)
            self.engine.runAndWait()

    def __init__(self):
        # Initialize NLTK
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Error initializing NLTK: {e}")
            sys.exit(1)

        # Initialize Firebase
        try:
            cred = credentials.Certificate('hi.json')
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://nlppro-c23bc-default-rtdb.firebaseio.com'
            })
            self.ref = db.reference('processed_text')
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            sys.exit(1)

        # Initialize Text-to-Speech engine
        try:
            self.engine = pyttsx3.init()
            # Set properties for better clarity
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level
        except Exception as e:
            print(f"{Fore.RED}Error initializing text-to-speech: {e}{Style.RESET_ALL}")
            sys.exit(1)

        # Initialize Speech Recognizer
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            # List available audio devices
            self.speak("Checking available audio devices")
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                self.speak(f"Found device {i}: {dev['name']}")
            p.terminate()

            self.recognizer = sr.Recognizer()
            # Test microphone initialization
            with sr.Microphone() as source:
                self.speak("Microphone initialized successfully")

        except Exception as e:
            self.speak(f"Error initializing audio system: {e}. Please ensure PyAudio is installed and microphone is connected.")
            sys.exit(1)

        # Adjust for ambient noise duration
        self.ambient_duration = 2
        # Maximum listening duration
        self.listen_timeout = 5
        # Maximum phrase duration
        self.phrase_timeout = 10

    def capture_speech(self):
        """Capture speech input from microphone with Hindi support"""
        try:
            # Try to use default microphone first
            with sr.Microphone() as source:
                self.speak("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=self.ambient_duration)
                self.speak("Listening... Speak now in English or Hindi.")
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout
                )

                try:
                    # Try to recognize Hindi first
                    text = self.recognizer.recognize_google(audio, language='hi-IN')
                    is_hindi = True
                except:
                    # If Hindi recognition fails, try English
                    try:
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        is_hindi = False
                    except sr.UnknownValueError:
                        self.speak("Sorry, I couldn't understand the audio.")
                        return None, False
                    except sr.RequestError as e:
                        self.speak(f"Error with the speech recognition service: {e}")
                        return None, False

                if text:
                    self.speak(f"You said: {text}", is_hindi)
                    return text, is_hindi

        except Exception as e:
            self.speak(f"Error capturing audio: {e}. Make sure your microphone is properly connected and enabled.")
            return None, False

    def process_text(self, text, is_hindi=False):
        """Process text and generate descriptions for visually impaired with Hindi support"""
        try:
            description = []
            
            # If text is in Hindi, translate to English for processing
            if is_hindi:
                translated = translator.translate(text, src='hi', dest='en')
                eng_text = translated.text
                description.append(f"Translation: {eng_text}")
            else:
                eng_text = text

            try:
                # Tokenize into sentences and words
                sentences = sent_tokenize(eng_text)
                description.append(f"Number of sentences: {len(sentences)}")

                # Process each sentence
                for i, sentence in enumerate(sentences, 1):
                    description.append(f"\nAnalyzing sentence {i}: {sentence}")
                    
                    try:
                        # Detailed NLTK analysis
                        tokens = word_tokenize(sentence)
                        tagged = pos_tag(tokens)

                        # Categorize words by type
                        word_types = {}
                        for word, tag in tagged:
                            if tag in POS_DESCRIPTIONS:
                                category = POS_DESCRIPTIONS[tag]
                                if category not in word_types:
                                    word_types[category] = []
                                word_types[category].append(word)

                        # Add word type analysis to description
                        for category, words in word_types.items():
                            if words:
                                description.append(f"{category}: {', '.join(words)}")

                        try:
                            # Named Entity Recognition
                            named_entities = ne_chunk(tagged)
                            entities = []
                            for chunk in named_entities:
                                if hasattr(chunk, 'label'):
                                    entity_text = ' '.join(c[0] for c in chunk)
                                    entities.append(f"{chunk.label()}: {entity_text}")
                            if entities:
                                description.append(f"Named Entities found: {', '.join(entities)}")
                        except Exception as e:
                            description.append("Note: Named Entity Recognition unavailable")

                        # VADER Sentiment Analysis
                        if sentiment_analyzer:
                            try:
                                sentiment_scores = sentiment_analyzer.polarity_scores(sentence)
                                compound_score = sentiment_scores['compound']
                                
                                # Determine sentiment description
                                if compound_score >= 0.05:
                                    sentiment_desc = "positive"
                                elif compound_score <= -0.05:
                                    sentiment_desc = "negative"
                                else:
                                    sentiment_desc = "neutral"

                                description.append(f"Sentiment Analysis:")
                                description.append(f"- Overall: {sentiment_desc} (score: {compound_score:.2f})")
                                description.append(f"- Positive: {sentiment_scores['pos']:.2f}")
                                description.append(f"- Negative: {sentiment_scores['neg']:.2f}")
                                description.append(f"- Neutral: {sentiment_scores['neu']:.2f}")
                            except Exception as e:
                                description.append("Note: Detailed sentiment analysis unavailable")
                    except Exception as e:
                        description.append(f"Note: Could not fully analyze sentence {i}")

            except Exception as e:
                description.append("Note: Basic text analysis unavailable")
                # Fallback to simple word tokenization
                words = text.split()
                description.append(f"Words found: {', '.join(words)}")

            # Speak each description with appropriate language
            for desc in description:
                self.speak(desc, is_hindi)

            return description
        except Exception as e:
            self.speak(f"Error processing text: {e}")
            return None

    def store_in_firebase(self, data):
        """Store processed data in Firebase"""
        try:
            entry_id = int(time.time())
            self.ref.child(f'entry_{entry_id}').set({
                'description': data,
                'raw_text': data.get('raw_text', ''),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'processed': data.get('processed', [])
            })
            return True
        except Exception as e:
            print(f"Error storing data in Firebase: {e}")
            return False

    def run(self):
        """Main execution loop"""
        self.speak("Visually Impaired Assistant Started. You can speak in English or Hindi. Press Ctrl+C to exit.")

        max_retries = 3  # Maximum number of consecutive errors before pausing
        retry_count = 0
        retry_delay = 5  # Seconds to wait after errors

        try:
            while True:
                try:
                    # Capture speech
                    spoken_text, is_hindi = self.capture_speech()

                    if spoken_text:
                        # Reset retry count on successful capture
                        retry_count = 0

                        # Process the text
                        processed_data = self.process_text(spoken_text, is_hindi)

                        if processed_data:
                            # Prepare data for storage
                            data = {
                                'raw_text': spoken_text,
                                'processed': processed_data
                            }

                            # Store in Firebase
                            if self.store_in_firebase(data):
                                self.speak("Processed Description:")
                                for desc in processed_data:
                                    self.speak(desc)
                                self.speak("Data stored in Firebase successfully.")
                            else:
                                self.speak("Failed to store data in Firebase.")
                        else:
                            self.speak("Failed to process the text.")
                    else:
                        # Increment retry count on failed capture
                        retry_count += 1
                        if retry_count >= max_retries:
                            self.speak(f"Too many errors. Waiting {retry_delay} seconds before trying again...")
                            time.sleep(retry_delay)
                            retry_count = 0

                    self.speak("Ready for next input...")
                    time.sleep(1)  # Small delay between attempts

                except Exception as e:
                    self.speak(f"Error in main loop: {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.speak(f"Too many errors. Waiting {retry_delay} seconds before trying again...")
                        time.sleep(retry_delay)
                        retry_count = 0

        except KeyboardInterrupt:
            self.speak("Exiting the application...")
            sys.exit(0)


def main():
    """Main entry point for the application"""
    try:
        # Initialize NLTK resources
        initialize_nltk()
        
        # Create and run assistant
        assistant = VisuallyImpairedAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())