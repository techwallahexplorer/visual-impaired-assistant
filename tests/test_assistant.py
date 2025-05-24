import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from awesome_assistant import AwesomeAssistant
from data_loader import DataLoader
import threading
import queue
import time

class TestAwesomeAssistant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.assistant = None
        cls.output_queue = queue.Queue()
        
    def setUp(self):
        """Set up each test"""
        self.assistant = AwesomeAssistant()
        
    def capture_output(self, text):
        """Capture assistant's speech output"""
        self.output_queue.put(text)
        
    def test_voice_initialization(self):
        """Test voice settings"""
        engine = self.assistant.engine
        properties = {
            'rate': engine.getProperty('rate'),
            'volume': engine.getProperty('volume'),
            'voice': engine.getProperty('voice')
        }
        
        self.assertEqual(properties['rate'], 150, "Speech rate should be 150")
        self.assertAlmostEqual(properties['volume'], 0.9, places=1, msg="Volume should be 0.9")
        self.assertIsNotNone(properties['voice'], "Voice should be set")
        
    def test_model_initialization(self):
        """Test ML model initialization"""
        self.assertIsNotNone(self.assistant.sentiment_analyzer, "Sentiment analyzer should be initialized")
        self.assertIsNotNone(self.assistant.qa_pipeline, "QA pipeline should be initialized")
        
    def test_data_loader(self):
        """Test data loader functionality"""
        self.assertIsNotNone(self.assistant.data_loader, "Data loader should be initialized")
        self.assertIsNotNone(self.assistant.training_data, "Training data should be loaded")
        
    def test_wake_word_detection(self):
        """Test wake word detector initialization"""
        self.assertIsNotNone(self.assistant.wake_word_detector, "Wake word detector should be initialized")
        
    def test_speech_recognition(self):
        """Test speech recognition components"""
        self.assertIsNotNone(self.assistant.recognizer, "Speech recognizer should be initialized")
        self.assertIsNotNone(self.assistant.whisper_model, "Whisper model should be initialized")
        
    def test_response_generation(self):
        """Test response generation"""
        # Test basic responses
        response = self.assistant.get_response('greeting', 'en')
        self.assertIsNotNone(response, "Should get a greeting response")
        
        # Test sentiment analysis
        if self.assistant.sentiment_analyzer:
            text = "I'm having a great day!"
            sentiment = self.assistant.sentiment_analyzer(text)[0]
            self.assertEqual(sentiment['label'], 'POSITIVE', "Should detect positive sentiment")
            
    def test_command_execution(self):
        """Test command execution"""
        # Set up output capture
        self.assistant.gui_callback = self.capture_output
        
        # Test time command
        self.assistant.execute_command("what time is it")
        try:
            response = self.output_queue.get(timeout=2)
            self.assertIn("current time", response.lower(), "Should respond with current time")
        except queue.Empty:
            self.fail("No response received for time command")
            
    def test_error_handling(self):
        """Test error handling"""
        # Test invalid command
        self.assistant.gui_callback = self.capture_output
        self.assistant.execute_command("thisisaninvalidcommand")
        try:
            response = self.output_queue.get(timeout=2)
            self.assertIn("sorry", response.lower(), "Should apologize for invalid command")
        except queue.Empty:
            self.fail("No response received for invalid command")
            
    def test_voice_properties(self):
        """Test voice property settings"""
        voices = self.assistant.engine.getProperty('voices')
        current_voice = self.assistant.engine.getProperty('voice')
        
        # Check if we have a voice set
        self.assertIsNotNone(current_voice, "Voice should be set")
        
        # Find the current voice in the list
        voice_found = False
        for voice in voices:
            if voice.id == current_voice:
                voice_found = True
                break
                
        self.assertTrue(voice_found, "Current voice should be in available voices")
        
    def test_threading_safety(self):
        """Test thread safety of assistant"""
        def run_commands():
            for _ in range(5):
                self.assistant.execute_command("what time is it")
                time.sleep(0.1)
                
        threads = [threading.Thread(target=run_commands) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
if __name__ == '__main__':
    unittest.main(verbosity=2)
