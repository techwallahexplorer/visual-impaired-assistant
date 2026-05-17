import os
import sys
import time
import logging
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import speech_recognition as sr
import pyttsx3
from colorama import init, Fore, Style

# ─────────────────────────────────────────────
# Structured logging — replaces bare print/TTS errors
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('visual_assistant.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Optional Firebase — never crashes the app
# ─────────────────────────────────────────────
firebase_admin = None
firebase_db = None
firebase_ref = None
FIREBASE_ENABLED = False

def _init_firebase():
    """Initialize Firebase from env var — gracefully optional."""
    global firebase_admin, firebase_db, firebase_ref, FIREBASE_ENABLED
    try:
        import firebase_admin as _fa
        from firebase_admin import credentials as _creds, db as _db

        # [FIX S1] Credential loaded from environment variable, NOT a committed file.
        # Set GOOGLE_APPLICATION_CREDENTIALS to the path of your service account JSON.
        cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        db_url    = os.environ.get('FIREBASE_DATABASE_URL',
                                   'https://nlppro-c23bc-default-rtdb.firebaseio.com')

        if not cred_path:
            logger.warning(
                "GOOGLE_APPLICATION_CREDENTIALS env var not set. "
                "Firebase disabled — data will NOT be stored remotely."
            )
            return

        if not os.path.isfile(cred_path):
            logger.warning(
                "Credential file '%s' not found. Firebase disabled.", cred_path
            )
            return

        cred = _creds.Certificate(cred_path)
        # Guard against double-init (e.g. tests)
        if not _fa.get_app._apps:  # type: ignore[attr-defined]
            _fa.initialize_app(cred, {'databaseURL': db_url})

        firebase_admin = _fa
        firebase_db    = _db
        firebase_ref   = _db.reference('processed_text')
        FIREBASE_ENABLED = True
        logger.info("Firebase initialised successfully.")

    except ImportError:
        logger.warning("firebase-admin not installed — Firebase disabled.")
    except Exception as exc:
        # [FIX A2] Firebase failure does NOT kill the process.
        logger.error("Firebase init failed (%s) — running without remote storage.", exc)


# ─────────────────────────────────────────────
# Optional translation — alpha library, fail-safe
# ─────────────────────────────────────────────
def _safe_translate(text: str, src: str = 'hi', dest: str = 'en') -> str:
    """Translate text with explicit fallback if googletrans fails."""
    try:
        from googletrans import Translator
        translator = Translator()
        result = translator.translate(text, src=src, dest=dest)
        if result and result.text:
            return result.text
        logger.warning("Empty translation result — using original text.")
        return text
    except Exception as exc:
        # [FIX A4] googletrans alpha failures are silently swallowed with a log.
        logger.warning("Translation failed (%s) — using original text.", exc)
        return text


# ─────────────────────────────────────────────
# NLTK — only download what is missing
# ─────────────────────────────────────────────
_REQUIRED_NLTK = [
    'punkt',
    'punkt_tab',
    'averaged_perceptron_tagger',
    'maxent_ne_chunker',
    'words',
    'vader_lexicon',
    'stopwords',
]

def initialize_nltk():
    """Download NLTK resources only if they are not already present."""
    for resource in _REQUIRED_NLTK:
        # [FIX E3] Check before downloading — avoids blocking on every cold start.
        resource_path = f'tokenizers/{resource}' if resource.startswith('punkt') else resource
        try:
            nltk.data.find(resource_path)
        except LookupError:
            logger.info("Downloading NLTK resource: %s", resource)
            try:
                nltk.download(resource, quiet=True)
            except Exception as exc:
                logger.warning("Could not download NLTK resource '%s': %s", resource, exc)


# ─────────────────────────────────────────────
# POS tag descriptions
# ─────────────────────────────────────────────
POS_DESCRIPTIONS = {
    'CC': 'Coordinating conjunction', 'CD': 'Cardinal number',
    'DT': 'Determiner', 'EX': 'Existential there', 'FW': 'Foreign word',
    'IN': 'Preposition/subordinating conjunction', 'JJ': 'Adjective',
    'JJR': 'Adjective, comparative', 'JJS': 'Adjective, superlative',
    'LS': 'List item marker', 'MD': 'Modal', 'NN': 'Noun, singular',
    'NNS': 'Noun, plural', 'NNP': 'Proper noun, singular',
    'NNPS': 'Proper noun, plural', 'PDT': 'Predeterminer',
    'POS': 'Possessive ending', 'PRP': 'Personal pronoun',
    'PRP$': 'Possessive pronoun', 'RB': 'Adverb',
    'RBR': 'Adverb, comparative', 'RBS': 'Adverb, superlative',
    'RP': 'Particle', 'TO': 'to', 'UH': 'Interjection',
    'VB': 'Verb, base form', 'VBD': 'Verb, past tense',
    'VBG': 'Verb, gerund/present participle', 'VBN': 'Verb, past participle',
    'VBP': 'Verb, non-3rd person singular present',
    'VBZ': 'Verb, 3rd person singular present', 'WDT': 'Wh-determiner',
    'WP': 'Wh-pronoun', 'WP$': 'Possessive wh-pronoun', 'WRB': 'Wh-adverb',
}


# ─────────────────────────────────────────────
# Main assistant class
# ─────────────────────────────────────────────
class VisuallyImpairedAssistant:

    def __init__(self):
        init()  # colorama

        # Sentiment analyser — optional
        self.sentiment_analyzer: SentimentIntensityAnalyzer | None = None
        try:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        except Exception as exc:
            logger.warning("Sentiment analyser unavailable: %s", exc)

        # Text-to-speech
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
        except Exception as exc:
            logger.error("TTS engine init failed: %s", exc)
            # [FIX A3] Don't sys.exit — degrade to text-only mode.
            self.engine = None

        # Speech recognition
        try:
            import pyaudio  # noqa: F401 — just verify it is installed
            self.recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                logger.info("Microphone detected.")
                self._speak_raw("Microphone initialised successfully.")
        except OSError as exc:
            # [FIX E2] Specific exception for hardware failure
            logger.error("Microphone hardware error: %s", exc)
            self._speak_raw(
                "Microphone not found. Please connect a microphone and restart."
            )
            sys.exit(1)
        except ImportError:
            logger.error("PyAudio not installed.")
            sys.exit(1)

        self.ambient_duration = 2
        self.listen_timeout   = 5
        self.phrase_timeout   = 10

    # ── TTS helpers ──────────────────────────────────────────────────────────

    def _speak_raw(self, text: str) -> None:
        """Low-level TTS call — does not translate."""
        if self.engine is None:
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            # [FIX A3] Re-init instead of crashing
            logger.warning("TTS engine stalled — reinitialising.")
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as exc:
                logger.error("TTS reinit failed: %s", exc)

    def speak(self, text: str, is_hindi: bool = False) -> None:
        """Print formatted output and speak it."""
        print(f"{Fore.GREEN}╔{'═' * 78}╗{Style.RESET_ALL}")
        words, current_line = text.split(), ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 76:
                current_line += word + " "
            else:
                print(f"{Fore.GREEN}║{Style.RESET_ALL} {current_line:<76} {Fore.GREEN}║{Style.RESET_ALL}")
                current_line = word + " "
        if current_line:
            print(f"{Fore.GREEN}║{Style.RESET_ALL} {current_line:<76} {Fore.GREEN}║{Style.RESET_ALL}")
        print(f"{Fore.GREEN}╚{'═' * 78}╝{Style.RESET_ALL}")

        speak_text = _safe_translate(text, src='hi', dest='en') if is_hindi else text
        self._speak_raw(speak_text)

    # ── Speech capture ───────────────────────────────────────────────────────

    def capture_speech(self):
        """Capture speech with specific exception handling — no bare except."""
        try:
            with sr.Microphone() as source:
                self.speak("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=self.ambient_duration)
                self.speak("Listening... Speak now in English or Hindi.")
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout,
                )
        except sr.WaitTimeoutError:
            self.speak("No speech detected within the timeout. Please try again.")
            logger.info("capture_speech: listen timeout")
            return None, False
        except OSError as exc:
            # [FIX E2] Hardware error — specific catch
            logger.error("capture_speech: microphone hardware error: %s", exc)
            self.speak("Microphone error. Please check your audio device.")
            return None, False

        # Attempt Hindi first, then English
        # [FIX E1] Language detection: Hindi is only accepted if recognition succeeds
        #          AND the text contains at least one non-ASCII character (Devanagari).
        for language, is_hindi in [('hi-IN', True), ('en-US', False)]:
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                if is_hindi:
                    # Verify it's actually Devanagari — not English mis-flagged as Hindi
                    if not any('\u0900' <= ch <= '\u097F' for ch in text):
                        logger.info("Hindi recognition returned ASCII — retrying as English.")
                        continue
                self.speak(f"You said: {text}", is_hindi)
                return text, is_hindi
            except sr.UnknownValueError:
                continue
            except sr.RequestError as exc:
                logger.error("Speech recognition service error: %s", exc)
                self.speak(f"Speech recognition service unavailable: {exc}")
                return None, False

        self.speak("Sorry, I couldn't understand the audio.")
        return None, False

    # ── Text processing ──────────────────────────────────────────────────────

    def process_text(self, text: str, is_hindi: bool = False):
        """Analyse text and return a list of description strings."""
        description = []
        try:
            # Translate Hindi to English for NLP processing
            eng_text = _safe_translate(text, src='hi', dest='en') if is_hindi else text
            if is_hindi:
                description.append(f"Translation: {eng_text}")

            sentences = sent_tokenize(eng_text)
            description.append(f"Number of sentences: {len(sentences)}")

            for i, sentence in enumerate(sentences, 1):
                description.append(f"\nAnalysing sentence {i}: {sentence}")
                try:
                    tokens = word_tokenize(sentence)
                    tagged = pos_tag(tokens)

                    word_types: dict[str, list[str]] = {}
                    for word, tag in tagged:
                        if tag in POS_DESCRIPTIONS:
                            word_types.setdefault(POS_DESCRIPTIONS[tag], []).append(word)

                    for category, words in word_types.items():
                        if words:
                            description.append(f"{category}: {', '.join(words)}")

                    try:
                        named_entities = ne_chunk(tagged)
                        entities = [
                            f"{chunk.label()}: {' '.join(c[0] for c in chunk)}"
                            for chunk in named_entities
                            if hasattr(chunk, 'label')
                        ]
                        if entities:
                            description.append(f"Named entities: {', '.join(entities)}")
                    except Exception as exc:
                        logger.warning("NER failed for sentence %d: %s", i, exc)
                        description.append("Note: Named entity recognition unavailable.")

                    if self.sentiment_analyzer:
                        try:
                            scores = self.sentiment_analyzer.polarity_scores(sentence)
                            c = scores['compound']
                            label = "positive" if c >= 0.05 else ("negative" if c <= -0.05 else "neutral")
                            description.append(
                                f"Sentiment: {label} (compound={c:.2f}, "
                                f"pos={scores['pos']:.2f}, neg={scores['neg']:.2f}, "
                                f"neu={scores['neu']:.2f})"
                            )
                        except Exception as exc:
                            logger.warning("Sentiment analysis failed: %s", exc)

                except Exception as exc:
                    logger.warning("Could not fully analyse sentence %d: %s", i, exc)
                    description.append(f"Note: Could not fully analyse sentence {i}.")

        except Exception as exc:
            logger.error("process_text top-level error: %s", exc)
            description.append("Note: Basic text analysis failed.")
            description.append(f"Words found: {', '.join(text.split())}")

        for desc in description:
            self.speak(desc, is_hindi)

        return description

    # ── Firebase storage ─────────────────────────────────────────────────────

    def store_in_firebase(self, data: dict) -> bool:
        """
        Store processed data in Firebase Realtime DB.
        [FIX A1/S3] Only runs if Firebase was successfully initialised.
        Raw speech text is NOT stored — only the processed analysis metadata.
        """
        if not FIREBASE_ENABLED:
            logger.info("Firebase disabled — skipping remote storage.")
            return False
        try:
            entry_id = int(time.time())
            # [FIX S3] Store analysis metadata only; raw_text intentionally omitted
            #          to avoid storing potentially sensitive spoken content.
            firebase_ref.child(f'entry_{entry_id}').set({
                'word_count': len(data.get('raw_text', '').split()),
                'sentence_count': len([d for d in data.get('processed', [])
                                       if d.startswith('\nAnalys')]),
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            })
            logger.info("Metadata stored in Firebase at entry_%d", entry_id)
            return True
        except Exception as exc:
            logger.error("Firebase write failed: %s", exc)
            return False

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        self.speak(
            "Visually Impaired Assistant started. "
            "You can speak in English or Hindi. Press Ctrl+C to exit."
        )
        max_retries, retry_count, retry_delay = 3, 0, 5

        try:
            while True:
                try:
                    spoken_text, is_hindi = self.capture_speech()

                    if spoken_text:
                        retry_count = 0
                        processed_data = self.process_text(spoken_text, is_hindi)
                        if processed_data:
                            self.store_in_firebase({
                                'raw_text': spoken_text,
                                'processed': processed_data,
                            })
                        else:
                            self.speak("Failed to process the text.")
                    else:
                        retry_count += 1
                        if retry_count >= max_retries:
                            self.speak(
                                f"Too many consecutive errors. "
                                f"Waiting {retry_delay} seconds before retrying."
                            )
                            time.sleep(retry_delay)
                            retry_count = 0

                    self.speak("Ready for next input.")
                    time.sleep(1)

                except Exception as exc:
                    logger.error("Main loop error: %s", exc)
                    self.speak(f"Unexpected error in main loop: {exc}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.speak(f"Waiting {retry_delay} seconds.")
                        time.sleep(retry_delay)
                        retry_count = 0

        except KeyboardInterrupt:
            self.speak("Exiting the application.")
            sys.exit(0)


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main() -> int:
    initialize_nltk()
    _init_firebase()
    try:
        assistant = VisuallyImpairedAssistant()
        assistant.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as exc:
        logger.critical("Fatal error: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())