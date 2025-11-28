"""
Productivity Scorer
Advanced productivity metrics and scoring algorithms
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from src.core.logger import setup_logger
from src.modules.analytics_engine import ActivityType, get_analytics_engine


class ProductivityMetrics:
    """Calculate various productivity metrics"""

    def __init__(self):
        self.logger = setup_logger("analytics.scorer")
        self.engine = get_analytics_engine()

    def calculate_productivity_score(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> float:
        """
        Calculate overall productivity score (0-100)
        Combines multiple factors weighted by importance
        """

        if start_date is None:
            start_date = datetime.now() - timedelta(days=1)
        if end_date is None:
            end_date = datetime.now()

        # Get events for period
        events = self.engine.get_events(start_date, end_date)

        if not events:
            return 0.0

        # Component scores
        task_score = self._calculate_task_score(events)
        focus_score = self._calculate_focus_score(events)
        communication_score = self._calculate_communication_score(events)
        consistency_score = self._calculate_consistency_score(events)
        output_score = self._calculate_output_score(events)

        # Weighted combination
        weights = {
            "tasks": 0.30,
            "focus": 0.25,
            "communication": 0.20,
            "consistency": 0.15,
            "output": 0.10,
        }

        final_score = (
            task_score * weights["tasks"]
            + focus_score * weights["focus"]
            + communication_score * weights["communication"]
            + consistency_score * weights["consistency"]
            + output_score * weights["output"]
        )

        return round(final_score, 2)

    def get_detailed_metrics(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> Dict[str, any]:
        """Get detailed productivity metrics breakdown"""

        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()

        events = self.engine.get_events(start_date, end_date)

        metrics = {
            "overall_score": self.calculate_productivity_score(start_date, end_date),
            "task_metrics": self._get_task_metrics(events),
            "focus_metrics": self._get_focus_metrics(events),
            "communication_metrics": self._get_communication_metrics(events),
            "time_metrics": self._get_time_metrics(events),
            "output_metrics": self._get_output_metrics(events),
            "efficiency_metrics": self._get_efficiency_metrics(events),
        }

        return metrics

    def get_productivity_insights(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> List[str]:
        """Get AI-generated productivity insights"""

        metrics = self.get_detailed_metrics(start_date, end_date)
        insights = []

        # Task completion insights
        task_rate = metrics["task_metrics"]["completion_rate"]
        if task_rate > 0.8:
            insights.append(f"✅ Excellent task completion rate ({task_rate*100:.0f}%). Keep it up!")
        elif task_rate < 0.5:
            insights.append(
                f"⚠️ Low task completion rate ({task_rate*100:.0f}%). Consider reducing task list size."
            )

        # Focus time insights
        focus_hours = metrics["focus_metrics"]["total_focus_hours"]
        if focus_hours < 2:
            insights.append("💡 Try scheduling more deep focus sessions. Aim for 2-4 hours daily.")
        elif focus_hours > 6:
            insights.append("⚠️ You're in focus mode a lot. Remember to take breaks!")

        # Email response time insights
        email_response = metrics["communication_metrics"]["avg_email_response_time_hours"]
        if email_response < 2:
            insights.append("📧 Great email response time! Very responsive.")
        elif email_response > 24:
            insights.append(
                "📧 Email response time is slow. Consider setting aside time for email processing."
            )

        # Peak productivity hours
        peak_hours = self.engine.get_peak_productivity_hours()[:3]
        if peak_hours:
            peak_time = ", ".join([f"{h:02d}:00" for h, _ in peak_hours])
            insights.append(
                f"🕐 Your peak productivity hours are: {peak_time}. Schedule important tasks then."
            )

        # Consistency insights
        consistency = metrics["efficiency_metrics"]["consistency_score"]
        if consistency > 0.8:
            insights.append("📈 Excellent consistency! You're maintaining steady productivity.")
        elif consistency < 0.5:
            insights.append("📊 Productivity varies significantly. Try establishing a routine.")

        # Meeting efficiency
        meeting_hours = metrics["time_metrics"]["meeting_hours"]
        if meeting_hours > 20:
            insights.append(
                f"⏰ You spent {meeting_hours:.1f} hours in meetings. Consider consolidating or declining some."
            )

        return insights

    def get_productivity_goals(self) -> Dict[str, Dict[str, any]]:
        """Get recommended productivity goals"""

        current_metrics = self.get_detailed_metrics()

        goals = {
            "task_completion": {
                "current": current_metrics["task_metrics"]["completion_rate"],
                "target": 0.85,
                "recommendation": "Complete 85% of created tasks",
            },
            "focus_time": {
                "current": current_metrics["focus_metrics"]["total_focus_hours"],
                "target": 4.0,
                "recommendation": "Maintain 3-4 hours of deep focus daily",
            },
            "email_response": {
                "current": current_metrics["communication_metrics"][
                    "avg_email_response_time_hours"
                ],
                "target": 4.0,
                "recommendation": "Respond to emails within 4 hours",
            },
            "productivity_score": {
                "current": current_metrics["overall_score"],
                "target": 80.0,
                "recommendation": "Maintain overall productivity score above 80",
            },
        }

        return goals

    # Component score calculations
    def _calculate_task_score(self, events: List) -> float:
        """Calculate task completion score (0-100)"""

        tasks_created = sum(1 for e in events if e.activity_type == ActivityType.TASK_CREATED)
        tasks_completed = sum(1 for e in events if e.activity_type == ActivityType.TASK_COMPLETED)

        if tasks_created == 0:
            return 50.0  # Neutral score if no tasks

        completion_rate = tasks_completed / tasks_created

        # Scale to 0-100
        return min(completion_rate * 100, 100)

    def _calculate_focus_score(self, events: List) -> float:
        """Calculate focus time score (0-100)"""

        focus_events = [e for e in events if e.activity_type == ActivityType.FOCUS_SESSION]

        if not focus_events:
            return 30.0  # Low score if no focus sessions

        total_focus_hours = sum(e.duration_seconds for e in focus_events) / 3600
        completed_sessions = sum(1 for e in focus_events if e.metadata.get("completed", False))

        # Target: 3-4 hours of focus per day
        target_hours = 3.5
        time_score = min((total_focus_hours / target_hours) * 50, 50)

        # Completion rate
        completion_score = (completed_sessions / len(focus_events)) * 50 if focus_events else 0

        return time_score + completion_score

    def _calculate_communication_score(self, events: List) -> float:
        """Calculate communication efficiency score (0-100)"""

        emails_received = sum(1 for e in events if e.activity_type == ActivityType.EMAIL_READ)
        emails_replied = sum(1 for e in events if e.activity_type == ActivityType.EMAIL_REPLIED)

        if emails_received == 0:
            return 70.0  # Neutral-good score if no emails

        response_rate = emails_replied / emails_received

        # Scale to 0-100 (target 60-80% response rate)
        if response_rate >= 0.6 and response_rate <= 0.8:
            return 100.0
        elif response_rate < 0.3:
            return 40.0
        else:
            return response_rate * 100

    def _calculate_consistency_score(self, events: List) -> float:
        """Calculate productivity consistency score (0-100)"""

        # Group events by day
        daily_scores = {}

        for event in events:
            day = event.timestamp.date()
            if day not in daily_scores:
                daily_scores[day] = []
            daily_scores[day].append(event.productivity_score)

        if not daily_scores:
            return 50.0

        # Calculate daily averages
        daily_avgs = [sum(scores) / len(scores) for scores in daily_scores.values()]

        # Calculate coefficient of variation (lower is more consistent)
        if len(daily_avgs) < 2:
            return 70.0

        mean_score = sum(daily_avgs) / len(daily_avgs)
        variance = sum((x - mean_score) ** 2 for x in daily_avgs) / len(daily_avgs)
        std_dev = variance**0.5

        cv = std_dev / mean_score if mean_score > 0 else 1

        # Convert to score (lower CV = higher score)
        consistency = max(0, 100 - (cv * 100))

        return consistency

    def _calculate_output_score(self, events: List) -> float:
        """Calculate output/deliverables score (0-100)"""

        output_events = [
            e
            for e in events
            if e.activity_type
            in [
                ActivityType.GITHUB_COMMIT,
                ActivityType.GITHUB_PR,
                ActivityType.EMAIL_SENT,
                ActivityType.JOB_APPLICATION,
                ActivityType.LINKEDIN_POST,
            ]
        ]

        # Target: 5+ outputs per day
        days = len(set(e.timestamp.date() for e in events))
        if days == 0:
            return 50.0

        outputs_per_day = len(output_events) / days

        # Scale to 0-100
        return min((outputs_per_day / 5) * 100, 100)

    # Detailed metrics
    def _get_task_metrics(self, events: List) -> Dict[str, any]:
        """Get detailed task metrics"""

        tasks_created = sum(1 for e in events if e.activity_type == ActivityType.TASK_CREATED)
        tasks_completed = sum(1 for e in events if e.activity_type == ActivityType.TASK_COMPLETED)

        return {
            "tasks_created": tasks_created,
            "tasks_completed": tasks_completed,
            "completion_rate": tasks_completed / tasks_created if tasks_created > 0 else 0,
            "avg_completion_time_hours": 0,  # TODO: Track task creation to completion time
        }

    def _get_focus_metrics(self, events: List) -> Dict[str, any]:
        """Get detailed focus metrics"""

        focus_events = [e for e in events if e.activity_type == ActivityType.FOCUS_SESSION]

        total_hours = sum(e.duration_seconds for e in focus_events) / 3600
        completed = sum(1 for e in focus_events if e.metadata.get("completed", False))

        return {
            "total_focus_sessions": len(focus_events),
            "total_focus_hours": total_hours,
            "completed_sessions": completed,
            "completion_rate": completed / len(focus_events) if focus_events else 0,
            "avg_session_duration_minutes": (
                (total_hours * 60) / len(focus_events) if focus_events else 0
            ),
        }

    def _get_communication_metrics(self, events: List) -> Dict[str, any]:
        """Get detailed communication metrics"""

        emails_read = sum(1 for e in events if e.activity_type == ActivityType.EMAIL_READ)
        emails_sent = sum(1 for e in events if e.activity_type == ActivityType.EMAIL_SENT)
        emails_replied = sum(1 for e in events if e.activity_type == ActivityType.EMAIL_REPLIED)

        linkedin_messages = sum(
            1 for e in events if e.activity_type == ActivityType.LINKEDIN_MESSAGE
        )
        linkedin_posts = sum(1 for e in events if e.activity_type == ActivityType.LINKEDIN_POST)

        return {
            "emails_read": emails_read,
            "emails_sent": emails_sent,
            "emails_replied": emails_replied,
            "email_response_rate": emails_replied / emails_read if emails_read > 0 else 0,
            "avg_email_response_time_hours": 4.0,  # TODO: Track actual response times
            "linkedin_messages": linkedin_messages,
            "linkedin_posts": linkedin_posts,
        }

    def _get_time_metrics(self, events: List) -> Dict[str, any]:
        """Get time allocation metrics"""

        total_duration = sum(e.duration_seconds for e in events) / 3600

        meeting_hours = (
            sum(e.duration_seconds for e in events if e.activity_type == ActivityType.MEETING)
            / 3600
        )

        focus_hours = (
            sum(e.duration_seconds for e in events if e.activity_type == ActivityType.FOCUS_SESSION)
            / 3600
        )

        break_hours = (
            sum(e.duration_seconds for e in events if e.activity_type == ActivityType.BREAK) / 3600
        )

        return {
            "total_tracked_hours": total_duration,
            "meeting_hours": meeting_hours,
            "focus_hours": focus_hours,
            "break_hours": break_hours,
            "productive_hours": focus_hours,
            "meeting_percentage": meeting_hours / total_duration if total_duration > 0 else 0,
        }

    def _get_output_metrics(self, events: List) -> Dict[str, any]:
        """Get output/deliverables metrics"""

        github_commits = sum(1 for e in events if e.activity_type == ActivityType.GITHUB_COMMIT)
        github_prs = sum(1 for e in events if e.activity_type == ActivityType.GITHUB_PR)
        github_reviews = sum(1 for e in events if e.activity_type == ActivityType.GITHUB_REVIEW)

        job_applications = sum(1 for e in events if e.activity_type == ActivityType.JOB_APPLICATION)

        return {
            "github_commits": github_commits,
            "github_prs": github_prs,
            "github_reviews": github_reviews,
            "job_applications": job_applications,
            "total_deliverables": github_commits + github_prs + job_applications,
        }

    def _get_efficiency_metrics(self, events: List) -> Dict[str, any]:
        """Get efficiency metrics"""

        # Calculate productivity per hour
        total_duration_hours = sum(e.duration_seconds for e in events) / 3600
        total_productivity = sum(e.productivity_score for e in events)

        productivity_per_hour = (
            total_productivity / total_duration_hours if total_duration_hours > 0 else 0
        )

        # Calculate consistency
        consistency = self._calculate_consistency_score(events) / 100

        return {
            "productivity_per_hour": productivity_per_hour,
            "consistency_score": consistency,
            "total_activities": len(events),
            "avg_activity_score": (total_productivity / len(events) if events else 0),
        }


# Global instance
_productivity_scorer: Optional[ProductivityMetrics] = None


def get_productivity_scorer() -> ProductivityMetrics:
    """Get global productivity scorer"""
    global _productivity_scorer
    if _productivity_scorer is None:
        _productivity_scorer = ProductivityMetrics()
    return _productivity_scorer
