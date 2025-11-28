"""
Task Prediction Model
ML-based task prediction using time series analysis
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.logger import setup_logger


class TaskPredictor:
    """Predicts tasks using time series analysis"""

    def __init__(self):
        self.logger = setup_logger("prediction.task")

        # Training data
        self.training_data: List[Dict[str, Any]] = []

        # Model state
        self.feature_weights: Dict[str, float] = {
            "time_of_day": 0.25,
            "day_of_week": 0.20,
            "historical_frequency": 0.30,
            "recent_activity": 0.15,
            "context_similarity": 0.10,
        }

        # Task templates learned from history
        self.task_templates: Dict[str, Dict[str, Any]] = {}

    def train(self, historical_tasks: List[Dict[str, Any]]):
        """Train predictor on historical tasks"""
        self.training_data = historical_tasks

        # Learn task templates
        self._extract_task_templates(historical_tasks)

        # Build time series features
        self._build_time_series_features(historical_tasks)

        self.logger.info(f"Trained on {len(historical_tasks)} tasks")

    def _extract_task_templates(self, tasks: List[Dict[str, Any]]):
        """Extract common task templates"""
        from collections import defaultdict

        task_groups = defaultdict(list)

        for task in tasks:
            if "title" not in task:
                continue

            # Group by title
            task_groups[task["title"]].append(task)

        # Create templates for frequent tasks
        for title, task_list in task_groups.items():
            if len(task_list) >= 3:  # Minimum occurrences
                template = {
                    "title": title,
                    "count": len(task_list),
                    "avg_priority": self._get_avg_priority(task_list),
                    "common_tags": self._get_common_tags(task_list),
                    "typical_duration": self._get_avg_duration(task_list),
                    "time_distribution": self._get_time_distribution(task_list),
                }

                self.task_templates[title] = template

        self.logger.debug(f"Extracted {len(self.task_templates)} task templates")

    def _get_avg_priority(self, tasks: List[Dict[str, Any]]) -> str:
        """Get most common priority"""
        from collections import Counter

        priorities = [t.get("priority", "medium") for t in tasks]
        if priorities:
            return Counter(priorities).most_common(1)[0][0]
        return "medium"

    def _get_common_tags(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Get most common tags"""
        from collections import Counter

        all_tags = []
        for task in tasks:
            if "tags" in task and task["tags"]:
                all_tags.extend(task["tags"])

        if all_tags:
            common = Counter(all_tags).most_common(3)
            return [tag for tag, _ in common]
        return []

    def _get_avg_duration(self, tasks: List[Dict[str, Any]]) -> Optional[float]:
        """Get average task duration in minutes"""
        durations = []

        for task in tasks:
            if "completed_at" in task and "created_at" in task:
                try:
                    completed = datetime.fromisoformat(task["completed_at"])
                    created = datetime.fromisoformat(task["created_at"])
                    duration = (completed - created).total_seconds() / 60
                    durations.append(duration)
                except (ValueError, KeyError):
                    continue

        return sum(durations) / len(durations) if durations else None

    def _get_time_distribution(self, tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Get time distribution (hours when task is typically created)"""
        hours = []

        for task in tasks:
            if "created_at" in task:
                try:
                    created = datetime.fromisoformat(task["created_at"])
                    hours.append(created.hour)
                except (ValueError, KeyError):
                    continue

        if not hours:
            return {}

        # Create distribution
        distribution = {}
        for hour in range(24):
            count = hours.count(hour)
            distribution[str(hour)] = count / len(hours) if hours else 0

        return distribution

    def _build_time_series_features(self, tasks: List[Dict[str, Any]]):
        """Build time series features from tasks"""
        # Sort tasks by time
        sorted_tasks = sorted(
            [t for t in tasks if "created_at" in t],
            key=lambda t: datetime.fromisoformat(t["created_at"]),
        )

        # Extract features over time
        self.time_series_features = {
            "hourly_task_count": self._get_hourly_counts(sorted_tasks),
            "daily_task_count": self._get_daily_counts(sorted_tasks),
            "weekday_patterns": self._get_weekday_patterns(sorted_tasks),
        }

    def _get_hourly_counts(self, tasks: List[Dict[str, Any]]) -> Dict[int, int]:
        """Get task count per hour of day"""
        hourly = {h: 0 for h in range(24)}

        for task in tasks:
            try:
                created = datetime.fromisoformat(task["created_at"])
                hourly[created.hour] += 1
            except (ValueError, KeyError):
                continue

        return hourly

    def _get_daily_counts(self, tasks: List[Dict[str, Any]]) -> Dict[int, int]:
        """Get task count per day of week"""
        daily = {d: 0 for d in range(7)}

        for task in tasks:
            try:
                created = datetime.fromisoformat(task["created_at"])
                daily[created.weekday()] += 1
            except (ValueError, KeyError):
                continue

        return daily

    def _get_weekday_patterns(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get patterns for each weekday"""
        patterns = {}

        for day in range(7):
            day_tasks = [
                t
                for t in tasks
                if datetime.fromisoformat(t.get("created_at", "")).weekday() == day
            ]

            patterns[str(day)] = {
                "count": len(day_tasks),
                "avg_hour": self._get_avg_hour(day_tasks),
                "common_priorities": self._get_common_priorities(day_tasks),
            }

        return patterns

    def _get_avg_hour(self, tasks: List[Dict[str, Any]]) -> float:
        """Get average hour of day for tasks"""
        hours = []

        for task in tasks:
            if "created_at" in task:
                try:
                    created = datetime.fromisoformat(task["created_at"])
                    hours.append(created.hour)
                except (ValueError, KeyError):
                    continue

        return sum(hours) / len(hours) if hours else 12.0

    def _get_common_priorities(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Get common priorities"""
        from collections import Counter

        priorities = [t.get("priority", "medium") for t in tasks]
        common = Counter(priorities).most_common(3)
        return [p for p, _ in common]

    def predict_tasks(
        self, context: Dict[str, Any] = None, max_predictions: int = 10
    ) -> List[Dict[str, Any]]:
        """Predict likely tasks for current/future time"""
        predictions = []
        now = datetime.now()

        if context is None:
            context = {}

        # Get current time features
        current_hour = context.get("hour", now.hour)
        current_day = context.get("day_of_week", now.weekday())

        # Score each task template
        for title, template in self.task_templates.items():
            score = self._calculate_prediction_score(
                template, current_hour, current_day, context
            )

            if score > 0.3:  # Threshold
                predictions.append({
                    "title": title,
                    "probability": score,
                    "priority": template["avg_priority"],
                    "tags": template["common_tags"],
                    "estimated_duration": template.get("typical_duration"),
                    "reason": self._generate_prediction_reason(template, current_hour, current_day),
                    "template_match": True,
                })

        # Generate new task suggestions based on patterns
        pattern_predictions = self._generate_pattern_predictions(current_hour, current_day)
        predictions.extend(pattern_predictions)

        # Sort by probability
        predictions.sort(key=lambda p: p["probability"], reverse=True)

        return predictions[:max_predictions]

    def _calculate_prediction_score(
        self,
        template: Dict[str, Any],
        current_hour: int,
        current_day: int,
        context: Dict[str, Any],
    ) -> float:
        """Calculate prediction score for a task template"""
        score = 0.0

        # Time of day score
        time_dist = template.get("time_distribution", {})
        time_score = time_dist.get(str(current_hour), 0.0)
        score += time_score * self.feature_weights["time_of_day"]

        # Day of week score
        if hasattr(self, "time_series_features"):
            day_pattern = self.time_series_features["weekday_patterns"].get(str(current_day), {})
            day_score = day_pattern.get("count", 0) / max(
                sum(p.get("count", 0) for p in self.time_series_features["weekday_patterns"].values()),
                1,
            )
            score += day_score * self.feature_weights["day_of_week"]

        # Historical frequency score
        total_templates = len(self.task_templates)
        frequency_score = template["count"] / max(
            sum(t["count"] for t in self.task_templates.values()), 1
        )
        score += frequency_score * self.feature_weights["historical_frequency"]

        # Recent activity score (check if similar tasks were created recently)
        recent_score = self._calculate_recent_activity_score(template)
        score += recent_score * self.feature_weights["recent_activity"]

        # Context similarity score
        context_score = self._calculate_context_similarity(template, context)
        score += context_score * self.feature_weights["context_similarity"]

        return min(1.0, score)

    def _calculate_recent_activity_score(self, template: Dict[str, Any]) -> float:
        """Calculate score based on recent similar activity"""
        # Check last 7 days for similar tasks
        now = datetime.now()
        cutoff = now - timedelta(days=7)

        recent_tasks = [
            t
            for t in self.training_data
            if "created_at" in t
            and datetime.fromisoformat(t["created_at"]) > cutoff
            and t.get("title") == template["title"]
        ]

        # Score based on recency
        if recent_tasks:
            return min(1.0, len(recent_tasks) / 5.0)

        return 0.0

    def _calculate_context_similarity(
        self, template: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """Calculate similarity between template and current context"""
        score = 0.0
        factors = 0

        # Priority match
        if "priority" in context and context["priority"] == template["avg_priority"]:
            score += 1.0
            factors += 1

        # Tag overlap
        if "tags" in context and template["common_tags"]:
            context_tags = set(context["tags"])
            template_tags = set(template["common_tags"])
            overlap = len(context_tags & template_tags)
            if template_tags:
                score += overlap / len(template_tags)
                factors += 1

        return score / factors if factors > 0 else 0.0

    def _generate_prediction_reason(
        self, template: Dict[str, Any], current_hour: int, current_day: int
    ) -> str:
        """Generate human-readable reason for prediction"""
        reasons = []

        # Check time of day
        time_dist = template.get("time_distribution", {})
        if time_dist.get(str(current_hour), 0) > 0.1:
            reasons.append(f"typically created around {current_hour}:00")

        # Check frequency
        if template["count"] >= 10:
            reasons.append(f"created {template['count']} times before")

        # Check recency
        recent_score = self._calculate_recent_activity_score(template)
        if recent_score > 0.3:
            reasons.append("created recently")

        if reasons:
            return "Predicted because: " + ", ".join(reasons)
        return "Based on historical patterns"

    def _generate_pattern_predictions(
        self, current_hour: int, current_day: int
    ) -> List[Dict[str, Any]]:
        """Generate predictions based on general patterns"""
        predictions = []

        # Check if this is a high-activity time
        if hasattr(self, "time_series_features"):
            hourly_counts = self.time_series_features["hourly_task_count"]
            avg_hourly = sum(hourly_counts.values()) / len(hourly_counts)

            if hourly_counts.get(current_hour, 0) > avg_hourly * 1.5:
                # High activity hour
                predictions.append({
                    "title": "Review pending tasks",
                    "probability": 0.6,
                    "priority": "medium",
                    "tags": ["review"],
                    "estimated_duration": 15,
                    "reason": f"High activity hour (typically {int(hourly_counts[current_hour])} tasks created)",
                    "template_match": False,
                })

        return predictions

    def get_prediction_accuracy(self, actual_tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate prediction accuracy"""
        if not actual_tasks:
            return {"accuracy": 0.0, "precision": 0.0, "recall": 0.0}

        # Get predictions for the time period
        predictions = self.predict_tasks()
        predicted_titles = {p["title"] for p in predictions}
        actual_titles = {t.get("title") for t in actual_tasks if "title" in t}

        # Calculate metrics
        true_positives = len(predicted_titles & actual_titles)
        false_positives = len(predicted_titles - actual_titles)
        false_negatives = len(actual_titles - predicted_titles)

        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )

        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )

        accuracy = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        }


# Global instance
_task_predictor: Optional[TaskPredictor] = None


def get_task_predictor() -> TaskPredictor:
    """Get global task predictor"""
    global _task_predictor
    if _task_predictor is None:
        _task_predictor = TaskPredictor()
    return _task_predictor
