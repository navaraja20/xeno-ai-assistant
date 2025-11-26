# Advanced Voice & NLP - XENO

Complete voice control system with custom wake words, multi-language support, emotion analysis, voice biometrics, and natural conversation.

## Features 🎤

### 1. Custom Wake Words
- **Pre-configured**: "XENO", "Hey XENO", "OK XENO", "Computer"
- **Custom wake words**: Add your own wake words with audio samples
- **Pattern matching**: Phoneme-based detection for accuracy
- **Sensitivity control**: Adjustable detection threshold (0.1 - 1.0)

```python
from src.voice.advanced_voice_engine import AdvancedVoiceEngine

engine = AdvancedVoiceEngine()
await engine.initialize()

# Add custom wake word
engine.add_custom_wake_word("jarvis")
```

### 2. Multi-Language Support
Supports 13 languages with automatic detection:

- **English** (US, UK)
- **Spanish** (Spain)
- **French** (France)
- **German** (Germany)
- **Italian** (Italy)
- **Portuguese** (Brazil)
- **Japanese** (Japan)
- **Chinese** (Mandarin)
- **Korean** (South Korea)
- **Russian** (Russia)
- **Arabic** (Saudi Arabia)
- **Hindi** (India)

```python
from src.voice.advanced_voice_engine import Language

# Set language
engine.set_language(Language.SPANISH)

# Auto-detect language
engine.stt.enable_auto_detect()
```

### 3. Emotion Analysis
Detects 8 emotions from voice and text:

- **Neutral** - Calm, matter-of-fact
- **Happy** - Positive, cheerful
- **Sad** - Downcast, melancholic
- **Angry** - Irritated, furious
- **Excited** - Enthusiastic, energetic
- **Frustrated** - Annoyed, impatient
- **Confused** - Uncertain, questioning
- **Calm** - Peaceful, relaxed

**Analysis combines**:
- Text keywords ("great", "sad", "angry", etc.)
- Audio features (pitch, energy, tempo)
- Punctuation patterns (exclamation marks, question marks)

```python
from src.voice.advanced_voice_engine import EmotionAnalyzer, Emotion

analyzer = EmotionAnalyzer()

# Analyze text
emotion = analyzer.analyze_text("This is amazing!")
print(emotion)  # Emotion.EXCITED

# Analyze audio + text
audio_features = {'pitch': 0.8, 'energy': 0.9, 'tempo': 0.7}
emotion = analyzer.analyze("Wow this is great!", audio_features)
```

### 4. Voice Biometrics
Speaker recognition and verification using voice fingerprints:

- **Enrollment**: Register users with voice samples
- **Verification**: Confirm speaker identity (threshold: 0.85)
- **Identification**: Identify speaker from enrolled profiles
- **Adaptive learning**: Profiles improve with usage

```python
from src.voice.advanced_voice_engine import VoiceBiometrics
import numpy as np

biometrics = VoiceBiometrics()

# Enroll user with 5 audio samples
audio_samples = [np.random.randn(16000) for _ in range(5)]
profile = biometrics.enroll_user("john_doe", audio_samples)

# Verify speaker
verified, confidence = biometrics.verify_speaker("john_doe", audio_sample)
print(f"Verified: {verified}, Confidence: {confidence:.2%}")

# Identify unknown speaker
user_id, confidence = biometrics.identify_speaker(audio_sample)
print(f"Speaker: {user_id}, Confidence: {confidence:.2%}")
```

### 5. Natural Conversation
Context-aware conversation management:

- **Conversation history**: Last 10 messages per user
- **Entity extraction**: Names, dates, times, locations
- **Topic detection**: Automatic topic change detection
- **Sentiment tracking**: Emotion history over conversation
- **Context summary**: Quick overview of conversation state

```python
from src.voice.advanced_voice_engine import ConversationManager

manager = ConversationManager()

# Add messages
manager.add_message("user123", "user", "Schedule meeting with John tomorrow at 2 PM")
manager.add_message("user123", "assistant", "Meeting scheduled with John for tomorrow at 2 PM")

# Get context
context = manager.get_context("user123")
print(context.entities)  # {'person': 'John', 'date': 'tomorrow', 'time': '2 PM'}

# Extract entities
entities = manager.extract_entities("Call Sarah next Monday morning", context)

# Get context summary
summary = manager.get_context_summary("user123")
print(summary)  # "Current topic: meetings | Entities: person=John, date=tomorrow | ..."
```

### 6. Voice Command Processing
Natural language understanding for voice commands:

**Supported Intents** (20+):
- Email: send, check, read
- Calendar: create event, check schedule, reschedule
- Tasks: create, list, complete
- Workflows: run, create
- General: search, question, reminder, timer
- Weather: check forecast
- News: headlines, topics
- Control: open/close apps, settings

**Example Commands**:
```
"Send email to john@example.com saying meeting confirmed"
"Schedule meeting with Sarah tomorrow at 3 PM"
"Create task to buy groceries"
"Run the daily standup workflow"
"What's the weather in San Francisco?"
"Remind me to call mom at 5 PM"
"Set timer for 10 minutes"
"Open Chrome"
```

```python
from src.voice.voice_command_processor import NaturalLanguageProcessor, VoiceCommandExecutor

nlp = NaturalLanguageProcessor()

# Parse command
command = nlp.parse_command("Send email to john about the project")
print(command.intent)  # CommandIntent.SEND_EMAIL
print(command.parameters)  # {'recipient': 'john', 'message': 'about the project'}
print(command.confidence)  # 0.92

# Execute command
executor = VoiceCommandExecutor(XENO_app)
result = await executor.execute(command)
print(result)  # {'success': True, 'message': 'Email sent to john'}
```

### 7. Visual Interface
PyQt6 voice control interface with:

- **Waveform visualization**: Real-time audio input display
- **Start/Stop controls**: One-click listening toggle
- **Language selector**: Switch between 13 languages
- **Sensitivity slider**: Adjust wake word detection (0.1 - 1.0)
- **Wake word selector**: Choose or add custom wake words
- **Status indicators**: Listening state, confidence, emotion, speaker
- **Live transcript**: Conversation history with timestamps
- **Dark theme**: Matches XENO design (#2b2d31)

```python
from src.ui.voice_ui import VoiceUI
from src.voice.advanced_voice_engine import AdvancedVoiceEngine

engine = AdvancedVoiceEngine()
await engine.initialize()

# Create UI
voice_ui = VoiceUI(engine)
voice_ui.show()
```

## Architecture

```
┌─────────────────────────────────────────┐
│       Advanced Voice Engine             │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Wake Word    │  │ Multi-Lang   │   │
│  │ Detector     │  │ STT/TTS      │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Emotion      │  │ Voice        │   │
│  │ Analyzer     │  │ Biometrics   │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Conversation │  │ Command      │   │
│  │ Manager      │  │ Processor    │   │
│  └──────────────┘  └──────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies
Already included in requirements.txt:
```bash
pip install SpeechRecognition==3.10.0
pip install pyaudio==0.2.13
pip install pyttsx3==2.90
pip install elevenlabs==0.2.26
pip install numpy
```

### 2. Basic Usage

```python
import asyncio
from src.voice.advanced_voice_engine import AdvancedVoiceEngine
import speech_recognition as sr

async def main():
    # Initialize engine
    engine = AdvancedVoiceEngine()
    await engine.initialize()
    
    # Listen to microphone
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        print("Say something...")
        audio = recognizer.listen(source)
    
    # Process audio
    result = await engine.process_audio(audio)
    
    if result['success']:
        print(f"Text: {result['text']}")
        print(f"Language: {result['language']}")
        print(f"Emotion: {result['emotion']}")
        print(f"User: {result['user_id']}")
        print(f"Confidence: {result['confidence']:.2%}")
        
        # Respond
        response_text = "I heard you!"
        await engine.respond(response_text, result['user_id'], result['emotion'])
    
    await engine.shutdown()

asyncio.run(main())
```

### 3. With Voice UI

```python
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

engine = AdvancedVoiceEngine()
voice_ui = VoiceUI(engine)
voice_ui.show()

sys.exit(app.exec())
```

## Advanced Usage

### Custom Wake Words with Audio Samples

```python
import numpy as np

# Record audio samples for custom wake word
samples = []
for i in range(5):
    print(f"Say 'jarvis' ({i+1}/5)")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    audio_np = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    samples.append(audio_np)

# Add custom wake word
engine.wake_word_detector.add_custom_wake_word("jarvis", samples)
```

### Voice Biometric Enrollment

```python
# Record 5-10 samples from user
print("Please say 5 phrases for enrollment:")
samples = []

phrases = [
    "The quick brown fox jumps over the lazy dog",
    "I love using XENO for productivity",
    "Schedule a meeting for tomorrow",
    "What's the weather like today",
    "Read my latest emails"
]

for phrase in phrases:
    print(f"Say: {phrase}")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    audio_np = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
    samples.append(audio_np)

# Enroll user
profile = engine.enroll_user("john_doe", samples)
print(f"Enrolled with confidence threshold: {profile.confidence_threshold}")
```

### Emotion-Aware Responses

```python
async def respond_with_emotion(text: str, user_emotion):
    """Respond with matching emotion"""
    
    # Match user's emotion
    response_emotion = user_emotion
    
    # Or adapt based on context
    if user_emotion == Emotion.SAD:
        response_emotion = Emotion.CALM  # Be calming
    elif user_emotion == Emotion.ANGRY:
        response_emotion = Emotion.CALM  # De-escalate
    elif user_emotion == Emotion.EXCITED:
        response_emotion = Emotion.HAPPY  # Match excitement
    
    await engine.respond(text, user_id="user123", emotion=response_emotion)
```

### Multi-Turn Conversations

```python
async def conversation_loop():
    """Natural conversation with context"""
    
    user_id = "john_doe"
    
    while True:
        # Listen
        with sr.Microphone() as source:
            audio = recognizer.listen(source)
        
        # Process
        result = await engine.process_audio(audio)
        
        if not result['success']:
            continue
        
        # Get conversation context
        context = engine.conversation_manager.get_context(user_id)
        
        # Check for topic change
        if result.get('topic_changed'):
            print("New topic detected!")
        
        # Use entities from context
        entities = result.get('entities', {})
        print(f"Entities: {entities}")
        
        # Generate contextual response
        # (integrate with your LLM here)
        response = f"I understand. You mentioned {entities}"
        
        # Respond with emotion
        await engine.respond(
            response,
            user_id=user_id,
            emotion=result['emotion'],
            language=result['language']
        )
```

## Integration with XENO

### Connect to Main App

```python
from src.voice.advanced_voice_engine import AdvancedVoiceEngine
from src.voice.voice_command_processor import VoiceCommandExecutor

class XENOApp:
    def __init__(self):
        self.voice_engine = AdvancedVoiceEngine()
        self.command_executor = VoiceCommandExecutor(self)
        
    async def initialize_voice(self):
        await self.voice_engine.initialize()
        
    async def process_voice_command(self, audio):
        # Process audio
        result = await self.voice_engine.process_audio(audio)
        
        if result['success']:
            # Parse command
            from src.voice.voice_command_processor import NaturalLanguageProcessor
            nlp = NaturalLanguageProcessor()
            command = nlp.parse_command(result['text'])
            
            # Execute
            exec_result = await self.command_executor.execute(command)
            
            # Respond
            await self.voice_engine.respond(
                exec_result['message'],
                result['user_id'],
                result['emotion'],
                result['language']
            )
```

### Voice-Triggered Workflows

```python
# In Integration Hub workflows
workflow = {
    'trigger': {
        'type': 'voice_command',
        'config': {
            'wake_word': 'XENO',
            'command_pattern': 'run daily standup'
        }
    },
    'actions': [
        # ... workflow actions
    ]
}

# Voice command handler
async def on_voice_command(command):
    if command.intent == CommandIntent.RUN_WORKFLOW:
        workflow_name = command.parameters.get('workflow_name')
        await workflow_engine.execute_workflow(workflow_name)
```

## Configuration

### Voice Settings
```python
# Wake word sensitivity (0.1 - 1.0)
engine.wake_word_detector.sensitivity = 0.7

# Voice biometric confidence threshold
engine.voice_biometrics.profiles['user'].confidence_threshold = 0.85

# Conversation history length
engine.conversation_manager.max_history = 20

# Language preferences
engine.set_language(Language.ENGLISH_US)
```

### Audio Settings
```python
# Microphone timeout
timeout = 5  # seconds

# Phrase time limit
phrase_time_limit = 10  # seconds

# Ambient noise adjustment
recognizer.adjust_for_ambient_noise(source, duration=1.0)

# Energy threshold
recognizer.energy_threshold = 4000
```

## Performance

- **Wake word detection**: < 100ms latency
- **Speech recognition**: 1-3 seconds (Google Cloud)
- **Emotion analysis**: < 50ms
- **Speaker identification**: < 100ms
- **Voice synthesis**: 1-2 seconds (ElevenLabs/Google)
- **Memory usage**: ~200MB (with all features)

## Troubleshooting

### Microphone Not Working
```python
# List available microphones
import speech_recognition as sr
print(sr.Microphone.list_microphone_names())

# Use specific microphone
mic = sr.Microphone(device_index=0)
```

### Low Recognition Accuracy
```python
# Adjust energy threshold
recognizer.energy_threshold = 4000  # Increase for noisy environments

# Adjust for ambient noise
with sr.Microphone() as source:
    recognizer.adjust_for_ambient_noise(source, duration=2.0)
```

### Language Detection Issues
```python
# Disable auto-detect, use fixed language
engine.stt.set_language(Language.ENGLISH_US)
engine.stt.auto_detect = False
```

## Future Enhancements

- [ ] Offline speech recognition (Whisper)
- [ ] Custom TTS voice cloning
- [ ] Noise cancellation
- [ ] Voice activity detection (VAD)
- [ ] Sentiment analysis (beyond emotion)
- [ ] Intent disambiguation
- [ ] Multi-speaker conversations
- [ ] Voice commands while speaking

## Dependencies

- **SpeechRecognition**: Google Cloud STT
- **pyttsx3**: Offline TTS fallback
- **pyaudio**: Audio input/output
- **ElevenLabs**: High-quality TTS (optional)
- **numpy**: Audio processing
- **PyQt6**: Voice UI

---

**Built with ❤️ for natural voice interaction**
