"""
Advanced Analytics Engine
Tracks and analyzes user activity, productivity, and patterns
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import setup_logger


class ActivityType(Enum):
    """Types of tracked activities"""

    EMAIL_READ = "email_read"
    EMAIL_SENT = "email_sent"
    EMAIL_REPLIED = "email_replied"
    CALENDAR_EVENT = "calendar_event"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    GITHUB_COMMIT = "github_commit"
    GITHUB_PR = "github_pr"
    GITHUB_REVIEW = "github_review"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_MESSAGE = "linkedin_message"
    JOB_APPLICATION = "job_application"
    VOICE_COMMAND = "voice_command"
    AI_QUERY = "ai_query"
    FOCUS_SESSION = "focus_session"
    MEETING = "meeting"
    BREAK = "break"
    CUSTOM = "custom"


class ActivityEvent:
    """Individual activity event"""

    def __init__(
        self,
        activity_type: ActivityType,
        timestamp: datetime = None,
        duration_seconds: float = 0,
        metadata: Dict[str, Any] = None,
        productivity_score: float = 0,
    ):
        self.activity_type = activity_type
        self.timestamp = timestamp or datetime.now()
        self.duration_seconds = duration_seconds
        self.metadata = metadata or {}
        self.productivity_score = productivity_score  # 0-1 scale

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "activity_type": self.activity_type.value,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "metadata": self.metadata,
            "productivity_score": self.productivity_score,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ActivityEvent":
        """Create from dictionary"""
        return ActivityEvent(
            activity_type=ActivityType(data["activity_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            duration_seconds=data.get("duration_seconds", 0),
            metadata=data.get("metadata", {}),
            productivity_score=data.get("productivity_score", 0),
        )


class AnalyticsEngine:
    """Main analytics engine for tracking and analysis"""

    def __init__(self, data_dir: str = "data/analytics"):
        self.logger = setup_logger("analytics.engine")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache (last 7 days)
        self.events: List[ActivityEvent] = []

        # Daily aggregations
        self.daily_stats: Dict[str, Dict[str, Any]] = {}

        # Load recent data
        self._load_recent_data()

    def track_activity(
        self,
        activity_type: ActivityType,
        duration_seconds: float = 0,
        metadata: Dict[str, Any] = None,
        productivity_score: float = None,
    ):
        """Track an activity event"""

        # Auto-calculate productivity score if not provided
        if productivity_score is None:
            productivity_score = self._calculate_productivity_score(
                activity_type, metadata
            )

        event = ActivityEvent(
            activity_type=activity_type,
            duration_seconds=duration_seconds,
            metadata=metadata or {},
            productivity_score=productivity_score,
        )

        self.events.append(event)

        # Save to daily file
        self._save_event(event)

        # Update daily aggregations
        self._update_daily_stats(event)

        self.logger.debug(
            f"Tracked activity: {activity_type.value} "
            f"(duration: {duration_seconds}s, score: {productivity_score:.2f})"
        )

    def get_events(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        activity_types: List[ActivityType] = None,
    ) -> List[ActivityEvent]:
        """Get filtered activity events"""

        events = self.events

        # Filter by date range
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]

        # Filter by activity type
        if activity_types:
            events = [e for e in events if e.activity_type in activity_types]

        return events

    def get_daily_summary(self, date: datetime = None) -> Dict[str, Any]:
        """Get daily summary statistics"""

        if date is None:
            date = datetime.now()

        date_key = date.strftime("%Y-%m-%d")

        if date_key in self.daily_stats:
            return self.daily_stats[date_key]

        # Calculate from events
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        day_events = self.get_events(day_start, day_end)

        return self._calculate_daily_summary(day_events, date_key)

    def get_weekly_summary(self, week_start: datetime = None) -> Dict[str, Any]:
        """Get weekly summary statistics"""

        if week_start is None:
            # Start of current week (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())

        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)

        week_events = self.get_events(week_start, week_end)

        return self._calculate_weekly_summary(week_events, week_start)

    def get_monthly_summary(self, month: datetime = None) -> Dict[str, Any]:
        """Get monthly summary statistics"""

        if month is None:
            month = datetime.now()

        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Calculate month end
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        month_events = self.get_events(month_start, month_end)

        return self._calculate_monthly_summary(month_events, month_start)

    def get_productivity_trends(
        self, days: int = 30
    ) -> List[Tuple[datetime, float]]:
        """Get productivity trend over time"""

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trends = []

        current_date = start_date
        while current_date <= end_date:
            summary = self.get_daily_summary(current_date)
            score = summary.get("productivity_score", 0)
            trends.append((current_date, score))
            current_date += timedelta(days=1)

        return trends

    def get_activity_breakdown(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get activity breakdown by type"""

        events = self.get_events(start_date, end_date)

        breakdown = defaultdict(lambda: {"count": 0, "total_duration": 0, "total_score": 0})

        for event in events:
            activity = event.activity_type.value
            breakdown[activity]["count"] += 1
            breakdown[activity]["total_duration"] += event.duration_seconds
            breakdown[activity]["total_score"] += event.productivity_score

        # Calculate averages
        for activity, data in breakdown.items():
            if data["count"] > 0:
                data["avg_duration"] = data["total_duration"] / data["count"]
                data["avg_score"] = data["total_score"] / data["count"]

        return dict(breakdown)

    def get_time_distribution(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[int, float]:
        """Get time distribution by hour of day"""

        events = self.get_events(start_date, end_date)

        distribution = defaultdict(float)

        for event in events:
            hour = event.timestamp.hour
            distribution[hour] += event.duration_seconds / 60  # Convert to minutes

        return dict(distribution)

    def get_peak_productivity_hours(self) -> List[Tuple[int, float]]:
        """Get peak productivity hours"""

        events = self.events

        hourly_scores = defaultdict(lambda: {"total_score": 0, "count": 0})

        for event in events:
            hour = event.timestamp.hour
            hourly_scores[hour]["total_score"] += event.productivity_score
            hourly_scores[hour]["count"] += 1

        # Calculate average scores per hour
        hourly_avg = []
        for hour, data in hourly_scores.items():
            if data["count"] > 0:
                avg_score = data["total_score"] / data["count"]
                hourly_avg.append((hour, avg_score))

        # Sort by score
        hourly_avg.sort(key=lambda x: x[1], reverse=True)

        return hourly_avg

    def get_completion_rates(self) -> Dict[str, float]:
        """Get task/goal completion rates"""

        # Tasks
        tasks_created = len(
            self.get_events(activity_types=[ActivityType.TASK_CREATED])
        )
        tasks_completed = len(
            self.get_events(activity_types=[ActivityType.TASK_COMPLETED])
        )

        # Emails
        emails_received = len(self.get_events(activity_types=[ActivityType.EMAIL_READ]))
        emails_replied = len(
            self.get_events(activity_types=[ActivityType.EMAIL_REPLIED])
        )

        # Focus sessions
        focus_events = self.get_events(activity_types=[ActivityType.FOCUS_SESSION])
        focus_completed = sum(
            1 for e in focus_events if e.metadata.get("completed", False)
        )

        return {
            "task_completion_rate": (
                tasks_completed / tasks_created if tasks_created > 0 else 0
            ),
            "email_response_rate": (
                emails_replied / emails_received if emails_received > 0 else 0
            ),
            "focus_completion_rate": (
                focus_completed / len(focus_events) if len(focus_events) > 0 else 0
            ),
        }

    def _calculate_productivity_score(
        self, activity_type: ActivityType, metadata: Dict[str, Any]
    ) -> float:
        """Calculate productivity score for activity"""

        # Base scores by activity type (0-1 scale)
        base_scores = {
            ActivityType.TASK_COMPLETED: 0.9,
            ActivityType.EMAIL_SENT: 0.7,
            ActivityType.EMAIL_REPLIED: 0.8,
            ActivityType.GITHUB_COMMIT: 0.9,
            ActivityType.GITHUB_PR: 0.95,
            ActivityType.GITHUB_REVIEW: 0.85,
            ActivityType.FOCUS_SESSION: 0.95,
            ActivityType.MEETING: 0.6,
            ActivityType.JOB_APPLICATION: 0.9,
            ActivityType.TASK_CREATED: 0.5,
            ActivityType.EMAIL_READ: 0.4,
            ActivityType.VOICE_COMMAND: 0.3,
            ActivityType.AI_QUERY: 0.5,
            ActivityType.BREAK: 0.2,
        }

        score = base_scores.get(activity_type, 0.5)

        # Adjust based on metadata
        if metadata:
            # Higher score for important tasks
            if metadata.get("priority") == "high":
                score += 0.1
            elif metadata.get("priority") == "critical":
                score += 0.15

            # Lower score for low priority
            if metadata.get("priority") == "low":
                score -= 0.1

            # Bonus for completed focus sessions
            if activity_type == ActivityType.FOCUS_SESSION:
                if metadata.get("completed"):
                    score += 0.05

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    def _calculate_daily_summary(
        self, events: List[ActivityEvent], date_key: str
    ) -> Dict[str, Any]:
        """Calculate daily summary from events"""

        if not events:
            return {
                "date": date_key,
                "total_events": 0,
                "total_duration_minutes": 0,
                "productivity_score": 0,
                "breakdown": {},
            }

        total_duration = sum(e.duration_seconds for e in events) / 60  # Minutes
        total_score = sum(e.productivity_score for e in events)
        avg_score = total_score / len(events) if events else 0

        # Activity breakdown
        breakdown = defaultdict(int)
        for event in events:
            breakdown[event.activity_type.value] += 1

        summary = {
            "date": date_key,
            "total_events": len(events),
            "total_duration_minutes": total_duration,
            "productivity_score": avg_score,
            "breakdown": dict(breakdown),
        }

        # Cache it
        self.daily_stats[date_key] = summary

        return summary

    def _calculate_weekly_summary(
        self, events: List[ActivityEvent], week_start: datetime
    ) -> Dict[str, Any]:
        """Calculate weekly summary"""

        # Daily summaries
        daily_summaries = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            daily_summaries.append(self.get_daily_summary(day))

        total_events = sum(d["total_events"] for d in daily_summaries)
        total_duration = sum(d["total_duration_minutes"] for d in daily_summaries)
        avg_score = (
            sum(d["productivity_score"] for d in daily_summaries) / 7
            if daily_summaries
            else 0
        )

        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "total_events": total_events,
            "total_duration_minutes": total_duration,
            "productivity_score": avg_score,
            "daily_summaries": daily_summaries,
        }

    def _calculate_monthly_summary(
        self, events: List[ActivityEvent], month_start: datetime
    ) -> Dict[str, Any]:
        """Calculate monthly summary"""

        total_duration = sum(e.duration_seconds for e in events) / 60
        total_score = sum(e.productivity_score for e in events)
        avg_score = total_score / len(events) if events else 0

        # Weekly breakdown
        weekly_summaries = []
        current_week = month_start
        while current_week.month == month_start.month:
            weekly_summaries.append(self.get_weekly_summary(current_week))
            current_week += timedelta(days=7)

        return {
            "month": month_start.strftime("%Y-%m"),
            "total_events": len(events),
            "total_duration_minutes": total_duration,
            "productivity_score": avg_score,
            "weekly_summaries": weekly_summaries,
        }

    def _update_daily_stats(self, event: ActivityEvent):
        """Update daily aggregations"""
        date_key = event.timestamp.strftime("%Y-%m-%d")

        if date_key not in self.daily_stats:
            self.daily_stats[date_key] = {
                "date": date_key,
                "total_events": 0,
                "total_duration_minutes": 0,
                "productivity_score": 0,
                "breakdown": {},
            }

        stats = self.daily_stats[date_key]
        stats["total_events"] += 1
        stats["total_duration_minutes"] += event.duration_seconds / 60

        # Update productivity score (running average)
        old_avg = stats["productivity_score"]
        new_count = stats["total_events"]
        stats["productivity_score"] = (
            old_avg * (new_count - 1) + event.productivity_score
        ) / new_count

        # Update breakdown
        activity = event.activity_type.value
        stats["breakdown"][activity] = stats["breakdown"].get(activity, 0) + 1

    def _save_event(self, event: ActivityEvent):
        """Save event to daily file"""
        try:
            date_key = event.timestamp.strftime("%Y-%m-%d")
            file_path = self.data_dir / f"{date_key}.json"

            # Load existing events
            events_data = []
            if file_path.exists():
                with open(file_path, "r") as f:
                    events_data = json.load(f)

            # Append new event
            events_data.append(event.to_dict())

            # Save
            with open(file_path, "w") as f:
                json.dump(events_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving event: {e}")

    def _load_recent_data(self, days: int = 7):
        """Load recent data into memory"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                file_path = self.data_dir / f"{date_key}.json"

                if file_path.exists():
                    with open(file_path, "r") as f:
                        events_data = json.load(f)

                    for event_data in events_data:
                        self.events.append(ActivityEvent.from_dict(event_data))

                current_date += timedelta(days=1)

            self.logger.info(f"Loaded {len(self.events)} events from last {days} days")

        except Exception as e:
            self.logger.error(f"Error loading recent data: {e}")


# Global instance
_analytics_engine: Optional[AnalyticsEngine] = None


def get_analytics_engine() -> AnalyticsEngine:
    """Get global analytics engine"""
    global _analytics_engine
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    return _analytics_engine


# Convenience function
def track_activity(
    activity_type: ActivityType, duration_seconds: float = 0, **metadata
):
    """Quick function to track activity"""
    return get_analytics_engine().track_activity(
        activity_type, duration_seconds, metadata
    )
