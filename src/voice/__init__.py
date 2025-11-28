"""
Voice system for XENO
Speech recognition and text-to-speech
"""
from .commands import VoiceCommandProcessor
from .recognition import VoiceRecognition

__all__ = ["VoiceRecognition", "VoiceCommandProcessor"]
