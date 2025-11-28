"""
XP System
Experience points, levels, and progression tracking
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class XPEvent:
    """XP earning event"""

    def __init__(
        self,
        event_type: str,
        amount: int,
        description: str,
        timestamp: datetime = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.event_type = event_type
        self.amount = amount
        self.description = description
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "event_type": self.event_type,
            "amount": self.amount,
            "description": self.description,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "XPEvent":
        """Create from dictionary"""
        return cls(
            event_type=data["event_type"],
            amount=data["amount"],
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


class XPSystem:
    """Manages XP, levels, and progression"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("gamification.xp")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "gamification"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.xp_file = self.storage_path / "xp_data.json"

        # XP configuration
        self.xp_rewards = {
            # Task completion
            "task_complete": 10,
            "task_complete_early": 15,
            "task_complete_streak": 20,
            # Communication
            "email_sent": 5,
            "email_processed": 2,
            "meeting_completed": 15,
            # Productivity
            "focus_session": 25,
            "pomodoro_complete": 20,
            "daily_goal_met": 50,
            # Learning
            "tutorial_complete": 30,
            "skill_learned": 100,
            # System usage
            "first_login_day": 10,
            "consecutive_days": 5,
            "voice_command": 3,
            "workflow_created": 50,
            "plugin_installed": 25,
        }

        # Level configuration
        self.base_xp = 100
        self.xp_multiplier = 1.5

        # User data
        self.total_xp = 0
        self.current_level = 1
        self.xp_history: List[XPEvent] = []

        # Load data
        self._load_data()

    def award_xp(
        self,
        event_type: str,
        multiplier: float = 1.0,
        description: str = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Award XP for an event"""
        # Get base XP for event type
        base_xp = self.xp_rewards.get(event_type, 0)
        if base_xp == 0:
            self.logger.warning(f"Unknown event type: {event_type}")
            return {"xp_awarded": 0, "level_up": False}

        # Calculate final XP
        xp_amount = int(base_xp * multiplier)

        # Create event
        event_description = description or f"Earned XP for {event_type}"
        event = XPEvent(event_type, xp_amount, event_description, metadata=metadata)

        # Record event
        self.xp_history.append(event)

        # Update total XP
        old_level = self.current_level
        self.total_xp += xp_amount

        # Check for level up
        new_level = self.calculate_level(self.total_xp)
        level_up = new_level > old_level

        if level_up:
            self.current_level = new_level
            self.logger.info(f"Level up! Now level {new_level}")

        # Persist
        self._persist_data()

        return {
            "xp_awarded": xp_amount,
            "total_xp": self.total_xp,
            "old_level": old_level,
            "new_level": self.current_level,
            "level_up": level_up,
            "xp_to_next_level": self.xp_to_next_level(),
        }

    def calculate_level(self, total_xp: int) -> int:
        """Calculate level from total XP"""
        level = 1
        xp_needed = self.base_xp

        while total_xp >= xp_needed:
            level += 1
            xp_needed += int(self.base_xp * (self.xp_multiplier ** (level - 1)))

        return level

    def xp_for_level(self, level: int) -> int:
        """Calculate total XP needed for a level"""
        total_xp = 0
        for lvl in range(1, level):
            total_xp += int(self.base_xp * (self.xp_multiplier ** (lvl - 1)))
        return total_xp

    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level"""
        current_level_xp = self.xp_for_level(self.current_level)
        next_level_xp = self.xp_for_level(self.current_level + 1)
        return next_level_xp - self.total_xp

    def get_progress_to_next_level(self) -> float:
        """Get progress percentage to next level"""
        current_level_xp = self.xp_for_level(self.current_level)
        next_level_xp = self.xp_for_level(self.current_level + 1)
        level_xp_range = next_level_xp - current_level_xp

        if level_xp_range == 0:
            return 100.0

        progress = (self.total_xp - current_level_xp) / level_xp_range * 100
        return max(0.0, min(100.0, progress))

    def get_stats(self) -> Dict[str, Any]:
        """Get XP statistics"""
        return {
            "total_xp": self.total_xp,
            "current_level": self.current_level,
            "xp_to_next_level": self.xp_to_next_level(),
            "progress_percent": self.get_progress_to_next_level(),
            "total_events": len(self.xp_history),
            "xp_by_type": self._get_xp_by_type(),
        }

    def get_recent_events(self, limit: int = 10) -> List[XPEvent]:
        """Get recent XP events"""
        return self.xp_history[-limit:]

    def _get_xp_by_type(self) -> Dict[str, int]:
        """Get XP earned by event type"""
        xp_by_type = {}
        for event in self.xp_history:
            xp_by_type[event.event_type] = xp_by_type.get(event.event_type, 0) + event.amount
        return xp_by_type

    def _persist_data(self):
        """Save XP data to disk"""
        try:
            data = {
                "total_xp": self.total_xp,
                "current_level": self.current_level,
                "xp_history": [event.to_dict() for event in self.xp_history],
            }

            with open(self.xp_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist XP data: {e}")

    def _load_data(self):
        """Load XP data from disk"""
        if not self.xp_file.exists():
            return

        try:
            with open(self.xp_file, "r") as f:
                data = json.load(f)

            self.total_xp = data.get("total_xp", 0)
            self.current_level = data.get("current_level", 1)

            self.xp_history = [
                XPEvent.from_dict(event_data) for event_data in data.get("xp_history", [])
            ]

            self.logger.info(f"Loaded XP data: Level {self.current_level}, {self.total_xp} XP")

        except Exception as e:
            self.logger.error(f"Failed to load XP data: {e}")


# Global instance
_xp_system: Optional[XPSystem] = None


def get_xp_system() -> XPSystem:
    """Get global XP system"""
    global _xp_system
    if _xp_system is None:
        _xp_system = XPSystem()
    return _xp_system
