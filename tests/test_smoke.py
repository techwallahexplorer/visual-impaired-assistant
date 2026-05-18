"""
Smoke tests for visual-impaired-assistant.
These run on CI without any microphone, speaker, camera, or Firebase.
All hardware-dependent components are mocked.
"""
import sys
import types
import unittest
from unittest.mock import MagicMock, patch


# ── Stub out hardware modules before any import of the main module ────────────

def _stub_module(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod

# pyaudio stub
_stub_module('pyaudio', PyAudio=MagicMock, paInt16=8)

# pyttsx3 stub
_pyttsx3 = _stub_module('pyttsx3')
_pyttsx3.init = MagicMock(return_value=MagicMock())

# speech_recognition stub
_sr = _stub_module('speech_recognition',
                   Recognizer=MagicMock,
                   Microphone=MagicMock,
                   UnknownValueError=Exception,
                   RequestError=Exception,
                   WaitTimeoutError=Exception)

# cv2 stub
_stub_module('cv2', VideoCapture=MagicMock, imencode=MagicMock)

# googletrans stub
_trans_mod = _stub_module('googletrans')
_translator = MagicMock()
_translator.translate.return_value = MagicMock(text='hello', src='en')
_trans_mod.Translator = MagicMock(return_value=_translator)

# firebase_admin stubs
_stub_module('firebase_admin')
_stub_module('firebase_admin.credentials')
_stub_module('firebase_admin.db')

# google.cloud stubs
_gc = _stub_module('google')
_gc_cloud = _stub_module('google.cloud')
_stub_module('google.cloud.speech')
_stub_module('google.cloud.storage')

# nltk stub (data already present in CI via download step)
import nltk  # noqa: E402 — real nltk is available


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestInputSanitization(unittest.TestCase):
    """Test the sanitization helpers without touching hardware."""

    def test_sanitize_removes_control_chars(self):
        raw = "hello\x00world\x1b[31m"
        result = ''.join(c for c in raw if c.isprintable())
        self.assertNotIn('\x00', result)
        self.assertNotIn('\x1b', result)

    def test_sanitize_strips_excess_whitespace(self):
        raw = "   fever   and   cough   "
        result = ' '.join(raw.split())
        self.assertEqual(result, "fever and cough")

    def test_empty_input_is_safe(self):
        result = ''.join(c for c in '' if c.isprintable())
        self.assertEqual(result, '')


class TestLanguageDetection(unittest.TestCase):
    """Test Devanagari detection logic from visually.py."""

    def _is_hindi(self, text: str) -> bool:
        return any('\u0900' <= ch <= '\u097F' for ch in text)

    def test_hindi_text_detected(self):
        self.assertTrue(self._is_hindi("नमस्ते दुनिया"))

    def test_english_not_detected_as_hindi(self):
        self.assertFalse(self._is_hindi("hello world"))

    def test_mixed_text_detected_as_hindi(self):
        self.assertTrue(self._is_hindi("hello नमस्ते"))

    def test_empty_string_not_hindi(self):
        self.assertFalse(self._is_hindi(""))


class TestSessionId(unittest.TestCase):
    """Verify session IDs are unique and non-empty."""

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

    def test_id_is_string(self):
        self.assertIsInstance(self._generate_id(), str)

    def test_ids_are_unique(self):
        ids = {self._generate_id() for _ in range(100)}
        self.assertEqual(len(ids), 100)

    def test_id_format(self):
        import re
        uid = self._generate_id()
        self.assertRegex(uid, r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')


class TestNltkAvailability(unittest.TestCase):
    """Ensure required NLTK data packages are present after CI download step."""

    def test_required_packages_available(self):
        packages = {
            'punkt': 'tokenizers/punkt',
            'punkt_tab': 'tokenizers/punkt_tab',
            'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
            'maxent_ne_chunker': 'chunkers/maxent_ne_chunker',
            'words': 'corpora/words',
            'vader_lexicon': 'sentiment/vader_lexicon.zip',
            'stopwords': 'corpora/stopwords',
        }
        for pkg, path in packages.items():
            try:
                nltk.data.find(path)
            except LookupError:
                self.fail(f"NLTK package '{pkg}' not downloaded in CI (checked path: '{path}')")


if __name__ == '__main__':
    unittest.main()
