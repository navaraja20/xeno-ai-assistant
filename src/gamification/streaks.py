"""
Streak System
Track daily streaks and habits
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class Streak:
    """Represents a tracking streak"""

    def __init__(
        self,
        streak_type: str,
        name: str,
        description: str,
        icon: str = "🔥",
    ):
        self.streak_type = streak_type
        self.name = name
        self.description = description
        self.icon = icon
        self.current_streak = 0
        self.longest_streak = 0
        self.last_activity_date: Optional[datetime] = None
        self.total_days = 0
        self.activity_dates: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "streak_type": self.streak_type,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "total_days": self.total_days,
            "activity_dates": self.activity_dates,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Streak":
        """Create from dictionary"""
        streak = cls(
            streak_type=data["streak_type"],
            name=data["name"],
            description=data["description"],
            icon=data.get("icon", "🔥"),
        )
        streak.current_streak = data.get("current_streak", 0)
        streak.longest_streak = data.get("longest_streak", 0)
        streak.last_activity_date = (
            datetime.fromisoformat(data["last_activity_date"])
            if data.get("last_activity_date")
            else None
        )
        streak.total_days = data.get("total_days", 0)
        streak.activity_dates = data.get("activity_dates", [])
        return streak


class StreakSystem:
    """Manages streaks and daily habits"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("gamification.streaks")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "gamification"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.streaks_file = self.storage_path / "streaks.json"

        # Streaks
        self.streaks: Dict[str, Streak] = {}

        # Initialize default streaks
        self._initialize_streaks()

        # Load data
        self._load_data()

    def _initialize_streaks(self):
        """Initialize default streak trackers"""
        default_streaks = [
            Streak("daily_login", "Daily Login", "Log in to XENO every day", "🔥"),
            Streak("task_completion", "Task Master", "Complete at least one task every day", "✅"),
            Streak("focus_session", "Focus Flow", "Complete a focus session every day", "🎯"),
            Streak("inbox_zero", "Inbox Zero", "Reach inbox zero every day", "📧"),
            Streak("learning", "Continuous Learner", "Learn something new every day", "📚"),
        ]

        for streak in default_streaks:
            self.streaks[streak.streak_type] = streak

    def record_activity(self, streak_type: str) -> Dict[str, Any]:
        """Record activity for a streak"""
        if streak_type not in self.streaks:
            self.logger.warning(f"Unknown streak type: {streak_type}")
            return {"success": False}

        streak = self.streaks[streak_type]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today.strftime("%Y-%m-%d")

        # Check if already recorded today
        if today_str in streak.activity_dates:
            return {
                "success": True,
                "already_recorded": True,
                "current_streak": streak.current_streak,
            }

        # Record activity
        streak.activity_dates.append(today_str)
        streak.total_days += 1

        # Update streak
        if streak.last_activity_date:
            yesterday = today - timedelta(days=1)
            if streak.last_activity_date.date() == yesterday.date():
                # Continuing streak
                streak.current_streak += 1
            else:
                # Streak broken
                streak.current_streak = 1
        else:
            # First activity
            streak.current_streak = 1

        streak.last_activity_date = today

        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        # Persist
        self._persist_data()

        return {
            "success": True,
            "already_recorded": False,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "milestone_reached": self._check_milestones(streak.current_streak),
        }

    def get_streak(self, streak_type: str) -> Optional[Streak]:
        """Get streak by type"""
        return self.streaks.get(streak_type)

    def get_all_streaks(self) -> List[Streak]:
        """Get all streaks"""
        return list(self.streaks.values())

    def get_active_streaks(self) -> List[Streak]:
        """Get all active streaks (>0 days)"""
        return [s for s in self.streaks.values() if s.current_streak > 0]

    def check_streak_status(self):
        """Check and update all streak statuses"""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        for streak in self.streaks.values():
            if not streak.last_activity_date:
                continue

            # Check if streak should be broken
            if streak.last_activity_date.date() < yesterday.date():
                if streak.current_streak > 0:
                    self.logger.info(f"Streak broken: {streak.name} ({streak.current_streak} days)")
                    streak.current_streak = 0

        self._persist_data()

    def get_stats(self) -> Dict[str, Any]:
        """Get streak statistics"""
        return {
            "total_streaks": len(self.streaks),
            "active_streaks": len(self.get_active_streaks()),
            "longest_current": max(
                (s.current_streak for s in self.streaks.values()),
                default=0
            ),
            "longest_ever": max(
                (s.longest_streak for s in self.streaks.values()),
                default=0
            ),
            "total_days": sum(s.total_days for s in self.streaks.values()),
        }

    def _check_milestones(self, streak_count: int) -> Optional[int]:
        """Check if a milestone was reached"""
        milestones = [7, 14, 30, 60, 100, 365]
        if streak_count in milestones:
            return streak_count
        return None

    def _persist_data(self):
        """Save streak data"""
        try:
            data = {
                "streaks": {
                    stype: streak.to_dict()
                    for stype, streak in self.streaks.items()
                }
            }

            with open(self.streaks_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist streaks: {e}")

    def _load_data(self):
        """Load streak data"""
        if not self.streaks_file.exists():
            return

        try:
            with open(self.streaks_file, "r") as f:
                data = json.load(f)

            for stype, streak_data in data.get("streaks", {}).items():
                if stype in self.streaks:
                    self.streaks[stype] = Streak.from_dict(streak_data)

            # Check streak status on load
            self.check_streak_status()

            self.logger.info(f"Loaded {len(self.streaks)} streaks")

        except Exception as e:
            self.logger.error(f"Failed to load streaks: {e}")


# Global instance
_streak_system: Optional[StreakSystem] = None


def get_streak_system() -> StreakSystem:
    """Get global streak system"""
    global _streak_system
    if _streak_system is None:
        _streak_system = StreakSystem()
    return _streak_system
