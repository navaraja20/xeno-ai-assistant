"""
Speech Recognition for XENO
Handles wake word detection and voice command recognition
"""
import speech_recognition as sr
import threading
import queue
from pathlib import Path
from src.core.logger import setup_logger


class VoiceRecognition:
    """Voice recognition system with wake word detection"""
    
    def __init__(self, wake_words=None):
        """
        Initialize voice recognition
        
        Args:
            wake_words: List of wake words (default: ["hey xeno", "xeno"])
        """
        self.logger = setup_logger("voice.recognition")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Wake words - include common mispronunciations
        self.wake_words = wake_words or [
            "hey xeno", "xeno", 
            "hey zeno", "zeno",
            "hey zenno", "zenno",
            "hey sino", "sino",
            "hey seno", "seno"
        ]
        
        # State
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.listen_thread = None
        
        # Adjust for ambient noise
        try:
            with self.microphone as source:
                self.logger.info("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Voice recognition ready!")
        except Exception as e:
            self.logger.error(f"Failed to initialize microphone: {e}")
    
    def start_listening(self):
        """Start continuous listening for wake word"""
        if self.is_listening:
            self.logger.warning("Already listening")
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        self.logger.info("Started listening for wake word...")
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        self.logger.info("Stopped listening")
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Try to recognize
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        self.logger.info(f"Heard: {text}")
                        
                        # Check for wake word
                        if any(wake in text for wake in self.wake_words):
                            self.logger.info("Wake word detected!")
                            
                            # Put wake word detection signal in queue
                            self.command_queue.put("__WAKE_WORD_DETECTED__")
                            
                            # Remove wake word from command
                            command = text
                            for wake in self.wake_words:
                                command = command.replace(wake, "").strip()
                            
                            if command:
                                self.logger.info(f"Command: {command}")
                                self.command_queue.put(command)
                            else:
                                # No command after wake word, listen for one more phrase
                                self._listen_for_command()
                        
                    except sr.UnknownValueError:
                        # Could not understand audio
                        pass
                    except sr.RequestError as e:
                        self.logger.error(f"Recognition service error: {e}")
                        
            except sr.WaitTimeoutError:
                # No speech detected, continue
                pass
            except Exception as e:
                self.logger.error(f"Error in listen loop: {e}")
    
    def _listen_for_command(self):
        """Listen specifically for a command after wake word"""
        try:
            with self.microphone as source:
                self.logger.info("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                command = self.recognizer.recognize_google(audio).lower()
                self.logger.info(f"Command: {command}")
                self.command_queue.put(command)
                
        except sr.WaitTimeoutError:
            self.logger.warning("No command heard")
        except sr.UnknownValueError:
            self.logger.warning("Could not understand command")
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
    
    def get_command(self, block=False, timeout=None):
        """
        Get next command from queue
        
        Args:
            block: Whether to block until command available
            timeout: Timeout in seconds (only if block=True)
            
        Returns:
            Command string or None
        """
        try:
            return self.command_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def listen_once(self):
        """
        Listen for a single command (blocking)
        
        Returns:
            Recognized text or None
        """
        try:
            with self.microphone as source:
                self.logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio).lower()
                self.logger.info(f"Heard: {text}")
                return text
                
        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
