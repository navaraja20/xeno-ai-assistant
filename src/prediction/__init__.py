"""
Prediction Module
Exports all prediction components
"""

from src.prediction.auto_scheduler import AutoScheduler, ScheduleSlot, get_auto_scheduler
from src.prediction.pattern_recognition import Pattern, PatternRecognitionEngine, get_pattern_engine
from src.prediction.suggestion_system import SuggestionSystem, TaskSuggestion, get_suggestion_system
from src.prediction.task_predictor import TaskPredictor, get_task_predictor

__all__ = [
    # Pattern Recognition
    "Pattern",
    "PatternRecognitionEngine",
    "get_pattern_engine",
    # Task Predictor
    "TaskPredictor",
    "get_task_predictor",
    # Auto Scheduler
    "ScheduleSlot",
    "AutoScheduler",
    "get_auto_scheduler",
    # Suggestion System
    "TaskSuggestion",
    "SuggestionSystem",
    "get_suggestion_system",
]
