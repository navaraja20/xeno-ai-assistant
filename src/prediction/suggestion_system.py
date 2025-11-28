"""
Suggestion System
Provides proactive task suggestions based on patterns and context
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from src.core.logger import setup_logger
from src.prediction.pattern_recognition import get_pattern_engine
from src.prediction.task_predictor import get_task_predictor


class TaskSuggestion:
    """Represents a task suggestion"""

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        reason: str = "",
        confidence: float = 0.5,
        tags: List[str] = None,
        estimated_duration: Optional[float] = None,
        suggested_time: Optional[datetime] = None,
        source: str = "pattern",
    ):
        self.title = title
        self.priority = priority
        self.reason = reason
        self.confidence = confidence
        self.tags = tags or []
        self.estimated_duration = estimated_duration
        self.suggested_time = suggested_time
        self.source = source  # pattern, predictor, context, user_feedback

        # Feedback tracking
        self.created_at = datetime.now()
        self.accepted = None  # True/False/None (pending)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "priority": self.priority,
            "reason": self.reason,
            "confidence": self.confidence,
            "tags": self.tags,
            "estimated_duration": self.estimated_duration,
            "suggested_time": self.suggested_time.isoformat() if self.suggested_time else None,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "accepted": self.accepted,
        }


class SuggestionSystem:
    """Generates and manages task suggestions"""

    def __init__(self):
        self.logger = setup_logger("prediction.suggestions")

        # Dependencies
        self.pattern_engine = get_pattern_engine()
        self.task_predictor = get_task_predictor()

        # Active suggestions
        self.active_suggestions: List[TaskSuggestion] = []

        # Suggestion history
        self.suggestion_history: List[TaskSuggestion] = []

        # User preferences (learned from feedback)
        self.user_preferences = {
            "preferred_times": [],  # List of (hour, confidence) tuples
            "preferred_tags": {},  # tag -> acceptance_rate
            "preferred_priorities": {},  # priority -> acceptance_rate
            "ignored_titles": set(),  # Titles user consistently rejects
        }

        # Suggestion settings
        self.max_suggestions = 10
        self.min_confidence = 0.5
        self.suggestion_cooldown_hours = 4  # Don't re-suggest same task within hours

    def generate_suggestions(self, context: Dict[str, Any] = None) -> List[TaskSuggestion]:
        """Generate task suggestions"""
        suggestions = []

        if context is None:
            context = {}

        # Get pattern-based suggestions
        pattern_suggestions = self._get_pattern_suggestions(context)
        suggestions.extend(pattern_suggestions)

        # Get predictor-based suggestions
        predictor_suggestions = self._get_predictor_suggestions(context)
        suggestions.extend(predictor_suggestions)

        # Get context-based suggestions
        context_suggestions = self._get_context_suggestions(context)
        suggestions.extend(context_suggestions)

        # Filter and rank suggestions
        filtered = self._filter_suggestions(suggestions)
        ranked = self._rank_suggestions(filtered)

        # Store as active suggestions
        self.active_suggestions = ranked[: self.max_suggestions]

        self.logger.info(f"Generated {len(self.active_suggestions)} suggestions")
        return self.active_suggestions

    def _get_pattern_suggestions(self, context: Dict[str, Any]) -> List[TaskSuggestion]:
        """Get suggestions from pattern recognition"""
        suggestions = []

        # Get pattern predictions
        predictions = self.pattern_engine.predict_next_tasks()

        for pred in predictions:
            # Skip if recently suggested
            if self._was_recently_suggested(pred.get("title", "")):
                continue

            # Skip if user has ignored this title
            if pred.get("title", "") in self.user_preferences["ignored_titles"]:
                continue

            suggestion = TaskSuggestion(
                title=pred.get("title", ""),
                priority="medium",  # Default, can be inferred from attributes
                reason=pred.get("description", "Based on recurring pattern"),
                confidence=pred.get("probability", 0.5),
                tags=[],
                estimated_duration=None,
                suggested_time=datetime.fromisoformat(pred["expected_time"])
                if "expected_time" in pred
                else None,
                source="pattern",
            )

            suggestions.append(suggestion)

        return suggestions

    def _get_predictor_suggestions(self, context: Dict[str, Any]) -> List[TaskSuggestion]:
        """Get suggestions from task predictor"""
        suggestions = []

        # Get ML predictions
        predictions = self.task_predictor.predict_tasks(context, max_predictions=15)

        for pred in predictions:
            # Skip if recently suggested
            if self._was_recently_suggested(pred.get("title", "")):
                continue

            # Skip if user has ignored
            if pred.get("title", "") in self.user_preferences["ignored_titles"]:
                continue

            suggestion = TaskSuggestion(
                title=pred.get("title", ""),
                priority=pred.get("priority", "medium"),
                reason=pred.get("reason", "Based on historical patterns"),
                confidence=pred.get("probability", 0.5),
                tags=pred.get("tags", []),
                estimated_duration=pred.get("estimated_duration"),
                suggested_time=None,  # Predictor doesn't provide specific times
                source="predictor",
            )

            suggestions.append(suggestion)

        return suggestions

    def _get_context_suggestions(self, context: Dict[str, Any]) -> List[TaskSuggestion]:
        """Get suggestions based on current context"""
        suggestions = []
        now = datetime.now()

        # Time-based suggestions
        current_hour = now.hour

        # Morning suggestions (6-9 AM)
        if 6 <= current_hour < 9:
            suggestions.append(
                TaskSuggestion(
                    title="Review today's priorities",
                    priority="medium",
                    reason="Morning planning helps set daily focus",
                    confidence=0.7,
                    tags=["planning", "morning"],
                    estimated_duration=15,
                    suggested_time=now,
                    source="context",
                )
            )

        # End of day suggestions (4-6 PM)
        elif 16 <= current_hour < 18:
            suggestions.append(
                TaskSuggestion(
                    title="Review completed tasks",
                    priority="low",
                    reason="End-of-day review helps track progress",
                    confidence=0.6,
                    tags=["review", "evening"],
                    estimated_duration=10,
                    suggested_time=now,
                    source="context",
                )
            )

        # Day-specific suggestions
        if now.weekday() == 0:  # Monday
            suggestions.append(
                TaskSuggestion(
                    title="Plan weekly goals",
                    priority="medium",
                    reason="Start of week planning",
                    confidence=0.65,
                    tags=["planning", "weekly"],
                    estimated_duration=20,
                    suggested_time=now,
                    source="context",
                )
            )

        elif now.weekday() == 4:  # Friday
            suggestions.append(
                TaskSuggestion(
                    title="Prepare weekly summary",
                    priority="low",
                    reason="End of week wrap-up",
                    confidence=0.6,
                    tags=["review", "weekly"],
                    estimated_duration=15,
                    suggested_time=now,
                    source="context",
                )
            )

        # Context-based (if provided)
        if context.get("recent_completed_count", 0) >= 5:
            suggestions.append(
                TaskSuggestion(
                    title="Take a break",
                    priority="low",
                    reason="You've completed 5+ tasks, time to rest",
                    confidence=0.8,
                    tags=["wellbeing"],
                    estimated_duration=15,
                    suggested_time=now,
                    source="context",
                )
            )

        if context.get("overdue_count", 0) > 0:
            suggestions.append(
                TaskSuggestion(
                    title="Review overdue tasks",
                    priority="high",
                    reason=f"You have {context['overdue_count']} overdue tasks",
                    confidence=0.9,
                    tags=["urgent", "review"],
                    estimated_duration=10,
                    suggested_time=now,
                    source="context",
                )
            )

        return suggestions

    def _was_recently_suggested(self, title: str) -> bool:
        """Check if task was suggested recently"""
        cutoff = datetime.now() - timedelta(hours=self.suggestion_cooldown_hours)

        for suggestion in self.suggestion_history:
            if (
                suggestion.title == title
                and suggestion.created_at > cutoff
                and suggestion.accepted is not True
            ):
                return True

        return False

    def _filter_suggestions(self, suggestions: List[TaskSuggestion]) -> List[TaskSuggestion]:
        """Filter out low-quality suggestions"""
        filtered = []

        for suggestion in suggestions:
            # Confidence threshold
            if suggestion.confidence < self.min_confidence:
                continue

            # No duplicates
            if any(s.title == suggestion.title for s in filtered):
                continue

            # Apply user preferences
            adjusted_confidence = self._apply_user_preferences(suggestion)
            suggestion.confidence = adjusted_confidence

            if adjusted_confidence >= self.min_confidence:
                filtered.append(suggestion)

        return filtered

    def _apply_user_preferences(self, suggestion: TaskSuggestion) -> float:
        """Adjust confidence based on user preferences"""
        confidence = suggestion.confidence

        # Check preferred tags
        if suggestion.tags:
            tag_scores = [
                self.user_preferences["preferred_tags"].get(tag, 0.5) for tag in suggestion.tags
            ]
            if tag_scores:
                avg_tag_score = sum(tag_scores) / len(tag_scores)
                confidence = confidence * 0.7 + avg_tag_score * 0.3

        # Check preferred priority
        priority_score = self.user_preferences["preferred_priorities"].get(suggestion.priority, 0.5)
        confidence = confidence * 0.8 + priority_score * 0.2

        return min(1.0, confidence)

    def _rank_suggestions(self, suggestions: List[TaskSuggestion]) -> List[TaskSuggestion]:
        """Rank suggestions by score"""

        def suggestion_score(s: TaskSuggestion) -> float:
            score = s.confidence * 10

            # Boost by priority
            priority_boost = {"high": 3, "medium": 2, "low": 1}
            score += priority_boost.get(s.priority, 2)

            # Boost if has specific time
            if s.suggested_time:
                score += 2

            # Boost recent suggestions
            age_hours = (datetime.now() - s.created_at).total_seconds() / 3600
            if age_hours < 1:
                score += 1

            return score

        return sorted(suggestions, key=suggestion_score, reverse=True)

    def accept_suggestion(self, title: str) -> bool:
        """User accepted a suggestion"""
        for suggestion in self.active_suggestions:
            if suggestion.title == title:
                suggestion.accepted = True
                self.suggestion_history.append(suggestion)
                self._update_preferences(suggestion, accepted=True)

                self.logger.info(f"Suggestion accepted: {title}")
                return True

        return False

    def reject_suggestion(self, title: str, permanent: bool = False) -> bool:
        """User rejected a suggestion"""
        for suggestion in self.active_suggestions:
            if suggestion.title == title:
                suggestion.accepted = False
                self.suggestion_history.append(suggestion)
                self._update_preferences(suggestion, accepted=False)

                if permanent:
                    self.user_preferences["ignored_titles"].add(title)
                    self.logger.info(f"Permanently ignored: {title}")

                self.logger.info(f"Suggestion rejected: {title}")
                return True

        return False

    def _update_preferences(self, suggestion: TaskSuggestion, accepted: bool):
        """Update user preferences based on feedback"""
        # Update tag preferences
        for tag in suggestion.tags:
            if tag not in self.user_preferences["preferred_tags"]:
                self.user_preferences["preferred_tags"][tag] = 0.5

            # Adjust preference
            adjustment = 0.1 if accepted else -0.05
            current = self.user_preferences["preferred_tags"][tag]
            self.user_preferences["preferred_tags"][tag] = max(0, min(1, current + adjustment))

        # Update priority preferences
        priority = suggestion.priority
        if priority not in self.user_preferences["preferred_priorities"]:
            self.user_preferences["preferred_priorities"][priority] = 0.5

        adjustment = 0.1 if accepted else -0.05
        current = self.user_preferences["preferred_priorities"][priority]
        self.user_preferences["preferred_priorities"][priority] = max(
            0, min(1, current + adjustment)
        )

    def get_suggestion_stats(self) -> Dict[str, Any]:
        """Get suggestion statistics"""
        total = len(self.suggestion_history)
        if total == 0:
            return {
                "total_suggestions": 0,
                "acceptance_rate": 0.0,
                "rejection_rate": 0.0,
                "pending_rate": 0.0,
            }

        accepted = sum(1 for s in self.suggestion_history if s.accepted is True)
        rejected = sum(1 for s in self.suggestion_history if s.accepted is False)
        pending = total - accepted - rejected

        return {
            "total_suggestions": total,
            "acceptance_rate": accepted / total,
            "rejection_rate": rejected / total,
            "pending_rate": pending / total,
            "active_suggestions": len(self.active_suggestions),
            "ignored_titles": len(self.user_preferences["ignored_titles"]),
        }


# Global instance
_suggestion_system: Optional[SuggestionSystem] = None


def get_suggestion_system() -> SuggestionSystem:
    """Get global suggestion system"""
    global _suggestion_system
    if _suggestion_system is None:
        _suggestion_system = SuggestionSystem()
    return _suggestion_system
