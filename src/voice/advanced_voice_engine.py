"""
Advanced Voice Engine for XENO
Features: Custom wake words, multi-language support, emotion analysis, voice biometrics
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import speech_recognition as sr
from collections import deque
import time


class Language(Enum):
    """Supported languages"""
    ENGLISH_US = "en-US"
    ENGLISH_UK = "en-GB"
    SPANISH = "es-ES"
    FRENCH = "fr-FR"
    GERMAN = "de-DE"
    ITALIAN = "it-IT"
    PORTUGUESE = "pt-BR"
    JAPANESE = "ja-JP"
    CHINESE = "zh-CN"
    KOREAN = "ko-KR"
    RUSSIAN = "ru-RU"
    ARABIC = "ar-SA"
    HINDI = "hi-IN"


class Emotion(Enum):
    """Detected emotions"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    CALM = "calm"


@dataclass
class VoiceProfile:
    """User voice profile for biometric recognition"""
    user_id: str
    voice_features: np.ndarray
    sample_count: int
    confidence_threshold: float = 0.85
    created_at: float = 0.0
    last_updated: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_updated == 0.0:
            self.last_updated = time.time()


@dataclass
class ConversationContext:
    """Maintains conversation context for natural dialogue"""
    user_id: str
    messages: deque
    current_topic: Optional[str] = None
    entities: Dict[str, Any] = None
    sentiment_history: List[str] = None
    language: Language = Language.ENGLISH_US
    start_time: float = 0.0
    
    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.sentiment_history is None:
            self.sentiment_history = []
        if self.start_time == 0.0:
            self.start_time = time.time()


class WakeWordDetector:
    """Custom wake word detection using audio pattern matching"""
    
    def __init__(self):
        self.wake_words = {
            "XENO": self._create_pattern("XENO"),
            "hey XENO": self._create_pattern("hey XENO"),
            "ok XENO": self._create_pattern("ok XENO"),
            "computer": self._create_pattern("computer")
        }
        self.sensitivity = 0.7
        self.is_listening = False
        
    def _create_pattern(self, word: str) -> Dict[str, Any]:
        """Create audio pattern for wake word"""
        # In production, this would use actual audio fingerprinting
        # For now, we'll use text-based detection as a fallback
        return {
            'text': word.lower(),
            'phonemes': self._text_to_phonemes(word),
            'duration': len(word) * 0.15,  # Approximate duration
            'samples': []
        }
    
    def _text_to_phonemes(self, text: str) -> List[str]:
        """Convert text to phonemes (simplified)"""
        # In production, use a proper phoneme library
        phoneme_map = {
            'XENO': ['Z', 'IY', 'N', 'OW'],
            'hey': ['HH', 'EY'],
            'ok': ['OW', 'K'],
            'computer': ['K', 'AH', 'M', 'P', 'Y', 'UW', 'T', 'ER']
        }
        return phoneme_map.get(text.lower(), [])
    
    def add_custom_wake_word(self, word: str, samples: List[np.ndarray] = None):
        """Add custom wake word with optional audio samples"""
        pattern = self._create_pattern(word)
        if samples:
            pattern['samples'] = samples
        self.wake_words[word.lower()] = pattern
        
    def detect(self, audio_text: str) -> Tuple[bool, Optional[str]]:
        """Detect wake word in audio/text"""
        text_lower = audio_text.lower().strip()
        
        for wake_word, pattern in self.wake_words.items():
            if pattern['text'] in text_lower:
                return True, wake_word
        
        return False, None
    
    def start(self):
        """Start wake word detection"""
        self.is_listening = True
        
    def stop(self):
        """Stop wake word detection"""
        self.is_listening = False


class EmotionAnalyzer:
    """Analyzes emotion from voice characteristics and text"""
    
    def __init__(self):
        self.emotion_keywords = {
            Emotion.HAPPY: ['great', 'awesome', 'excellent', 'wonderful', 'love', 'happy', 'glad', 'fantastic'],
            Emotion.SAD: ['sad', 'unhappy', 'disappointed', 'depressed', 'unfortunate', 'sorry'],
            Emotion.ANGRY: ['angry', 'furious', 'mad', 'annoyed', 'irritated', 'frustrated'],
            Emotion.EXCITED: ['excited', 'amazing', 'incredible', 'wow', 'yes!', 'perfect'],
            Emotion.FRUSTRATED: ['ugh', 'annoying', 'confusing', 'difficult', 'complicated'],
            Emotion.CONFUSED: ['confused', 'don\'t understand', 'what', 'huh', 'unclear'],
            Emotion.CALM: ['calm', 'peaceful', 'relaxed', 'fine', 'okay', 'alright']
        }
        
    def analyze_text(self, text: str) -> Emotion:
        """Analyze emotion from text content"""
        text_lower = text.lower()
        
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        # Check for exclamation marks (excitement)
        if text.count('!') >= 2:
            return Emotion.EXCITED
        
        # Check for question marks (confusion)
        if text.count('?') >= 2:
            return Emotion.CONFUSED
        
        return Emotion.NEUTRAL
    
    def analyze_audio(self, audio_features: Dict[str, float]) -> Emotion:
        """Analyze emotion from audio features (pitch, energy, tempo)"""
        # In production, use actual audio analysis
        pitch = audio_features.get('pitch', 0)
        energy = audio_features.get('energy', 0)
        tempo = audio_features.get('tempo', 0)
        
        # High pitch + high energy = excited
        if pitch > 0.7 and energy > 0.7:
            return Emotion.EXCITED
        
        # Low pitch + low energy = sad
        if pitch < 0.3 and energy < 0.3:
            return Emotion.SAD
        
        # High energy + fast tempo = angry
        if energy > 0.8 and tempo > 0.7:
            return Emotion.ANGRY
        
        # Medium values = calm
        if 0.4 < pitch < 0.6 and 0.4 < energy < 0.6:
            return Emotion.CALM
        
        return Emotion.NEUTRAL
    
    def analyze(self, text: str, audio_features: Optional[Dict[str, float]] = None) -> Emotion:
        """Combined emotion analysis from text and audio"""
        text_emotion = self.analyze_text(text)
        
        if audio_features:
            audio_emotion = self.analyze_audio(audio_features)
            # Weight audio more heavily as it's more reliable
            if audio_emotion != Emotion.NEUTRAL:
                return audio_emotion
        
        return text_emotion


class VoiceBiometrics:
    """Speaker recognition using voice biometrics"""
    
    def __init__(self):
        self.profiles: Dict[str, VoiceProfile] = {}
        self.feature_dim = 128  # Voice feature vector dimension
        
    def extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """Extract voice features for biometric matching"""
        # In production, use MFCC, i-vectors, or x-vectors
        # For now, simulate with random features
        if len(audio_data) == 0:
            return np.random.randn(self.feature_dim)
        
        # Simulate feature extraction
        features = np.random.randn(self.feature_dim)
        # Normalize
        features = features / np.linalg.norm(features)
        return features
    
    def enroll_user(self, user_id: str, audio_samples: List[np.ndarray]) -> VoiceProfile:
        """Enroll new user with voice samples"""
        # Extract features from all samples
        feature_vectors = [self.extract_features(sample) for sample in audio_samples]
        
        # Average features
        avg_features = np.mean(feature_vectors, axis=0)
        
        # Create profile
        profile = VoiceProfile(
            user_id=user_id,
            voice_features=avg_features,
            sample_count=len(audio_samples)
        )
        
        self.profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, audio_sample: np.ndarray):
        """Update existing voice profile with new sample"""
        if user_id not in self.profiles:
            return
        
        profile = self.profiles[user_id]
        new_features = self.extract_features(audio_sample)
        
        # Moving average
        alpha = 0.1  # Learning rate
        profile.voice_features = (1 - alpha) * profile.voice_features + alpha * new_features
        profile.sample_count += 1
        profile.last_updated = time.time()
    
    def verify_speaker(self, user_id: str, audio_sample: np.ndarray) -> Tuple[bool, float]:
        """Verify if audio matches user's voice profile"""
        if user_id not in self.profiles:
            return False, 0.0
        
        profile = self.profiles[user_id]
        features = self.extract_features(audio_sample)
        
        # Calculate cosine similarity
        similarity = np.dot(profile.voice_features, features)
        
        # Verify against threshold
        verified = similarity >= profile.confidence_threshold
        return verified, similarity
    
    def identify_speaker(self, audio_sample: np.ndarray) -> Tuple[Optional[str], float]:
        """Identify speaker from all enrolled profiles"""
        if not self.profiles:
            return None, 0.0
        
        features = self.extract_features(audio_sample)
        
        best_match = None
        best_score = 0.0
        
        for user_id, profile in self.profiles.items():
            similarity = np.dot(profile.voice_features, features)
            if similarity > best_score:
                best_score = similarity
                best_match = user_id
        
        if best_score >= 0.7:  # Minimum identification threshold
            return best_match, best_score
        
        return None, best_score


class MultiLanguageSTT:
    """Multi-language speech-to-text engine"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {lang.value: lang for lang in Language}
        self.auto_detect = True
        
    def set_language(self, language: Language):
        """Set recognition language"""
        self.auto_detect = False
        self.current_language = language
    
    def enable_auto_detect(self):
        """Enable automatic language detection"""
        self.auto_detect = True
    
    async def recognize(
        self,
        audio_data: sr.AudioData,
        language: Optional[Language] = None
    ) -> Tuple[str, Language, float]:
        """Recognize speech with language detection"""
        
        if language is None and not self.auto_detect:
            language = Language.ENGLISH_US
        
        # Try recognition with specified or detected language
        try:
            if language:
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=language.value
                )
                confidence = 0.9  # Google doesn't return confidence
                return text, language, confidence
            
            # Auto-detect by trying multiple languages
            languages_to_try = [
                Language.ENGLISH_US,
                Language.SPANISH,
                Language.FRENCH,
                Language.GERMAN,
                Language.CHINESE,
                Language.JAPANESE
            ]
            
            best_result = None
            best_confidence = 0.0
            
            for lang in languages_to_try:
                try:
                    text = self.recognizer.recognize_google(
                        audio_data,
                        language=lang.value
                    )
                    # Simple heuristic: longer text = better recognition
                    confidence = min(len(text) / 100, 1.0)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_result = (text, lang, confidence)
                except:
                    continue
            
            if best_result:
                return best_result
            
            # Fallback to English
            text = self.recognizer.recognize_google(audio_data)
            return text, Language.ENGLISH_US, 0.8
            
        except sr.UnknownValueError:
            return "", Language.ENGLISH_US, 0.0
        except sr.RequestError as e:
            raise Exception(f"Speech recognition error: {e}")


class MultiLanguageTTS:
    """Multi-language text-to-speech engine"""
    
    def __init__(self):
        self.voices = self._initialize_voices()
        self.current_language = Language.ENGLISH_US
        
    def _initialize_voices(self) -> Dict[Language, Dict[str, Any]]:
        """Initialize voice configurations for each language"""
        return {
            Language.ENGLISH_US: {'voice': 'en-US-Neural2-C', 'rate': 1.0, 'pitch': 0.0},
            Language.ENGLISH_UK: {'voice': 'en-GB-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.SPANISH: {'voice': 'es-ES-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.FRENCH: {'voice': 'fr-FR-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.GERMAN: {'voice': 'de-DE-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.ITALIAN: {'voice': 'it-IT-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.PORTUGUESE: {'voice': 'pt-BR-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.JAPANESE: {'voice': 'ja-JP-Neural2-B', 'rate': 1.0, 'pitch': 0.0},
            Language.CHINESE: {'voice': 'zh-CN-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.KOREAN: {'voice': 'ko-KR-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.RUSSIAN: {'voice': 'ru-RU-Neural2-A', 'rate': 1.0, 'pitch': 0.0},
            Language.ARABIC: {'voice': 'ar-XA-Wavenet-A', 'rate': 1.0, 'pitch': 0.0},
            Language.HINDI: {'voice': 'hi-IN-Neural2-A', 'rate': 1.0, 'pitch': 0.0}
        }
    
    def set_language(self, language: Language):
        """Set TTS language"""
        self.current_language = language
    
    async def speak(
        self,
        text: str,
        language: Optional[Language] = None,
        emotion: Emotion = Emotion.NEUTRAL
    ) -> bytes:
        """Generate speech with emotion modulation"""
        lang = language or self.current_language
        voice_config = self.voices.get(lang, self.voices[Language.ENGLISH_US])
        
        # Adjust voice parameters based on emotion
        rate = voice_config['rate']
        pitch = voice_config['pitch']
        
        if emotion == Emotion.EXCITED:
            rate *= 1.2
            pitch += 2.0
        elif emotion == Emotion.SAD:
            rate *= 0.8
            pitch -= 2.0
        elif emotion == Emotion.ANGRY:
            rate *= 1.1
            pitch += 1.0
        elif emotion == Emotion.CALM:
            rate *= 0.9
            pitch -= 0.5
        
        # In production, use Google Cloud TTS, ElevenLabs, or Azure
        # For now, return placeholder
        print(f"Speaking ({lang.value}, {emotion.value}): {text}")
        print(f"  Rate: {rate}, Pitch: {pitch}")
        
        return b""  # Placeholder for audio bytes


class ConversationManager:
    """Manages natural conversation flow with context"""
    
    def __init__(self):
        self.contexts: Dict[str, ConversationContext] = {}
        self.max_history = 10
        
    def get_context(self, user_id: str) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.contexts:
            self.contexts[user_id] = ConversationContext(
                user_id=user_id,
                messages=deque(maxlen=self.max_history)
            )
        return self.contexts[user_id]
    
    def add_message(self, user_id: str, role: str, content: str, emotion: Emotion = Emotion.NEUTRAL):
        """Add message to conversation history"""
        context = self.get_context(user_id)
        
        message = {
            'role': role,
            'content': content,
            'emotion': emotion.value,
            'timestamp': time.time()
        }
        
        context.messages.append(message)
        context.sentiment_history.append(emotion.value)
        
    def extract_entities(self, text: str, context: ConversationContext) -> Dict[str, Any]:
        """Extract entities from text"""
        # Simple entity extraction (in production, use NER model)
        entities = context.entities.copy()
        
        # Extract dates
        date_keywords = ['today', 'tomorrow', 'yesterday', 'next week', 'next month']
        for keyword in date_keywords:
            if keyword in text.lower():
                entities['date'] = keyword
        
        # Extract times
        time_keywords = ['morning', 'afternoon', 'evening', 'night', 'noon']
        for keyword in time_keywords:
            if keyword in text.lower():
                entities['time'] = keyword
        
        # Extract names (simple pattern)
        import re
        names = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', text)
        if names:
            entities['person'] = names[0]
        
        context.entities = entities
        return entities
    
    def detect_topic_change(self, current_text: str, context: ConversationContext) -> bool:
        """Detect if conversation topic has changed"""
        if not context.messages:
            return True
        
        last_message = context.messages[-1]['content']
        
        # Simple topic detection (in production, use topic modeling)
        keywords_current = set(current_text.lower().split())
        keywords_last = set(last_message.lower().split())
        
        # Calculate overlap
        overlap = len(keywords_current & keywords_last) / max(len(keywords_current), 1)
        
        # Topic changed if less than 30% overlap
        return overlap < 0.3
    
    def get_context_summary(self, user_id: str) -> str:
        """Get summary of conversation context"""
        context = self.get_context(user_id)
        
        if not context.messages:
            return "No conversation history."
        
        summary_parts = []
        
        if context.current_topic:
            summary_parts.append(f"Current topic: {context.current_topic}")
        
        if context.entities:
            summary_parts.append(f"Entities: {', '.join(f'{k}={v}' for k, v in context.entities.items())}")
        
        recent_sentiment = context.sentiment_history[-3:] if context.sentiment_history else []
        if recent_sentiment:
            summary_parts.append(f"Recent emotions: {', '.join(recent_sentiment)}")
        
        return " | ".join(summary_parts)


class AdvancedVoiceEngine:
    """Main advanced voice engine integrating all components"""
    
    def __init__(self):
        self.wake_word_detector = WakeWordDetector()
        self.emotion_analyzer = EmotionAnalyzer()
        self.voice_biometrics = VoiceBiometrics()
        self.stt = MultiLanguageSTT()
        self.tts = MultiLanguageTTS()
        self.conversation_manager = ConversationManager()
        
        self.current_user: Optional[str] = None
        self.is_active = False
        
    async def initialize(self):
        """Initialize voice engine"""
        self.wake_word_detector.start()
        self.is_active = True
        print("Advanced Voice Engine initialized")
    
    async def process_audio(self, audio_data: sr.AudioData) -> Dict[str, Any]:
        """Process audio input with full pipeline"""
        result = {
            'success': False,
            'text': '',
            'language': Language.ENGLISH_US,
            'emotion': Emotion.NEUTRAL,
            'user_id': None,
            'confidence': 0.0
        }
        
        try:
            # Convert to numpy array for biometrics
            audio_np = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Speaker identification
            user_id, speaker_confidence = self.voice_biometrics.identify_speaker(audio_np)
            result['user_id'] = user_id
            self.current_user = user_id
            
            # Speech recognition with language detection
            text, language, stt_confidence = await self.stt.recognize(audio_data)
            result['text'] = text
            result['language'] = language
            result['confidence'] = stt_confidence
            
            if not text:
                return result
            
            # Wake word detection
            wake_detected, wake_word = self.wake_word_detector.detect(text)
            result['wake_word_detected'] = wake_detected
            result['wake_word'] = wake_word
            
            # Emotion analysis
            audio_features = {
                'pitch': np.random.rand(),
                'energy': np.random.rand(),
                'tempo': np.random.rand()
            }
            emotion = self.emotion_analyzer.analyze(text, audio_features)
            result['emotion'] = emotion
            
            # Update conversation context
            if user_id:
                self.conversation_manager.add_message(user_id, 'user', text, emotion)
                context = self.conversation_manager.get_context(user_id)
                
                # Extract entities
                entities = self.conversation_manager.extract_entities(text, context)
                result['entities'] = entities
                
                # Detect topic change
                topic_changed = self.conversation_manager.detect_topic_change(text, context)
                result['topic_changed'] = topic_changed
                
                # Get context summary
                result['context_summary'] = self.conversation_manager.get_context_summary(user_id)
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def respond(
        self,
        text: str,
        user_id: Optional[str] = None,
        emotion: Emotion = Emotion.NEUTRAL,
        language: Optional[Language] = None
    ) -> bytes:
        """Generate voice response"""
        if user_id:
            # Add to conversation history
            self.conversation_manager.add_message(user_id, 'assistant', text, emotion)
        
        # Generate speech
        audio = await self.tts.speak(text, language, emotion)
        return audio
    
    def enroll_user(self, user_id: str, audio_samples: List[np.ndarray]):
        """Enroll user for voice biometrics"""
        profile = self.voice_biometrics.enroll_user(user_id, audio_samples)
        print(f"User {user_id} enrolled with {profile.sample_count} samples")
        return profile
    
    def add_custom_wake_word(self, word: str):
        """Add custom wake word"""
        self.wake_word_detector.add_custom_wake_word(word)
        print(f"Custom wake word '{word}' added")
    
    def set_language(self, language: Language):
        """Set primary language"""
        self.stt.set_language(language)
        self.tts.set_language(language)
    
    async def shutdown(self):
        """Shutdown voice engine"""
        self.wake_word_detector.stop()
        self.is_active = False
        print("Advanced Voice Engine shutdown")
