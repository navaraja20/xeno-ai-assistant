"""
Voice system for XENO
Speech recognition and text-to-speech
"""
from .recognition import VoiceRecognition
from .commands import VoiceCommandProcessor

__all__ = ['VoiceRecognition', 'VoiceCommandProcessor']
