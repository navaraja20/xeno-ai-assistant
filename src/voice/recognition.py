"""
Speech Recognition for XENO
Handles wake word detection and voice command recognition
"""
import queue
import threading
from pathlib import Path

import speech_recognition as sr

from src.core.logger import setup_logger


class VoiceRecognition:
    """Voice recognition system with wake word detection"""

    def __init__(self, wake_words=None, continuous_mode=True, always_active=True):
        """
        Initialize voice recognition

        Args:
            wake_words: List of wake words (default: ["hey XENO", "XENO"])
            continuous_mode: If True, stays active without needing wake word each time
            always_active: If True, listens to ALL commands without wake word (most hands-free)
        """
        self.logger = setup_logger("voice.recognition")
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Wake words - include common mispronunciations
        self.wake_words = wake_words or [
            "hey XENO",
            "XENO",
            "hey zeno",
            "zeno",
            "hey zenno",
            "zenno",
            "hey sino",
            "sino",
            "hey seno",
            "seno",
        ]

        # Exit words to pause continuous mode
        self.exit_words = [
            "sleep",
            "go to sleep",
            "stop listening",
            "pause",
            "that's all",
            "thanks",
            "thank you",
        ]

        # State
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.listen_thread = None
        self.continuous_mode = continuous_mode  # Continuous listening mode
        self.always_active = always_active  # Always listen without wake word
        self.active_session = always_active  # If always_active, start in active session
        self.wake_detected = False  # Track if wake word was recently detected
        self.last_wake_time = None
        self.last_command_time = None
        self.wake_timeout = 10  # Seconds to wait for command after wake word
        self.session_timeout = 30  # Seconds of silence before pausing continuous mode

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
        import time

        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                    # Try to recognize
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        self.logger.info(f"Heard: {text}")

                        # Check for exit words to pause continuous mode
                        if (self.continuous_mode or self.always_active) and self.active_session:
                            if any(exit_word in text for exit_word in self.exit_words):
                                self.logger.info("Exit command detected, pausing session")
                                self.command_queue.put("__SESSION_PAUSED__")
                                # In always_active mode, don't actually pause
                                if not self.always_active:
                                    self.active_session = False
                                    self.wake_detected = False
                                continue

                        # Check if session timeout in continuous mode (but not always_active)
                        if (
                            self.continuous_mode
                            and not self.always_active
                            and self.active_session
                            and self.last_command_time
                        ):
                            if time.time() - self.last_command_time > self.session_timeout:
                                self.logger.info("Session timeout, pausing")
                                self.active_session = False
                                self.wake_detected = False

                        # Check for wake word
                        if any(wake in text for wake in self.wake_words):
                            self.logger.info("Wake word detected!")

                            # Activate session in continuous mode
                            if self.continuous_mode or self.always_active:
                                self.active_session = True

                            # Activate wake mode
                            self.wake_detected = True
                            self.last_wake_time = time.time()
                            self.last_command_time = time.time()

                            # Put wake word detection signal in queue
                            self.command_queue.put("__WAKE_WORD_DETECTED__")

                            # Remove wake word from command
                            command = text
                            for wake in self.wake_words:
                                command = command.replace(wake, "").strip()

                            if command:
                                self.logger.info(f"Command: {command}")
                                self.command_queue.put(command)
                            # If no command, continuous mode will catch the next phrase

                        # In always_active mode OR (continuous mode and active session), treat everything as command
                        elif self.always_active or (self.continuous_mode and self.active_session):
                            self.logger.info(
                                f"Command ({'always active' if self.always_active else 'continuous mode'}): {text}"
                            )
                            self.command_queue.put(text)
                            self.last_command_time = time.time()

                        # Traditional wake mode (backward compatible)
                        elif self.wake_detected and self.last_wake_time:
                            if time.time() - self.last_wake_time <= self.wake_timeout:
                                self.logger.info(f"Command (wake mode active): {text}")
                                self.command_queue.put(text)
                                self.last_command_time = time.time()
                                # In continuous mode, stay active; otherwise reset
                                if not self.continuous_mode:
                                    self.wake_detected = False
                                    self.last_wake_time = None
                            else:
                                # Wake mode expired
                                self.wake_detected = False
                                self.last_wake_time = None
                                self.active_session = False

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
