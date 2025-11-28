"""
Achievements System
Track and unlock achievements
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class Achievement:
    """Represents an achievement"""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        icon: str,
        category: str,
        xp_reward: int = 0,
        secret: bool = False,
        requirement: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.category = category
        self.xp_reward = xp_reward
        self.secret = secret
        self.requirement = requirement or {}
        self.unlocked = False
        self.unlocked_at: Optional[datetime] = None
        self.progress = 0
        self.max_progress = requirement.get("count", 1) if requirement else 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "xp_reward": self.xp_reward,
            "secret": self.secret,
            "requirement": self.requirement,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "progress": self.progress,
            "max_progress": self.max_progress,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Achievement":
        """Create from dictionary"""
        achievement = cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            icon=data["icon"],
            category=data["category"],
            xp_reward=data.get("xp_reward", 0),
            secret=data.get("secret", False),
            requirement=data.get("requirement"),
        )
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlocked_at = (
            datetime.fromisoformat(data["unlocked_at"]) if data.get("unlocked_at") else None
        )
        achievement.progress = data.get("progress", 0)
        achievement.max_progress = data.get("max_progress", 1)
        return achievement


class AchievementSystem:
    """Manages achievements and tracking"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("gamification.achievements")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "gamification"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.achievements_file = self.storage_path / "achievements.json"

        # Achievements
        self.achievements: Dict[str, Achievement] = {}

        # Initialize default achievements
        self._initialize_achievements()

        # Load progress
        self._load_progress()

    def _initialize_achievements(self):
        """Initialize default achievements"""
        default_achievements = [
            # Getting Started
            Achievement(
                "first_task",
                "First Steps",
                "Complete your first task",
                "🎯",
                "Getting Started",
                xp_reward=50,
                requirement={"event": "task_complete", "count": 1},
            ),
            Achievement(
                "welcome_aboard",
                "Welcome Aboard",
                "Use XENO for the first time",
                "👋",
                "Getting Started",
                xp_reward=25,
                requirement={"event": "first_login", "count": 1},
            ),
            # Productivity
            Achievement(
                "task_master",
                "Task Master",
                "Complete 100 tasks",
                "🏆",
                "Productivity",
                xp_reward=500,
                requirement={"event": "task_complete", "count": 100},
            ),
            Achievement(
                "early_bird",
                "Early Bird",
                "Complete 10 tasks ahead of schedule",
                "🐦",
                "Productivity",
                xp_reward=250,
                requirement={"event": "task_complete_early", "count": 10},
            ),
            Achievement(
                "speed_demon",
                "Speed Demon",
                "Complete 10 tasks in one day",
                "⚡",
                "Productivity",
                xp_reward=300,
                requirement={"event": "daily_tasks", "count": 10},
            ),
            # Streaks
            Achievement(
                "week_warrior",
                "Week Warrior",
                "Use XENO for 7 consecutive days",
                "📅",
                "Streaks",
                xp_reward=200,
                requirement={"event": "consecutive_days", "count": 7},
            ),
            Achievement(
                "month_champion",
                "Month Champion",
                "Use XENO for 30 consecutive days",
                "🗓️",
                "Streaks",
                xp_reward=1000,
                requirement={"event": "consecutive_days", "count": 30},
            ),
            # Focus
            Achievement(
                "zen_master",
                "Zen Master",
                "Complete 50 focus sessions",
                "🧘",
                "Focus",
                xp_reward=400,
                requirement={"event": "focus_session", "count": 50},
            ),
            Achievement(
                "deep_work",
                "Deep Work",
                "Complete a 4-hour focus session",
                "🎯",
                "Focus",
                xp_reward=500,
                requirement={"event": "focus_hours", "count": 4},
            ),
            # Communication
            Achievement(
                "inbox_hero",
                "Inbox Hero",
                "Process 500 emails",
                "📧",
                "Communication",
                xp_reward=300,
                requirement={"event": "email_processed", "count": 500},
            ),
            Achievement(
                "meeting_maven",
                "Meeting Maven",
                "Complete 50 meetings",
                "💼",
                "Communication",
                xp_reward=350,
                requirement={"event": "meeting_completed", "count": 50},
            ),
            # Automation
            Achievement(
                "workflow_wizard",
                "Workflow Wizard",
                "Create 10 workflows",
                "🔧",
                "Automation",
                xp_reward=600,
                requirement={"event": "workflow_created", "count": 10},
            ),
            Achievement(
                "plugin_pioneer",
                "Plugin Pioneer",
                "Install 5 plugins",
                "🔌",
                "Automation",
                xp_reward=250,
                requirement={"event": "plugin_installed", "count": 5},
            ),
            # Learning
            Achievement(
                "knowledge_seeker",
                "Knowledge Seeker",
                "Complete 10 tutorials",
                "📚",
                "Learning",
                xp_reward=400,
                requirement={"event": "tutorial_complete", "count": 10},
            ),
            Achievement(
                "skill_collector",
                "Skill Collector",
                "Learn 5 new skills",
                "⭐",
                "Learning",
                xp_reward=750,
                requirement={"event": "skill_learned", "count": 5},
            ),
            # Secret Achievements
            Achievement(
                "night_owl",
                "Night Owl",
                "Complete a task after midnight",
                "🦉",
                "Secret",
                xp_reward=100,
                secret=True,
                requirement={"event": "late_night_task", "count": 1},
            ),
            Achievement(
                "easter_egg",
                "Curious Explorer",
                "Find the hidden easter egg",
                "🥚",
                "Secret",
                xp_reward=500,
                secret=True,
                requirement={"event": "easter_egg_found", "count": 1},
            ),
        ]

        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement

    def track_event(
        self, event_type: str, count: int = 1, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Achievement]:
        """Track an event and check for achievement unlocks"""
        unlocked = []

        for achievement in self.achievements.values():
            if achievement.unlocked:
                continue

            # Check if event matches requirement
            req_event = achievement.requirement.get("event")
            if req_event != event_type:
                continue

            # Update progress
            achievement.progress += count

            # Check if unlocked
            if achievement.progress >= achievement.max_progress:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
                unlocked.append(achievement)
                self.logger.info(f"Achievement unlocked: {achievement.name}")

        if unlocked:
            self._persist_progress()

        return unlocked

    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID"""
        return self.achievements.get(achievement_id)

    def get_achievements_by_category(self, category: str) -> List[Achievement]:
        """Get achievements in a category"""
        return [a for a in self.achievements.values() if a.category == category]

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(self, include_secret: bool = False) -> List[Achievement]:
        """Get all locked achievements"""
        locked = [a for a in self.achievements.values() if not a.unlocked]
        if not include_secret:
            locked = [a for a in locked if not a.secret]
        return locked

    def get_progress_stats(self) -> Dict[str, Any]:
        """Get achievement progress statistics"""
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())

        return {
            "total_achievements": total,
            "unlocked": unlocked,
            "locked": total - unlocked,
            "completion_percent": (unlocked / total * 100) if total > 0 else 0,
            "total_xp_earned": sum(a.xp_reward for a in self.get_unlocked_achievements()),
            "categories": self._get_category_stats(),
        }

    def _get_category_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics by category"""
        stats = {}
        for achievement in self.achievements.values():
            category = achievement.category
            if category not in stats:
                stats[category] = {"total": 0, "unlocked": 0}

            stats[category]["total"] += 1
            if achievement.unlocked:
                stats[category]["unlocked"] += 1

        return stats

    def _persist_progress(self):
        """Save achievement progress"""
        try:
            data = {
                "achievements": {
                    aid: achievement.to_dict() for aid, achievement in self.achievements.items()
                }
            }

            with open(self.achievements_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist achievements: {e}")

    def _load_progress(self):
        """Load achievement progress"""
        if not self.achievements_file.exists():
            return

        try:
            with open(self.achievements_file, "r") as f:
                data = json.load(f)

            for aid, achievement_data in data.get("achievements", {}).items():
                if aid in self.achievements:
                    # Update existing achievement
                    achievement = self.achievements[aid]
                    achievement.unlocked = achievement_data.get("unlocked", False)
                    achievement.unlocked_at = (
                        datetime.fromisoformat(achievement_data["unlocked_at"])
                        if achievement_data.get("unlocked_at")
                        else None
                    )
                    achievement.progress = achievement_data.get("progress", 0)

            self.logger.info(f"Loaded achievement progress")

        except Exception as e:
            self.logger.error(f"Failed to load achievements: {e}")


# Global instance
_achievement_system: Optional[AchievementSystem] = None


def get_achievement_system() -> AchievementSystem:
    """Get global achievement system"""
    global _achievement_system
    if _achievement_system is None:
        _achievement_system = AchievementSystem()
    return _achievement_system
