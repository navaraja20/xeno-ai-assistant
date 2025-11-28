"""
Gamification Module
XP, achievements, streaks, and leaderboards
"""

from src.gamification.xp_system import XPSystem, XPEvent, get_xp_system
from src.gamification.achievements import Achievement, AchievementSystem, get_achievement_system
from src.gamification.streaks import Streak, StreakSystem, get_streak_system
from src.gamification.leaderboards import (
    LeaderboardEntry,
    Leaderboard,
    LeaderboardSystem,
    get_leaderboard_system,
)

__all__ = [
    # XP System
    "XPSystem",
    "XPEvent",
    "get_xp_system",
    # Achievements
    "Achievement",
    "AchievementSystem",
    "get_achievement_system",
    # Streaks
    "Streak",
    "StreakSystem",
    "get_streak_system",
    # Leaderboards
    "LeaderboardEntry",
    "Leaderboard",
    "LeaderboardSystem",
    "get_leaderboard_system",
]
