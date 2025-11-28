"""
Sample Plugin: Task Stats
Demonstrates analytics plugin capabilities
"""

from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.plugins.plugin_base import AnalyticsPlugin, PluginContext


class Plugin(AnalyticsPlugin):
    """
    Task Statistics Plugin
    Analyzes task completion patterns and provides insights
    """

    def initialize(self, context: PluginContext, config: Dict[str, Any]) -> bool:
        """Initialize plugin"""
        self.context = context
        self._config = config
        self.logger.info("Task Stats Plugin initialized")
        return True

    def activate(self) -> bool:
        """Activate plugin"""
        self.logger.info("Task Stats Plugin activated")
        return True

    def deactivate(self) -> bool:
        """Deactivate plugin"""
        self.logger.info("Task Stats Plugin deactivated")
        return True

    def analyze(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze task data"""
        if not data:
            return {"error": "No data provided"}

        # Filter completed tasks
        completed_tasks = [
            t for t in data if t.get("status") == "completed" and "completed_at" in t
        ]

        # Calculate statistics
        total_tasks = len(data)
        completed_count = len(completed_tasks)
        completion_rate = (
            completed_count / total_tasks if total_tasks > 0 else 0
        )

        # Priority distribution
        priority_dist = Counter(t.get("priority", "medium") for t in data)

        # Tag frequency
        all_tags = []
        for task in data:
            if "tags" in task and task["tags"]:
                all_tags.extend(task["tags"])
        tag_freq = Counter(all_tags)

        # Average completion time
        completion_times = []
        for task in completed_tasks:
            if "created_at" in task and "completed_at" in task:
                try:
                    created = datetime.fromisoformat(task["created_at"])
                    completed = datetime.fromisoformat(task["completed_at"])
                    duration = (completed - created).total_seconds() / 3600  # hours
                    completion_times.append(duration)
                except:
                    continue

        avg_completion_time = (
            sum(completion_times) / len(completion_times)
            if completion_times
            else 0
        )

        # Productivity by day of week
        daily_completions = {i: 0 for i in range(7)}
        for task in completed_tasks:
            if "completed_at" in task:
                try:
                    completed = datetime.fromisoformat(task["completed_at"])
                    daily_completions[completed.weekday()] += 1
                except:
                    continue

        # Most productive day
        most_productive_day = max(daily_completions.items(), key=lambda x: x[1])
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Recent trends (last 7 days)
        now = datetime.now()
        recent_tasks = [
            t
            for t in completed_tasks
            if "completed_at" in t
            and datetime.fromisoformat(t["completed_at"]) > now - timedelta(days=7)
        ]

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_count,
            "completion_rate": completion_rate,
            "priority_distribution": dict(priority_dist),
            "top_tags": dict(tag_freq.most_common(10)),
            "average_completion_hours": round(avg_completion_time, 2),
            "daily_completions": {
                day_names[day]: count for day, count in daily_completions.items()
            },
            "most_productive_day": day_names[most_productive_day[0]],
            "recent_completions": len(recent_tasks),
            "insights": self._generate_insights(
                completion_rate,
                avg_completion_time,
                most_productive_day,
                day_names,
            ),
        }

    def _generate_insights(
        self,
        completion_rate: float,
        avg_completion_time: float,
        most_productive_day: tuple,
        day_names: list,
    ) -> List[str]:
        """Generate insights from statistics"""
        insights = []

        # Completion rate insights
        if completion_rate >= 0.8:
            insights.append("Excellent completion rate! You're staying on top of your tasks.")
        elif completion_rate >= 0.6:
            insights.append("Good completion rate. Consider prioritizing remaining tasks.")
        else:
            insights.append("Low completion rate. You may want to review your task load.")

        # Completion time insights
        if avg_completion_time < 24:
            insights.append("Tasks are being completed quickly, usually within a day.")
        elif avg_completion_time < 72:
            insights.append("Tasks typically take 1-3 days to complete.")
        else:
            insights.append("Tasks take longer to complete. Consider breaking them down.")

        # Productivity insights
        day_name = day_names[most_productive_day[0]]
        insights.append(f"You're most productive on {day_name}s.")

        return insights

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "include_archived": {"type": "boolean", "default": False},
            },
            "required": [],
        }
