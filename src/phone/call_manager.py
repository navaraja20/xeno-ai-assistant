"""
Phone Call Integration
Twilio-based voice calling system
"""

import os
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from twilio.rest import Client
from twilio.twiml.voice_response import Gather, VoiceResponse

from src.core.logger import setup_logger


class CallStatus:
    """Call status constants"""

    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"


class Call:
    """Represents a phone call"""

    def __init__(
        self,
        call_sid: str,
        from_number: str,
        to_number: str,
        direction: str,
        status: str,
        duration: Optional[int] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None,
        recording_url: Optional[str] = None,
    ):
        self.call_sid = call_sid
        self.from_number = from_number
        self.to_number = to_number
        self.direction = direction  # "inbound" or "outbound"
        self.status = status
        self.duration = duration  # seconds
        self.started_at = started_at or datetime.now()
        self.ended_at = ended_at
        self.recording_url = recording_url
        self.transcription: Optional[str] = None
        self.notes: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "call_sid": self.call_sid,
            "from_number": self.from_number,
            "to_number": self.to_number,
            "direction": self.direction,
            "status": self.status,
            "duration": self.duration,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "recording_url": self.recording_url,
            "transcription": self.transcription,
            "notes": self.notes,
        }

    @staticmethod
    def from_twilio_call(twilio_call) -> "Call":
        """Create from Twilio call object"""
        return Call(
            call_sid=twilio_call.sid,
            from_number=twilio_call.from_,
            to_number=twilio_call.to,
            direction=twilio_call.direction,
            status=twilio_call.status,
            duration=twilio_call.duration,
            started_at=twilio_call.start_time,
            ended_at=twilio_call.end_time,
        )


class CallManager:
    """Manages phone calls via Twilio"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self.logger = setup_logger("phone.call_manager")

        # Twilio credentials
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        # Initialize Twilio client
        self.client: Optional[Client] = None
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.logger.info("Twilio client initialized")
        else:
            self.logger.warning("Twilio credentials not found in environment")

        # Call history
        self.call_history: List[Call] = []

        # Event callbacks
        self.on_call_started: Optional[Callable[[Call], None]] = None
        self.on_call_ended: Optional[Callable[[Call], None]] = None
        self.on_call_failed: Optional[Callable[[Call, str], None]] = None

        self._initialized = True

    def is_configured(self) -> bool:
        """Check if Twilio is properly configured"""
        return self.client is not None and self.phone_number is not None

    def make_call(
        self,
        to_number: str,
        message: Optional[str] = None,
        record: bool = False,
        ai_assistant: bool = False,
    ) -> Optional[Call]:
        """
        Make an outbound phone call

        Args:
            to_number: Phone number to call
            message: Optional message to speak (TTS)
            record: Whether to record the call
            ai_assistant: Whether to enable AI assistant during call
        """
        if not self.is_configured():
            self.logger.error("Twilio not configured")
            return None

        try:
            # Create TwiML response
            twiml = VoiceResponse()

            if message:
                # Text-to-speech message
                twiml.say(message, voice="alice")

            if ai_assistant:
                # Enable AI assistant (interactive)
                gather = Gather(
                    input="speech",
                    action="/voice/handle-speech",
                    speech_timeout="auto",
                    language="en-US",
                )
                gather.say("How can I help you?", voice="alice")
                twiml.append(gather)

            # Make the call
            twilio_call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                twiml=str(twiml),
                record=record,
                recording_status_callback="/voice/recording-status" if record else None,
            )

            # Create Call object
            call = Call.from_twilio_call(twilio_call)
            self.call_history.append(call)

            self.logger.info(f"Call initiated to {to_number}: {call.call_sid}")

            if self.on_call_started:
                self.on_call_started(call)

            return call

        except Exception as e:
            self.logger.error(f"Failed to make call: {e}")
            if self.on_call_failed:
                self.on_call_failed(None, str(e))
            return None

    def answer_call(self, call_sid: str, greeting: Optional[str] = None) -> VoiceResponse:
        """
        Generate TwiML response for incoming call

        Args:
            call_sid: Twilio call SID
            greeting: Optional greeting message
        """
        twiml = VoiceResponse()

        # Greeting
        if greeting:
            twiml.say(greeting, voice="alice")
        else:
            twiml.say("Hello! This is XENO, your AI assistant.", voice="alice")

        # Gather speech input
        gather = Gather(
            input="speech",
            action=f"/voice/handle-speech?call_sid={call_sid}",
            speech_timeout="auto",
            language="en-US",
        )
        gather.say("What can I help you with?", voice="alice")
        twiml.append(gather)

        # Fallback
        twiml.say("I didn't catch that. Goodbye!", voice="alice")
        twiml.hangup()

        return twiml

    def handle_speech(
        self,
        speech_text: str,
        call_sid: str,
        ai_response_generator: Optional[Callable[[str], str]] = None,
    ) -> VoiceResponse:
        """
        Handle speech input during call

        Args:
            speech_text: Transcribed speech from caller
            call_sid: Twilio call SID
            ai_response_generator: Function to generate AI response
        """
        twiml = VoiceResponse()

        self.logger.info(f"Speech received on {call_sid}: {speech_text}")

        # Generate AI response
        if ai_response_generator:
            response = ai_response_generator(speech_text)
        else:
            response = f"You said: {speech_text}. How can I help you further?"

        # Speak response
        twiml.say(response, voice="alice")

        # Continue gathering
        gather = Gather(
            input="speech",
            action=f"/voice/handle-speech?call_sid={call_sid}",
            speech_timeout="auto",
            language="en-US",
        )
        gather.say("Is there anything else?", voice="alice")
        twiml.append(gather)

        # End call
        twiml.say("Thank you for calling. Goodbye!", voice="alice")
        twiml.hangup()

        return twiml

    def end_call(self, call_sid: str) -> bool:
        """End an active call"""
        if not self.is_configured():
            return False

        try:
            call = self.client.calls(call_sid).update(status="completed")

            # Update call history
            for c in self.call_history:
                if c.call_sid == call_sid:
                    c.status = CallStatus.COMPLETED
                    c.ended_at = datetime.now()

                    if self.on_call_ended:
                        self.on_call_ended(c)
                    break

            self.logger.info(f"Call ended: {call_sid}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to end call: {e}")
            return False

    def get_call_status(self, call_sid: str) -> Optional[str]:
        """Get current status of a call"""
        if not self.is_configured():
            return None

        try:
            call = self.client.calls(call_sid).fetch()

            # Update call history
            for c in self.call_history:
                if c.call_sid == call_sid:
                    c.status = call.status
                    c.duration = call.duration
                    c.ended_at = call.end_time
                    break

            return call.status

        except Exception as e:
            self.logger.error(f"Failed to get call status: {e}")
            return None

    def get_call_recording(self, call_sid: str) -> Optional[str]:
        """Get recording URL for a call"""
        if not self.is_configured():
            return None

        try:
            recordings = self.client.recordings.list(call_sid=call_sid, limit=1)

            if recordings:
                recording = recordings[0]
                url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"

                # Update call history
                for c in self.call_history:
                    if c.call_sid == call_sid:
                        c.recording_url = url
                        break

                return url

            return None

        except Exception as e:
            self.logger.error(f"Failed to get recording: {e}")
            return None

    def get_call_history(
        self,
        limit: int = 50,
        direction: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Call]:
        """
        Get call history

        Args:
            limit: Maximum number of calls to return
            direction: Filter by direction ("inbound" or "outbound")
            status: Filter by status
        """
        filtered = self.call_history

        if direction:
            filtered = [c for c in filtered if c.direction == direction]

        if status:
            filtered = [c for c in filtered if c.status == status]

        return filtered[-limit:]

    def get_recent_calls(self, limit: int = 10) -> List[Call]:
        """Get most recent calls"""
        return self.call_history[-limit:]

    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS message

        Args:
            to_number: Phone number to send to
            message: Message text
        """
        if not self.is_configured():
            return False

        try:
            self.client.messages.create(
                to=to_number,
                from_=self.phone_number,
                body=message,
            )

            self.logger.info(f"SMS sent to {to_number}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send SMS: {e}")
            return False

    def add_call_note(self, call_sid: str, note: str):
        """Add note to a call"""
        for call in self.call_history:
            if call.call_sid == call_sid:
                call.notes.append(note)
                self.logger.info(f"Note added to call {call_sid}")
                break

    def get_call_statistics(self) -> Dict[str, Any]:
        """Get call statistics"""
        total = len(self.call_history)
        inbound = len([c for c in self.call_history if c.direction == "inbound"])
        outbound = total - inbound

        completed = len([c for c in self.call_history if c.status == CallStatus.COMPLETED])
        failed = len([c for c in self.call_history if c.status == CallStatus.FAILED])

        durations = [c.duration for c in self.call_history if c.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_calls": total,
            "inbound_calls": inbound,
            "outbound_calls": outbound,
            "completed_calls": completed,
            "failed_calls": failed,
            "average_duration": avg_duration,
            "total_duration": sum(durations),
        }


def get_call_manager() -> CallManager:
    """Get CallManager singleton"""
    return CallManager()
