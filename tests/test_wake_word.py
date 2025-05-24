import unittest
import soundfile as sf
import numpy as np
import speech_recognition as sr
from unittest.mock import MagicMock, patch
from wake_word_detection import WakeWordDetector

class TestWakeWordDetector(unittest.TestCase):
    def setUp(self):
        self.detector = WakeWordDetector()

    def test_initialization(self):
        """Test if the detector is properly initialized"""
        self.assertEqual(self.detector.wake_word, "hey awesome")
        self.assertIsNotNone(self.detector.recognizer)
        self.assertIsNotNone(self.detector.animation_window)
        self.assertEqual(self.detector.recognizer.energy_threshold, 4000)
        self.assertTrue(self.detector.recognizer.dynamic_energy_threshold)
        self.assertEqual(self.detector.recognizer.pause_threshold, 0.8)
        self.assertEqual(self.detector.recognizer.phrase_threshold, 0.3)
        self.assertEqual(self.detector.recognizer.non_speaking_duration, 0.5)

    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('wake_word_detection.show_wake_animation')
    def test_wake_word_variations(self, mock_animation, mock_recognize):
        """Test detection of different wake word variations"""
        variations = [
            "hey awesome",
            "hi awesome",
            "hello awesome",
            "hay awesome",
            "hey awsome"
        ]
        
        for phrase in variations:
            mock_recognize.return_value = phrase
            with patch('speech_recognition.Microphone') as mock_mic,\
                 patch.object(self.detector.recognizer, 'listen') as mock_listen,\
                 patch.object(self.detector.recognizer, 'adjust_for_ambient_noise'):
                
                mock_source = MagicMock()
                mock_mic.return_value.__enter__.return_value = mock_source
                mock_audio = MagicMock()
                mock_listen.return_value = mock_audio
                
                # Simulate one successful detection then exit
                def side_effect(*args, **kwargs):
                    result = self.detector.detect()
                    raise KeyboardInterrupt()
                    return result
                
                try:
                    side_effect()
                except KeyboardInterrupt:
                    pass
                
                mock_animation.assert_called_once()
                mock_recognize.assert_called_with(mock_audio)

    @patch('speech_recognition.Recognizer.recognize_google')
    @patch('wake_word_detection.show_wake_animation')
    def test_non_wake_words(self, mock_animation, mock_recognize):
        """Test rejection of non-wake words"""
        non_wake_words = [
            "hey assistant",
            "hello there",
            "hi computer",
            "random phrase"
        ]
        
        for phrase in non_wake_words:
            mock_recognize.return_value = phrase
            with patch('speech_recognition.Microphone') as mock_mic,\
                 patch.object(self.detector.recognizer, 'listen') as mock_listen,\
                 patch.object(self.detector.recognizer, 'adjust_for_ambient_noise'):
                
                mock_source = MagicMock()
                mock_mic.return_value.__enter__.return_value = mock_source
                mock_audio = MagicMock()
                mock_listen.return_value = mock_audio
                
                def side_effect(*args, **kwargs):
                    result = self.detector.detect()
                    raise KeyboardInterrupt()
                    return result
                
                try:
                    side_effect()
                except KeyboardInterrupt:
                    pass
                
                mock_animation.assert_not_called()
                mock_recognize.assert_called_with(mock_audio)

    def test_error_handling(self):
        """Test error handling scenarios"""
        with patch('speech_recognition.Microphone') as mock_mic:
            mock_source = MagicMock()
            mock_mic.return_value.__enter__.return_value = mock_source
            
            # Test UnknownValueError handling
            self.detector.recognizer.recognize_google = MagicMock(
                side_effect=sr.UnknownValueError()
            )
            result = self.detector.detect()
            self.assertFalse(result)
            
            # Test RequestError handling
            self.detector.recognizer.recognize_google = MagicMock(
                side_effect=sr.RequestError("Test error")
            )
            result = self.detector.detect()
            self.assertFalse(result)

    def test_ambient_noise_adjustment(self):
        """Test ambient noise adjustment functionality"""
        with patch('speech_recognition.Microphone') as mock_mic:
            mock_source = MagicMock()
            mock_mic.return_value.__enter__.return_value = mock_source
            
            # Mock the adjust_for_ambient_noise method
            self.detector.recognizer.adjust_for_ambient_noise = MagicMock()
            self.detector.detect()
            
            # Verify that adjust_for_ambient_noise was called with correct duration
            self.detector.recognizer.adjust_for_ambient_noise.assert_called_once_with(
                mock_source, duration=1
            )

if __name__ == '__main__':
    unittest.main()