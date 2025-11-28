"""
Leaderboard System
Competitive rankings and social features
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class LeaderboardEntry:
    """Represents a leaderboard entry"""

    def __init__(
        self,
        user_id: str,
        username: str,
        score: int,
        rank: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.user_id = user_id
        self.username = username
        self.score = score
        self.rank = rank
        self.metadata = metadata or {}
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "score": self.score,
            "rank": self.rank,
            "metadata": self.metadata,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeaderboardEntry":
        """Create from dictionary"""
        entry = cls(
            user_id=data["user_id"],
            username=data["username"],
            score=data["score"],
            rank=data.get("rank", 0),
            metadata=data.get("metadata", {}),
        )
        entry.updated_at = datetime.fromisoformat(data["updated_at"])
        return entry


class Leaderboard:
    """Manages a leaderboard"""

    def __init__(
        self,
        leaderboard_id: str,
        name: str,
        description: str,
        score_type: str,  # 'xp', 'tasks_completed', 'streak_days', etc.
        period: str = "all_time",  # 'all_time', 'monthly', 'weekly', 'daily'
    ):
        self.leaderboard_id = leaderboard_id
        self.name = name
        self.description = description
        self.score_type = score_type
        self.period = period
        self.entries: Dict[str, LeaderboardEntry] = {}

    def update_score(
        self,
        user_id: str,
        username: str,
        score: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update user's score"""
        if user_id in self.entries:
            entry = self.entries[user_id]
            entry.score = score
            entry.updated_at = datetime.now()
            if metadata:
                entry.metadata.update(metadata)
        else:
            self.entries[user_id] = LeaderboardEntry(user_id, username, score, metadata=metadata)

        # Recalculate ranks
        self._calculate_ranks()

    def get_top(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top N entries"""
        sorted_entries = sorted(self.entries.values(), key=lambda e: e.score, reverse=True)
        return sorted_entries[:limit]

    def get_rank(self, user_id: str) -> Optional[int]:
        """Get user's rank"""
        if user_id not in self.entries:
            return None
        return self.entries[user_id].rank

    def get_entry(self, user_id: str) -> Optional[LeaderboardEntry]:
        """Get user's entry"""
        return self.entries.get(user_id)

    def _calculate_ranks(self):
        """Calculate ranks for all entries"""
        sorted_entries = sorted(self.entries.values(), key=lambda e: e.score, reverse=True)

        for i, entry in enumerate(sorted_entries, 1):
            entry.rank = i

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "leaderboard_id": self.leaderboard_id,
            "name": self.name,
            "description": self.description,
            "score_type": self.score_type,
            "period": self.period,
            "entries": {user_id: entry.to_dict() for user_id, entry in self.entries.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Leaderboard":
        """Create from dictionary"""
        leaderboard = cls(
            leaderboard_id=data["leaderboard_id"],
            name=data["name"],
            description=data["description"],
            score_type=data["score_type"],
            period=data.get("period", "all_time"),
        )

        for user_id, entry_data in data.get("entries", {}).items():
            leaderboard.entries[user_id] = LeaderboardEntry.from_dict(entry_data)

        return leaderboard


class LeaderboardSystem:
    """Manages multiple leaderboards"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("gamification.leaderboard")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "gamification"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.leaderboards_file = self.storage_path / "leaderboards.json"

        # Leaderboards
        self.leaderboards: Dict[str, Leaderboard] = {}

        # Initialize default leaderboards
        self._initialize_leaderboards()

        # Load data
        self._load_data()

    def _initialize_leaderboards(self):
        """Initialize default leaderboards"""
        default_leaderboards = [
            Leaderboard(
                "xp_all_time",
                "Total XP",
                "All-time XP leaderboard",
                "xp",
                "all_time",
            ),
            Leaderboard(
                "tasks_all_time",
                "Task Champion",
                "Most tasks completed",
                "tasks_completed",
                "all_time",
            ),
            Leaderboard(
                "streak_longest",
                "Streak Master",
                "Longest active streak",
                "streak_days",
                "all_time",
            ),
            Leaderboard(
                "xp_monthly",
                "Monthly XP",
                "XP earned this month",
                "xp",
                "monthly",
            ),
            Leaderboard(
                "productivity_weekly",
                "Weekly Productivity",
                "Most productive this week",
                "productivity_score",
                "weekly",
            ),
        ]

        for leaderboard in default_leaderboards:
            self.leaderboards[leaderboard.leaderboard_id] = leaderboard

    def update_score(
        self,
        leaderboard_id: str,
        user_id: str,
        username: str,
        score: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update user's score on a leaderboard"""
        if leaderboard_id not in self.leaderboards:
            self.logger.warning(f"Unknown leaderboard: {leaderboard_id}")
            return

        leaderboard = self.leaderboards[leaderboard_id]
        leaderboard.update_score(user_id, username, score, metadata)

        self._persist_data()

    def get_leaderboard(self, leaderboard_id: str) -> Optional[Leaderboard]:
        """Get leaderboard by ID"""
        return self.leaderboards.get(leaderboard_id)

    def get_top(self, leaderboard_id: str, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top N from leaderboard"""
        if leaderboard_id not in self.leaderboards:
            return []

        return self.leaderboards[leaderboard_id].get_top(limit)

    def get_user_rank(self, leaderboard_id: str, user_id: str) -> Optional[int]:
        """Get user's rank on leaderboard"""
        if leaderboard_id not in self.leaderboards:
            return None

        return self.leaderboards[leaderboard_id].get_rank(user_id)

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's stats across all leaderboards"""
        stats = {}

        for lb_id, leaderboard in self.leaderboards.items():
            entry = leaderboard.get_entry(user_id)
            if entry:
                stats[lb_id] = {
                    "rank": entry.rank,
                    "score": entry.score,
                    "total_entries": len(leaderboard.entries),
                }

        return stats

    def _persist_data(self):
        """Save leaderboard data"""
        try:
            data = {
                "leaderboards": {
                    lb_id: leaderboard.to_dict() for lb_id, leaderboard in self.leaderboards.items()
                }
            }

            with open(self.leaderboards_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist leaderboards: {e}")

    def _load_data(self):
        """Load leaderboard data"""
        if not self.leaderboards_file.exists():
            return

        try:
            with open(self.leaderboards_file, "r") as f:
                data = json.load(f)

            for lb_id, lb_data in data.get("leaderboards", {}).items():
                self.leaderboards[lb_id] = Leaderboard.from_dict(lb_data)

            self.logger.info(f"Loaded {len(self.leaderboards)} leaderboards")

        except Exception as e:
            self.logger.error(f"Failed to load leaderboards: {e}")


# Global instance
_leaderboard_system: Optional[LeaderboardSystem] = None


def get_leaderboard_system() -> LeaderboardSystem:
    """Get global leaderboard system"""
    global _leaderboard_system
    if _leaderboard_system is None:
        _leaderboard_system = LeaderboardSystem()
    return _leaderboard_system
