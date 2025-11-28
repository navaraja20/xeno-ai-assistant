"""
Focus Modes - Context-Aware Work Modes
Different focus modes for various work contexts
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class FocusModeType(Enum):
    """Types of focus modes"""

    DEEP_WORK = "deep_work"  # Intense concentration, no interruptions
    CREATIVE = "creative"  # Creative work, gentle environment
    MEETING = "meeting"  # In meeting, urgent only
    LEARNING = "learning"  # Learning mode, reference materials allowed
    BREAK = "break"  # Taking a break, minimal notifications
    ADMIN = "admin"  # Administrative tasks, all notifications
    CUSTOM = "custom"  # User-defined custom mode


class FocusMode:
    """Focus mode configuration"""

    def __init__(
        self,
        name: str,
        mode_type: FocusModeType = FocusModeType.CUSTOM,
        description: str = "",
        dnd_enabled: bool = True,
        allow_critical: bool = True,
        allow_calendar: bool = False,
        ui_theme: str = "minimal",
        notification_threshold: int = 4,  # Only priority 4+ (HIGH, CRITICAL)
        auto_reply_enabled: bool = False,
        auto_reply_message: str = "",
        background_music: Optional[str] = None,
        screen_filter: Optional[str] = None,
        custom_settings: Dict[str, Any] = None,
    ):
        self.name = name
        self.mode_type = mode_type
        self.description = description
        self.dnd_enabled = dnd_enabled
        self.allow_critical = allow_critical
        self.allow_calendar = allow_calendar
        self.ui_theme = ui_theme
        self.notification_threshold = notification_threshold
        self.auto_reply_enabled = auto_reply_enabled
        self.auto_reply_message = auto_reply_message
        self.background_music = background_music
        self.screen_filter = screen_filter  # e.g., "blue_light_filter", "grayscale"
        self.custom_settings = custom_settings or {}

    def should_allow_notification(self, notification_priority: int) -> bool:
        """Check if notification should be allowed in this mode"""
        if not self.dnd_enabled:
            return True

        if self.allow_critical and notification_priority >= 5:
            return True

        return notification_priority >= self.notification_threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "mode_type": self.mode_type.value,
            "description": self.description,
            "dnd_enabled": self.dnd_enabled,
            "allow_critical": self.allow_critical,
            "allow_calendar": self.allow_calendar,
            "ui_theme": self.ui_theme,
            "notification_threshold": self.notification_threshold,
            "auto_reply_enabled": self.auto_reply_enabled,
            "auto_reply_message": self.auto_reply_message,
            "background_music": self.background_music,
            "screen_filter": self.screen_filter,
            "custom_settings": self.custom_settings,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FocusMode":
        """Create from dictionary"""
        return FocusMode(
            name=data["name"],
            mode_type=FocusModeType(data.get("mode_type", "custom")),
            description=data.get("description", ""),
            dnd_enabled=data.get("dnd_enabled", True),
            allow_critical=data.get("allow_critical", True),
            allow_calendar=data.get("allow_calendar", False),
            ui_theme=data.get("ui_theme", "minimal"),
            notification_threshold=data.get("notification_threshold", 4),
            auto_reply_enabled=data.get("auto_reply_enabled", False),
            auto_reply_message=data.get("auto_reply_message", ""),
            background_music=data.get("background_music"),
            screen_filter=data.get("screen_filter"),
            custom_settings=data.get("custom_settings", {}),
        )


class FocusSession:
    """Active focus mode session"""

    def __init__(
        self,
        mode: FocusMode,
        duration_minutes: Optional[int] = None,
        goal: str = "",
    ):
        self.mode = mode
        self.duration_minutes = duration_minutes
        self.goal = goal
        self.start_time = datetime.now()
        self.end_time = (
            self.start_time + timedelta(minutes=duration_minutes) if duration_minutes else None
        )
        self.paused = False
        self.pause_time: Optional[datetime] = None
        self.total_pause_duration = timedelta()

    def get_elapsed_time(self) -> timedelta:
        """Get elapsed time in session"""
        if self.paused and self.pause_time:
            return self.pause_time - self.start_time - self.total_pause_duration

        return datetime.now() - self.start_time - self.total_pause_duration

    def get_remaining_time(self) -> Optional[timedelta]:
        """Get remaining time in session"""
        if not self.end_time:
            return None

        if self.paused:
            return self.end_time - (self.pause_time or datetime.now())

        return self.end_time - datetime.now()

    def is_complete(self) -> bool:
        """Check if session is complete"""
        if not self.end_time:
            return False

        return datetime.now() >= self.end_time

    def pause(self):
        """Pause session"""
        if not self.paused:
            self.paused = True
            self.pause_time = datetime.now()

    def resume(self):
        """Resume session"""
        if self.paused and self.pause_time:
            pause_duration = datetime.now() - self.pause_time
            self.total_pause_duration += pause_duration
            self.paused = False
            self.pause_time = None

    def extend(self, minutes: int):
        """Extend session duration"""
        if self.end_time:
            self.end_time += timedelta(minutes=minutes)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "mode": self.mode.to_dict(),
            "duration_minutes": self.duration_minutes,
            "goal": self.goal,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "paused": self.paused,
            "elapsed_minutes": self.get_elapsed_time().total_seconds() / 60,
            "remaining_minutes": (
                self.get_remaining_time().total_seconds() / 60
                if self.get_remaining_time()
                else None
            ),
        }


class FocusModeManager:
    """Manages focus modes and sessions"""

    def __init__(self, modes_file: str = "data/focus_modes.json"):
        self.logger = setup_logger("focus.modes")
        self.modes_file = Path(modes_file)
        self.modes: Dict[str, FocusMode] = {}
        self.current_session: Optional[FocusSession] = None
        self.session_callbacks: List[Callable] = []

        # Statistics
        self.session_history: List[Dict[str, Any]] = []

        # Ensure data directory exists
        self.modes_file.parent.mkdir(parents=True, exist_ok=True)

        # Load modes
        self._load_modes()
        self._register_default_modes()

    def add_mode(self, mode: FocusMode):
        """Add or update focus mode"""
        self.modes[mode.name] = mode
        self._save_modes()
        self.logger.info(f"Added focus mode: {mode.name}")

    def get_mode(self, name: str) -> Optional[FocusMode]:
        """Get focus mode by name"""
        return self.modes.get(name)

    def list_modes(self, mode_type: Optional[FocusModeType] = None) -> List[FocusMode]:
        """List all focus modes"""
        modes = list(self.modes.values())

        if mode_type:
            modes = [m for m in modes if m.mode_type == mode_type]

        return modes

    def start_session(
        self,
        mode_name: str,
        duration_minutes: Optional[int] = None,
        goal: str = "",
    ) -> bool:
        """Start a focus session"""
        mode = self.get_mode(mode_name)

        if not mode:
            self.logger.error(f"Mode not found: {mode_name}")
            return False

        # End current session if exists
        if self.current_session:
            self.end_session()

        # Create new session
        self.current_session = FocusSession(mode, duration_minutes, goal)

        # Apply mode settings
        self._apply_mode_settings(mode)

        # Notify callbacks
        self._notify_session_callbacks("session_started", self.current_session)

        self.logger.info(
            f"Started focus session: {mode_name} "
            f"({'unlimited' if not duration_minutes else f'{duration_minutes} minutes'})"
        )

        return True

    def end_session(self):
        """End current focus session"""
        if not self.current_session:
            return

        # Calculate statistics
        elapsed = self.current_session.get_elapsed_time()
        session_data = {
            "mode": self.current_session.mode.name,
            "duration_minutes": elapsed.total_seconds() / 60,
            "goal": self.current_session.goal,
            "completed": self.current_session.is_complete(),
            "start_time": self.current_session.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
        }

        self.session_history.append(session_data)

        # Revert mode settings
        self._revert_mode_settings(self.current_session.mode)

        # Notify callbacks
        self._notify_session_callbacks("session_ended", self.current_session)

        self.logger.info(
            f"Ended focus session: {self.current_session.mode.name} "
            f"({elapsed.total_seconds() / 60:.1f} minutes)"
        )

        self.current_session = None

    def pause_session(self):
        """Pause current session"""
        if self.current_session:
            self.current_session.pause()
            self._notify_session_callbacks("session_paused", self.current_session)
            self.logger.info("Paused focus session")

    def resume_session(self):
        """Resume current session"""
        if self.current_session:
            self.current_session.resume()
            self._notify_session_callbacks("session_resumed", self.current_session)
            self.logger.info("Resumed focus session")

    def extend_session(self, minutes: int):
        """Extend current session"""
        if self.current_session:
            self.current_session.extend(minutes)
            self._notify_session_callbacks("session_extended", self.current_session)
            self.logger.info(f"Extended session by {minutes} minutes")

    def get_current_session(self) -> Optional[FocusSession]:
        """Get current active session"""
        return self.current_session

    def add_session_callback(self, callback: Callable):
        """Add callback for session events"""
        self.session_callbacks.append(callback)

    def get_stats(self) -> Dict[str, Any]:
        """Get focus mode statistics"""
        if not self.session_history:
            return {"total_sessions": 0, "total_minutes": 0}

        total_sessions = len(self.session_history)
        total_minutes = sum(s["duration_minutes"] for s in self.session_history)
        completed_sessions = sum(1 for s in self.session_history if s["completed"])

        # Mode breakdown
        mode_usage = {}
        for session in self.session_history:
            mode = session["mode"]
            if mode not in mode_usage:
                mode_usage[mode] = {"count": 0, "minutes": 0}
            mode_usage[mode]["count"] += 1
            mode_usage[mode]["minutes"] += session["duration_minutes"]

        return {
            "total_sessions": total_sessions,
            "total_minutes": total_minutes,
            "completed_sessions": completed_sessions,
            "completion_rate": (completed_sessions / total_sessions if total_sessions > 0 else 0),
            "mode_usage": mode_usage,
            "current_session": (self.current_session.to_dict() if self.current_session else None),
        }

    def _apply_mode_settings(self, mode: FocusMode):
        """Apply focus mode settings"""
        # TODO: Connect to actual systems

        # DND
        if mode.dnd_enabled:
            self.logger.debug("Enabling DND")

        # UI Theme
        if mode.ui_theme:
            self.logger.debug(f"Applying theme: {mode.ui_theme}")

        # Screen filter
        if mode.screen_filter:
            self.logger.debug(f"Applying screen filter: {mode.screen_filter}")

        # Background music
        if mode.background_music:
            self.logger.debug(f"Starting background music: {mode.background_music}")

    def _revert_mode_settings(self, mode: FocusMode):
        """Revert focus mode settings"""
        # TODO: Revert to previous state
        if mode.dnd_enabled:
            self.logger.debug("Disabling DND")

        if mode.screen_filter:
            self.logger.debug("Removing screen filter")

        if mode.background_music:
            self.logger.debug("Stopping background music")

    def _notify_session_callbacks(self, event: str, session: FocusSession):
        """Notify session callbacks"""
        for callback in self.session_callbacks:
            try:
                callback(event, session)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def _save_modes(self):
        """Save modes to file"""
        try:
            data = {name: mode.to_dict() for name, mode in self.modes.items()}

            with open(self.modes_file, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.debug(f"Saved {len(self.modes)} focus modes")
        except Exception as e:
            self.logger.error(f"Error saving modes: {e}")

    def _load_modes(self):
        """Load modes from file"""
        if not self.modes_file.exists():
            return

        try:
            with open(self.modes_file, "r") as f:
                data = json.load(f)

            for name, mode_data in data.items():
                self.modes[name] = FocusMode.from_dict(mode_data)

            self.logger.info(f"Loaded {len(self.modes)} focus modes")
        except Exception as e:
            self.logger.error(f"Error loading modes: {e}")

    def _register_default_modes(self):
        """Register default focus modes"""

        # Deep Work Mode
        deep_work = FocusMode(
            name="Deep Work",
            mode_type=FocusModeType.DEEP_WORK,
            description="Maximum concentration, zero interruptions",
            dnd_enabled=True,
            allow_critical=False,
            allow_calendar=False,
            ui_theme="minimal_dark",
            notification_threshold=5,  # Only CRITICAL (but DND blocks all)
            auto_reply_enabled=True,
            auto_reply_message="I'm in deep work mode. Will respond later.",
            screen_filter="blue_light_filter",
        )
        self.add_mode(deep_work)

        # Creative Mode
        creative = FocusMode(
            name="Creative",
            mode_type=FocusModeType.CREATIVE,
            description="Creative work with gentle environment",
            dnd_enabled=True,
            allow_critical=True,
            allow_calendar=False,
            ui_theme="creative_light",
            notification_threshold=5,
            background_music="ambient",
        )
        self.add_mode(creative)

        # Meeting Mode
        meeting = FocusMode(
            name="Meeting",
            mode_type=FocusModeType.MEETING,
            description="In a meeting, urgent notifications only",
            dnd_enabled=True,
            allow_critical=True,
            allow_calendar=True,
            ui_theme="minimal",
            notification_threshold=4,  # HIGH and CRITICAL
            auto_reply_enabled=True,
            auto_reply_message="I'm in a meeting. Will get back to you soon.",
        )
        self.add_mode(meeting)

        # Learning Mode
        learning = FocusMode(
            name="Learning",
            mode_type=FocusModeType.LEARNING,
            description="Learning mode, references allowed",
            dnd_enabled=True,
            allow_critical=True,
            allow_calendar=True,
            ui_theme="learning",
            notification_threshold=4,
        )
        self.add_mode(learning)

        # Break Mode
        break_mode = FocusMode(
            name="Break",
            mode_type=FocusModeType.BREAK,
            description="Taking a break, minimal notifications",
            dnd_enabled=True,
            allow_critical=True,
            allow_calendar=False,
            ui_theme="relaxing",
            notification_threshold=4,
            background_music="relaxing",
        )
        self.add_mode(break_mode)

        # Admin Mode
        admin = FocusMode(
            name="Admin",
            mode_type=FocusModeType.ADMIN,
            description="Administrative tasks, all notifications enabled",
            dnd_enabled=False,
            allow_critical=True,
            allow_calendar=True,
            ui_theme="default",
            notification_threshold=2,  # LOW and above
        )
        self.add_mode(admin)


# Global instance
_focus_mode_manager: Optional[FocusModeManager] = None


def get_focus_mode_manager() -> FocusModeManager:
    """Get global focus mode manager"""
    global _focus_mode_manager
    if _focus_mode_manager is None:
        _focus_mode_manager = FocusModeManager()
    return _focus_mode_manager
