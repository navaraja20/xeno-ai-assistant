"""
Voice Assistant for Phone Calls
AI-powered assistant during phone conversations
"""

import re
from typing import Any, Dict, Optional

from src.core.logger import setup_logger
from src.phone.call_manager import get_call_manager


class VoiceAssistant:
    """AI assistant for phone calls"""

    def __init__(self):
        self.logger = setup_logger("phone.voice_assistant")
        self.call_manager = get_call_manager()

        # Intent patterns
        self.intent_patterns = {
            "schedule_meeting": [
                r"schedule.*meeting",
                r"book.*appointment",
                r"set.*calendar",
            ],
            "check_email": [
                r"check.*email",
                r"read.*email",
                r"any.*messages",
            ],
            "check_calendar": [
                r"what.*schedule",
                r"check.*calendar",
                r"what.*today",
                r"what.*meetings",
            ],
            "send_email": [
                r"send.*email",
                r"email.*to",
                r"compose.*email",
            ],
            "create_task": [
                r"create.*task",
                r"add.*todo",
                r"remind.*me",
            ],
            "check_weather": [
                r"weather",
                r"forecast",
                r"temperature",
            ],
            "tell_joke": [
                r"tell.*joke",
                r"make.*laugh",
                r"something.*funny",
            ],
        }

        # Response templates
        self.responses = {
            "greeting": "Hello! This is XENO, your AI assistant. How can I help you today?",
            "schedule_meeting": "I can help you schedule a meeting. What time works for you?",
            "check_email": "Let me check your emails. You have {count} unread messages.",
            "check_calendar": "Your next meeting is {event} at {time}.",
            "send_email": "Who would you like to send an email to?",
            "create_task": "What task would you like me to add?",
            "check_weather": "The current weather is {weather} with a temperature of {temp} degrees.",
            "tell_joke": "Why did the AI go to therapy? It had too many layers!",
            "unknown": "I'm not sure I understand. Could you rephrase that?",
            "goodbye": "Thank you for calling. Have a great day!",
        }

    def detect_intent(self, text: str) -> str:
        """Detect intent from spoken text"""
        text_lower = text.lower()

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    self.logger.info(f"Intent detected: {intent}")
                    return intent

        return "unknown"

    def generate_response(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response to spoken input

        Args:
            text: Transcribed speech from caller
            context: Optional context (call info, user data, etc.)
        """
        context = context or {}

        # Detect intent
        intent = self.detect_intent(text)

        # Get base response
        response = self.responses.get(intent, self.responses["unknown"])

        # Personalize response with context
        if intent == "check_email" and "email_count" in context:
            response = response.format(count=context["email_count"])
        elif intent == "check_calendar" and "next_event" in context:
            response = response.format(
                event=context["next_event"]["title"],
                time=context["next_event"]["time"],
            )
        elif intent == "check_weather" and "weather" in context:
            response = response.format(
                weather=context["weather"]["condition"],
                temp=context["weather"]["temperature"],
            )

        self.logger.info(f"Generated response for intent '{intent}': {response}")

        return response

    def handle_call(self, caller_number: str, speech_text: Optional[str] = None) -> str:
        """
        Handle incoming call

        Args:
            caller_number: Phone number of caller
            speech_text: Transcribed speech (if available)
        """
        if not speech_text:
            return self.responses["greeting"]

        # Detect goodbye intent
        if any(word in speech_text.lower() for word in ["bye", "goodbye", "thank you"]):
            return self.responses["goodbye"]

        # Generate context (in real implementation, fetch from database)
        context = {
            "email_count": 5,  # Mock data
            "next_event": {
                "title": "Team Standup",
                "time": "10:00 AM",
            },
            "weather": {
                "condition": "sunny",
                "temperature": 72,
            },
        }

        return self.generate_response(speech_text, context)

    def make_ai_call(
        self,
        to_number: str,
        initial_message: str,
        enable_conversation: bool = True,
    ) -> Optional[str]:
        """
        Make an AI-powered call

        Args:
            to_number: Phone number to call
            initial_message: Initial message to speak
            enable_conversation: Whether to enable back-and-forth conversation
        """
        call = self.call_manager.make_call(
            to_number=to_number,
            message=initial_message,
            record=True,
            ai_assistant=enable_conversation,
        )

        if call:
            self.logger.info(f"AI call initiated: {call.call_sid}")
            return call.call_sid

        return None

    def schedule_reminder_call(
        self,
        to_number: str,
        reminder_message: str,
        scheduled_time: str,
    ) -> bool:
        """
        Schedule a reminder call

        Args:
            to_number: Phone number to call
            reminder_message: Reminder message to speak
            scheduled_time: When to make the call (ISO format)
        """
        # In real implementation, store in database and use scheduler
        self.logger.info(f"Reminder call scheduled for {scheduled_time}: {reminder_message}")
        return True

    def get_call_summary(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """
        Get summary of a call

        Args:
            call_sid: Twilio call SID
        """
        # Find call in history
        for call in self.call_manager.call_history:
            if call.call_sid == call_sid:
                return {
                    "call_sid": call_sid,
                    "duration": call.duration,
                    "direction": call.direction,
                    "status": call.status,
                    "transcription": call.transcription,
                    "notes": call.notes,
                    "recording_url": call.recording_url,
                }

        return None


def get_voice_assistant() -> VoiceAssistant:
    """Get VoiceAssistant singleton"""
    return VoiceAssistant()
