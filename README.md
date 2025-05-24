# Awesome - Your Personal Laptop Assistant

Awesome is a voice-controlled assistant for Windows that helps you control your laptop through voice commands. It uses advanced speech recognition and natural language processing to understand and execute your commands.

## Features

- Voice command recognition using Whisper (offline processing)
- Natural language understanding using transformers
- System control capabilities (volume, screenshots, etc.)
- Application management (open/close programs)
- Time and date information

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start the assistant, run:
```bash
python awesome_assistant.py
```

### Available Commands

- "Open [browser/chrome/notepad]"
- "What's the time?"
- "What's the date?"
- "Volume up/down/mute"
- "Take a screenshot"
- "Exit/Stop/Goodbye" (to close the assistant)

## Security Note

This assistant runs with user permissions and can access system functions that the user has permission to use. Please be mindful of the commands you give and ensure your system's security settings are appropriately configured.

## Customization

You can extend the assistant's capabilities by adding new commands in the `execute_command` method of the `AwesomeAssistant` class.