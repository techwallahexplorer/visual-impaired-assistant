import unittest
from unittest.mock import MagicMock, patch
from awesome_assistant import AwesomeAssistant
from datetime import datetime

class TestAwesomeAssistant(unittest.TestCase):
    def setUp(self):
        self.assistant = AwesomeAssistant()
        # Mock the text-to-speech engine to avoid actual speech output
        self.assistant.engine = MagicMock()

    def test_speak(self):
        test_text = "Hello, this is a test"
        self.assistant.speak(test_text)
        self.assistant.engine.say.assert_called_once_with(test_text)
        self.assistant.engine.runAndWait.assert_called_once()

    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_listen(self, mock_mic, mock_recognizer):
        # Import AudioSource from speech_recognition
        from speech_recognition import AudioSource
        
        # Mock the whisper model transcription
        self.assistant.whisper_model.transcribe = MagicMock(return_value={"text": "test command"})
        
        # Configure the mock microphone and recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        
        # Create a proper AudioSource mock
        class MockAudioSource(AudioSource):
            def __init__(self):
                self.SAMPLE_RATE = 16000
                self.SAMPLE_WIDTH = 2
                self.CHUNK = 1024
                self.CHANNELS = 1
                self.format = None
                self._stream = None

            def __enter__(self):
                self._stream = MagicMock()
                return self

            def __exit__(self, *args):
                self._stream = None

            @property
            def stream(self):
                return self._stream
        
        mock_mic_instance = MockAudioSource()
        mock_mic.return_value = mock_mic_instance
        
        mock_audio = MagicMock()
        mock_audio.get_wav_data.return_value = b'fake_audio_data'
        mock_recognizer_instance.listen.return_value = mock_audio
        
        # Mock file operations
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_open.return_value.__exit__ = MagicMock()
            result = self.assistant.listen()
            self.assertEqual(result, "test command")

    def test_execute_command_time(self):
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "12:00"
            self.assistant.execute_command("what's the time?")
            self.assistant.engine.say.assert_called_once_with("The current time is 12:00")

    def test_execute_command_date(self):
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2024-01-01"
            self.assistant.execute_command("what's the date?")
            self.assistant.engine.say.assert_called_once_with("Today's date is 2024-01-01")

    @patch('subprocess.Popen')
    def test_execute_command_open_browser(self, mock_popen):
        self.assistant.execute_command("open browser")
        mock_popen.assert_called_once_with(["chrome"])
        self.assistant.engine.say.assert_called_once_with("Opening Chrome browser")

    @patch('pyautogui.screenshot')
    def test_execute_command_screenshot(self, mock_screenshot):
        mock_screenshot_obj = MagicMock()
        mock_screenshot.return_value = mock_screenshot_obj
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0)
            self.assistant.execute_command("take a screenshot")
            mock_screenshot_obj.save.assert_called_once()
            self.assistant.engine.say.assert_called_once_with("Screenshot taken")

    @patch('pyautogui.press')
    def test_execute_command_volume(self, mock_press):
        # Test volume up
        self.assistant.execute_command("volume up")
        mock_press.assert_called_with("volumeup")
        self.assistant.engine.say.assert_called_with("Volume increased")

        # Test volume down
        self.assistant.execute_command("volume down")
        mock_press.assert_called_with("volumedown")
        self.assistant.engine.say.assert_called_with("Volume decreased")

        # Test volume mute
        self.assistant.execute_command("volume mute")
        mock_press.assert_called_with("volumemute")
        self.assistant.engine.say.assert_called_with("Volume muted")

    def test_unknown_command(self):
        self.assistant.execute_command("unknown command")
        self.assistant.engine.say.assert_called_once_with("I'm not sure how to help with that yet. I'm still learning!")

    def test_detect_language(self):
        # Test Hindi detection
        self.assertEqual(self.assistant.detect_language("नमस्ते कैसे हैं आप"), 'hi')
        # Test Hinglish detection
        self.assertEqual(self.assistant.detect_language("kya hai bhai"), 'hinglish')
        # Test English detection
        self.assertEqual(self.assistant.detect_language("hello how are you"), 'en')

    @patch('pywhatkit.sendwhatmsg_instantly')
    def test_send_whatsapp_message(self, mock_send):
        self.assistant.send_whatsapp_message("+1234567890", "Test message")
        mock_send.assert_called_once_with("+1234567890", "Test message")
        self.assistant.engine.say.assert_called_once_with("WhatsApp message sent successfully")

    @patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        # Setup mock SMTP instance
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Setup test credentials
        self.assistant.setup_gmail("test@gmail.com", "password")
        
        # Test sending email
        self.assistant.send_email("recipient@example.com", "Test Subject", "Test Body")
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with('smtp.gmail.com', 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("test@gmail.com", "password")
        mock_smtp_instance.send_message.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()
        self.assistant.engine.say.assert_called_once_with("Email sent successfully")

    @patch('webbrowser.open')
    def test_search_jiosaavn(self, mock_open):
        self.assistant.search_jiosaavn("test song")
        mock_open.assert_called_once_with("https://www.jiosaavn.com/search/test song")
        self.assistant.engine.say.assert_called_once_with("Searching for test song on JioSaavn")

    @patch('pywhatkit.playonyt')
    def test_play_youtube(self, mock_play):
        self.assistant.play_youtube("test video")
        mock_play.assert_called_once_with("test video")
        self.assistant.engine.say.assert_called_once_with("Playing test video on YouTube")

    def test_get_response(self):
        # Test English response
        self.assertEqual(
            self.assistant.get_response('greeting', 'en', self.assistant.name),
            f"Hello! I'm {self.assistant.name}, your personal laptop assistant. How can I help you?"
        )
        
        # Test Hindi response
        self.assertEqual(
            self.assistant.get_response('greeting', 'hi', self.assistant.name),
            f"नमस्ते! मैं {self.assistant.name} हूं, आपका पर्सनल लैपटॉप असिस्टेंट। मैं आपकी कैसे मदद कर सकती हूं?"
        )
        
        # Test Hinglish response
        self.assertEqual(
            self.assistant.get_response('greeting', 'hinglish', self.assistant.name),
            f"Hello! Main {self.assistant.name} hoon, aapki personal laptop assistant. Main aapki kaise help kar sakti hoon?"
        )

if __name__ == '__main__':
    unittest.main()