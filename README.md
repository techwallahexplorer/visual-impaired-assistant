# Visually Impaired Assistant

[![Python Application](https://github.com/techwallahexplorer/visual-impaired-assistant/actions/workflows/python-app.yml/badge.svg)](https://github.com/techwallahexplorer/visual-impaired-assistant/actions/workflows/python-app.yml)

A Python-based assistant for visually impaired users that provides speech recognition, text analysis, and audio feedback in both English and Hindi. This tool helps visually impaired users interact with computers through voice commands and receive detailed analysis of their speech in both English and Hindi.

## Features

- **Multilingual Support**
  - Speech recognition in English and Hindi
  - Automatic language detection
  - Translation between Hindi and English

- **Advanced Text Analysis**
  - Part-of-speech tagging (nouns, verbs, adjectives, etc.)
  - Named Entity Recognition
  - Sentiment Analysis using VADER
  - Word categorization and analysis

- **Accessibility Features**
  - Clear audio feedback using text-to-speech
  - Formatted console output with color coding
  - Error recovery and graceful degradation

## Requirements

- Python 3.8+
- Required packages (see requirements.txt)
- Internet connection for speech recognition and translation
- Working microphone for speech input

## Quick Start

### Installation from PyPI

```bash
pip install visual-impaired-assistant
```

### Run the Assistant

```bash
visual-assistant
```

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/techwallahexplorer/visual-impaired-assistant.git
   cd visual-impaired-assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix/MacOS
   ```

3. Install in development mode:

   ```bash
   pip install -e .
   ```

4. NLTK resources will be downloaded automatically on first run

## GitHub Integration

1. Fork the repository on GitHub
2. Create a new branch for your feature:

   ```bash
   git checkout -b feature-name
   ```

3. Make your changes and commit:

   ```bash
   git add .
   git commit -m "Add new feature"
   ```

4. Push to GitHub:

   ```bash
   git push origin feature-name
   ```
5. Create a Pull Request on GitHub

## Usage

1. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```

2. Run the assistant:
   ```bash
   python visually.py
   ```

3. Speak when prompted (in English or Hindi)
4. Listen to the analysis and feedback

## Configuration

The assistant can be configured through the following parameters in `visually.py`:

- `ambient_duration`: Duration for ambient noise adjustment (default: 1 second)
- `listen_timeout`: Timeout for listening (default: 5 seconds)
- `phrase_timeout`: Maximum phrase duration (default: 5 seconds)

## Project Structure

```
Visual/
├── .venv/                 # Virtual environment
├── visually.py           # Main assistant code
├── test_audio.py        # Audio testing utilities
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Version History

- v1.0.0 (2025-05-23)
  - Initial release
  - Basic speech recognition in English
  - Simple text analysis

- v1.1.0 (2025-05-23)
  - Added Hindi language support
  - Improved error handling
  - Enhanced text analysis with NLTK

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
