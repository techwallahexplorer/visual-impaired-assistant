# Visual Impaired Assistant

A Python voice assistant for English/Hindi speech input, text analysis, and audio feedback. The project focuses on accessibility workflows, NLP analysis, and safer handling of optional services such as Firebase and translation.

## What It Does

- Captures speech input through a microphone.
- Supports English and Hindi input paths.
- Runs NLP analysis with NLTK:
  - tokenization
  - POS tagging
  - named entity recognition
  - VADER sentiment analysis
- Provides text-to-speech feedback.
- Handles Firebase, translation, and TTS failures without crashing the whole app.
- Includes CI smoke tests that mock audio/TTS dependencies for headless runners.

## Tech Stack

- Python
- SpeechRecognition
- pyttsx3
- NLTK
- VADER
- googletrans
- Firebase Admin SDK
- GitHub Actions
- pytest

## Local Setup

```bash
git clone https://github.com/techwallahexplorer/visual-impaired-assistant.git
cd visual-impaired-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

Run:

```bash
visual-assistant
```

or:

```bash
python -m visual_assistant.visually
```

## Optional Firebase Logging

Firebase is disabled unless credentials are provided through environment variables.

```bash
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
set FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
```

The app should continue locally even when Firebase is not configured.

## Testing

```bash
pytest tests/ -v
```

The smoke tests mock microphone, speaker, translation, and Firebase dependencies so the core safety paths can run in CI.

## Current Limits

- Speech recognition depends on microphone quality and internet availability.
- `googletrans` is unofficial and can break; production use should move to Google Cloud Translate.
- This is an accessibility prototype, not a certified assistive technology product.
