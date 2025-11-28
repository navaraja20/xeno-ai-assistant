"""
Context Detector
Detects context (time, activity, emotion, location) for theme selection
"""

from datetime import datetime, time
from enum import Enum
from typing import Optional

from src.core.logger import setup_logger
from src.ui.theme_engine import ActivityContext, EmotionState


class TimeOfDay(Enum):
    """Time of day periods"""

    EARLY_MORNING = "early_morning"  # 5-8 AM
    MORNING = "morning"  # 8-12 PM
    AFTERNOON = "afternoon"  # 12-5 PM
    EVENING = "evening"  # 5-9 PM
    NIGHT = "night"  # 9 PM - 5 AM


class WeatherCondition(Enum):
    """Weather conditions"""

    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    UNKNOWN = "unknown"


class ContextDetector:
    """Detects various contextual information"""

    def __init__(self):
        self.logger = setup_logger("theme.context")

        # Current state
        self.current_activity: Optional[ActivityContext] = None
        self.current_emotion: Optional[EmotionState] = None
        self.manual_override = False

    def detect_time_of_day(self) -> TimeOfDay:
        """Detect current time of day period"""

        current_time = datetime.now().time()

        if time(5, 0) <= current_time < time(8, 0):
            return TimeOfDay.EARLY_MORNING
        elif time(8, 0) <= current_time < time(12, 0):
            return TimeOfDay.MORNING
        elif time(12, 0) <= current_time < time(17, 0):
            return TimeOfDay.AFTERNOON
        elif time(17, 0) <= current_time < time(21, 0):
            return TimeOfDay.EVENING
        else:
            return TimeOfDay.NIGHT

    def detect_activity_context(self) -> ActivityContext:
        """Detect current activity context"""

        if self.manual_override and self.current_activity:
            return self.current_activity

        # Auto-detect based on various signals

        # Check focus mode
        focus_mode = self._check_focus_mode()
        if focus_mode:
            return focus_mode

        # Check calendar
        calendar_context = self._check_calendar_context()
        if calendar_context:
            return calendar_context

        # Check time patterns
        time_context = self._detect_time_based_activity()
        if time_context:
            return time_context

        return ActivityContext.DEFAULT

    def detect_emotion_state(self) -> EmotionState:
        """Detect current emotional state"""

        if self.manual_override and self.current_emotion:
            return self.current_emotion

        # Auto-detect based on various signals

        # Check activity patterns
        emotion = self._detect_emotion_from_activity()
        if emotion:
            return emotion

        # Check time of day
        time_emotion = self._detect_emotion_from_time()
        if time_emotion:
            return time_emotion

        return EmotionState.NEUTRAL

    def set_manual_activity(self, activity: ActivityContext):
        """Manually set activity context"""
        self.current_activity = activity
        self.manual_override = True
        self.logger.info(f"Manual activity set: {activity.value}")

    def set_manual_emotion(self, emotion: EmotionState):
        """Manually set emotion state"""
        self.current_emotion = emotion
        self.manual_override = True
        self.logger.info(f"Manual emotion set: {emotion.value}")

    def clear_manual_override(self):
        """Clear manual overrides"""
        self.manual_override = False
        self.current_activity = None
        self.current_emotion = None
        self.logger.info("Manual overrides cleared")

    def get_theme_suggestion(self) -> str:
        """Get theme suggestion based on context"""

        time_of_day = self.detect_time_of_day()
        activity = self.detect_activity_context()
        emotion = self.detect_emotion_state()

        # Priority: Activity > Emotion > Time

        # Activity-based themes
        activity_themes = {
            ActivityContext.FOCUS: "focus_minimal",
            ActivityContext.CREATIVE: "creative_vibrant",
            ActivityContext.MEETING: "meeting_professional",
            ActivityContext.RELAX: "relax_calm",
            ActivityContext.ADMIN: "light_modern",
        }

        if activity != ActivityContext.DEFAULT:
            return activity_themes.get(activity, "light_modern")

        # Emotion-based themes
        emotion_themes = {
            EmotionState.CALM: "relax_calm",
            EmotionState.ENERGIZED: "energized_bright",
            EmotionState.STRESSED: "calm_soothing",
        }

        if emotion != EmotionState.NEUTRAL:
            return emotion_themes.get(emotion, "light_modern")

        # Time-based themes
        time_themes = {
            TimeOfDay.EARLY_MORNING: "light_modern",
            TimeOfDay.MORNING: "energized_bright",
            TimeOfDay.AFTERNOON: "light_modern",
            TimeOfDay.EVENING: "relax_calm",
            TimeOfDay.NIGHT: "dark_modern",
        }

        return time_themes.get(time_of_day, "light_modern")

    def is_work_hours(self) -> bool:
        """Check if current time is work hours"""
        current_time = datetime.now().time()
        return time(9, 0) <= current_time < time(17, 0)

    def is_weekend(self) -> bool:
        """Check if today is weekend"""
        return datetime.now().weekday() >= 5

    def _check_focus_mode(self) -> Optional[ActivityContext]:
        """Check if focus mode is active"""
        try:
            from src.voice.focus_modes import get_focus_mode_manager

            manager = get_focus_mode_manager()
            session = manager.get_current_session()

            if session:
                mode_type = session.mode.mode_type.value

                if "deep" in mode_type or "focus" in mode_type:
                    return ActivityContext.FOCUS
                elif "creative" in mode_type:
                    return ActivityContext.CREATIVE
                elif "meeting" in mode_type:
                    return ActivityContext.MEETING
                elif "break" in mode_type or "relax" in mode_type:
                    return ActivityContext.RELAX

        except Exception as e:
            self.logger.debug(f"Could not check focus mode: {e}")

        return None

    def _check_calendar_context(self) -> Optional[ActivityContext]:
        """Check calendar for context clues"""
        # TODO: Integrate with calendar manager

        # Check if there's a meeting in next 15 minutes
        # If yes, return ActivityContext.MEETING

        return None

    def _detect_time_based_activity(self) -> Optional[ActivityContext]:
        """Detect activity based on time patterns"""

        time_of_day = self.detect_time_of_day()

        # Morning: typically admin/planning
        if time_of_day == TimeOfDay.EARLY_MORNING:
            return ActivityContext.ADMIN

        # Night: typically relax
        if time_of_day == TimeOfDay.NIGHT:
            return ActivityContext.RELAX

        # Work hours: default to focus if weekday
        if self.is_work_hours() and not self.is_weekend():
            return ActivityContext.FOCUS

        return None

    def _detect_emotion_from_activity(self) -> Optional[EmotionState]:
        """Detect emotion from activity patterns"""

        # Check recent productivity
        try:
            from src.modules.productivity_scorer import get_productivity_scorer

            scorer = get_productivity_scorer()
            score = scorer.calculate_productivity_score()

            if score >= 80:
                return EmotionState.ENERGIZED
            elif score < 50:
                return EmotionState.STRESSED

        except Exception as e:
            self.logger.debug(f"Could not check productivity: {e}")

        return None

    def _detect_emotion_from_time(self) -> Optional[EmotionState]:
        """Detect emotion from time of day"""

        time_of_day = self.detect_time_of_day()

        # Morning: energized
        if time_of_day in [TimeOfDay.EARLY_MORNING, TimeOfDay.MORNING]:
            return EmotionState.ENERGIZED

        # Evening/Night: calm
        if time_of_day in [TimeOfDay.EVENING, TimeOfDay.NIGHT]:
            return EmotionState.CALM

        return None

    def get_context_summary(self) -> dict:
        """Get summary of current context"""

        return {
            "time_of_day": self.detect_time_of_day().value,
            "activity": self.detect_activity_context().value,
            "emotion": self.detect_emotion_state().value,
            "is_work_hours": self.is_work_hours(),
            "is_weekend": self.is_weekend(),
            "suggested_theme": self.get_theme_suggestion(),
            "manual_override": self.manual_override,
        }


# Global instance
_context_detector: Optional[ContextDetector] = None


def get_context_detector() -> ContextDetector:
    """Get global context detector"""
    global _context_detector
    if _context_detector is None:
        _context_detector = ContextDetector()
    return _context_detector
