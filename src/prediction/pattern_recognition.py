"""
Pattern Recognition Engine
Detects recurring patterns in user behavior and tasks
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.logger import setup_logger


class Pattern:
    """Represents a detected pattern"""

    def __init__(
        self,
        pattern_id: str,
        pattern_type: str,
        description: str,
        confidence: float,
        frequency: str,
    ):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type  # time, sequence, recurring, contextual
        self.description = description
        self.confidence = confidence  # 0-1
        self.frequency = frequency  # daily, weekly, monthly, custom

        # Pattern details
        self.attributes: Dict[str, Any] = {}
        self.occurrences: List[datetime] = []
        self.last_detected = datetime.now()

        # Prediction
        self.next_expected: Optional[datetime] = None
        self.probability = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "attributes": self.attributes,
            "occurrence_count": len(self.occurrences),
            "last_detected": self.last_detected.isoformat(),
            "next_expected": self.next_expected.isoformat() if self.next_expected else None,
            "probability": self.probability,
        }


class PatternRecognitionEngine:
    """Detects patterns in user behavior"""

    def __init__(self):
        self.logger = setup_logger("prediction.pattern")

        # Detected patterns
        self.patterns: Dict[str, Pattern] = {}

        # Historical data
        self.task_history: List[Dict[str, Any]] = []
        self.activity_history: List[Dict[str, Any]] = []

        # Pattern detection parameters
        self.min_occurrences = 3  # Minimum occurrences to establish pattern
        self.time_window_days = 30  # Look back window

    def analyze_task_history(self, tasks: List[Dict[str, Any]]) -> List[Pattern]:
        """Analyze task history to detect patterns"""
        self.task_history.extend(tasks)
        detected_patterns = []

        # Detect time-based patterns
        time_patterns = self._detect_time_patterns(tasks)
        detected_patterns.extend(time_patterns)

        # Detect recurring task patterns
        recurring_patterns = self._detect_recurring_tasks(tasks)
        detected_patterns.extend(recurring_patterns)

        # Detect sequence patterns
        sequence_patterns = self._detect_task_sequences(tasks)
        detected_patterns.extend(sequence_patterns)

        # Detect contextual patterns
        contextual_patterns = self._detect_contextual_patterns(tasks)
        detected_patterns.extend(contextual_patterns)

        # Store patterns
        for pattern in detected_patterns:
            self.patterns[pattern.pattern_id] = pattern

        self.logger.info(f"Detected {len(detected_patterns)} patterns")
        return detected_patterns

    def _detect_time_patterns(self, tasks: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect time-based patterns (same task at same time)"""
        patterns = []

        # Group tasks by title and hour
        task_times = defaultdict(list)

        for task in tasks:
            if "created_at" not in task or "title" not in task:
                continue

            try:
                created_at = datetime.fromisoformat(task["created_at"])
                hour = created_at.hour
                day_of_week = created_at.weekday()

                key = f"{task['title']}_{hour}_{day_of_week}"
                task_times[key].append(created_at)
            except (ValueError, KeyError):
                continue

        # Find patterns with sufficient occurrences
        for key, timestamps in task_times.items():
            if len(timestamps) >= self.min_occurrences:
                parts = key.split("_")
                task_title = "_".join(parts[:-2])
                hour = int(parts[-2])
                day_of_week = int(parts[-1])

                # Calculate confidence based on consistency
                time_diffs = []
                for i in range(1, len(timestamps)):
                    diff = (timestamps[i] - timestamps[i - 1]).total_seconds()
                    time_diffs.append(diff)

                # Check if times are consistent (within 1 hour variance)
                if time_diffs:
                    avg_diff = sum(time_diffs) / len(time_diffs)
                    variance = sum((d - avg_diff) ** 2 for d in time_diffs) / len(time_diffs)
                    std_dev = variance ** 0.5

                    # High confidence if low variance
                    confidence = max(0.0, 1.0 - (std_dev / (7 * 24 * 3600)))  # Normalize by week
                else:
                    confidence = 0.5

                if confidence >= 0.6:
                    pattern = Pattern(
                        pattern_id=f"time_{key}",
                        pattern_type="time",
                        description=f"'{task_title}' typically created on {self._get_day_name(day_of_week)} at {hour:02d}:00",
                        confidence=confidence,
                        frequency="weekly",
                    )

                    pattern.attributes = {
                        "task_title": task_title,
                        "hour": hour,
                        "day_of_week": day_of_week,
                    }
                    pattern.occurrences = timestamps

                    # Predict next occurrence
                    last_occurrence = timestamps[-1]
                    days_until_next = (7 - last_occurrence.weekday() + day_of_week) % 7
                    if days_until_next == 0:
                        days_until_next = 7

                    pattern.next_expected = last_occurrence + timedelta(days=days_until_next)
                    pattern.next_expected = pattern.next_expected.replace(hour=hour, minute=0, second=0)
                    pattern.probability = confidence

                    patterns.append(pattern)

        return patterns

    def _detect_recurring_tasks(self, tasks: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect tasks that recur regularly"""
        patterns = []

        # Group tasks by title
        task_groups = defaultdict(list)

        for task in tasks:
            if "title" in task and "created_at" in task:
                try:
                    created_at = datetime.fromisoformat(task["created_at"])
                    task_groups[task["title"]].append(created_at)
                except (ValueError, KeyError):
                    continue

        # Analyze each task group
        for title, timestamps in task_groups.items():
            if len(timestamps) >= self.min_occurrences:
                timestamps.sort()

                # Calculate intervals
                intervals = []
                for i in range(1, len(timestamps)):
                    interval = (timestamps[i] - timestamps[i - 1]).total_seconds() / 86400  # Days
                    intervals.append(interval)

                if not intervals:
                    continue

                # Check if intervals are consistent
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
                std_dev = variance ** 0.5

                # Determine frequency
                frequency = "custom"
                if 0.8 <= avg_interval <= 1.2:
                    frequency = "daily"
                elif 6.5 <= avg_interval <= 7.5:
                    frequency = "weekly"
                elif 13 <= avg_interval <= 15:
                    frequency = "biweekly"
                elif 28 <= avg_interval <= 31:
                    frequency = "monthly"

                # High confidence if consistent
                confidence = max(0.0, 1.0 - (std_dev / avg_interval)) if avg_interval > 0 else 0.0

                if confidence >= 0.6:
                    pattern = Pattern(
                        pattern_id=f"recurring_{title.replace(' ', '_')}",
                        pattern_type="recurring",
                        description=f"'{title}' recurs {frequency} (every {avg_interval:.1f} days)",
                        confidence=confidence,
                        frequency=frequency,
                    )

                    pattern.attributes = {
                        "task_title": title,
                        "avg_interval_days": avg_interval,
                        "std_dev": std_dev,
                    }
                    pattern.occurrences = timestamps

                    # Predict next occurrence
                    last_occurrence = timestamps[-1]
                    pattern.next_expected = last_occurrence + timedelta(days=avg_interval)
                    pattern.probability = confidence

                    patterns.append(pattern)

        return patterns

    def _detect_task_sequences(self, tasks: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect sequences of tasks that occur together"""
        patterns = []

        # Sort tasks by time
        sorted_tasks = sorted(
            [t for t in tasks if "created_at" in t and "title" in t],
            key=lambda t: datetime.fromisoformat(t["created_at"]),
        )

        # Look for task sequences (tasks created within 1 hour)
        sequences = []
        current_sequence = []
        last_time = None

        for task in sorted_tasks:
            try:
                created_at = datetime.fromisoformat(task["created_at"])

                if last_time and (created_at - last_time).total_seconds() <= 3600:
                    current_sequence.append(task["title"])
                else:
                    if len(current_sequence) >= 2:
                        sequences.append(tuple(current_sequence))
                    current_sequence = [task["title"]]

                last_time = created_at
            except (ValueError, KeyError):
                continue

        # Count sequence frequencies
        sequence_counts = Counter(sequences)

        for sequence, count in sequence_counts.items():
            if count >= self.min_occurrences:
                confidence = min(1.0, count / 10.0)  # Scale confidence

                pattern = Pattern(
                    pattern_id=f"sequence_{'_'.join(sequence)}",
                    pattern_type="sequence",
                    description=f"Task sequence: {' → '.join(sequence)}",
                    confidence=confidence,
                    frequency="conditional",
                )

                pattern.attributes = {
                    "sequence": list(sequence),
                    "occurrence_count": count,
                }
                pattern.probability = confidence * 0.8  # Slightly lower for sequences

                patterns.append(pattern)

        return patterns

    def _detect_contextual_patterns(self, tasks: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns based on context (tags, priority, etc.)"""
        patterns = []

        # Group tasks by context attributes
        context_groups = defaultdict(lambda: defaultdict(list))

        for task in tasks:
            if "created_at" not in task:
                continue

            try:
                created_at = datetime.fromisoformat(task["created_at"])

                # Group by priority
                if "priority" in task:
                    context_groups["priority"][task["priority"]].append(created_at)

                # Group by tags
                if "tags" in task and task["tags"]:
                    for tag in task["tags"]:
                        context_groups["tag"][tag].append(created_at)

                # Group by day of week
                day_of_week = created_at.weekday()
                context_groups["day_of_week"][day_of_week].append(task)

            except (ValueError, KeyError):
                continue

        # Analyze day-of-week patterns
        for day, day_tasks in context_groups["day_of_week"].items():
            if len(day_tasks) >= self.min_occurrences:
                # Check if certain types of tasks happen on specific days
                task_titles = [t.get("title", "") for t in day_tasks]
                most_common = Counter(task_titles).most_common(1)

                if most_common:
                    common_task, count = most_common[0]
                    confidence = count / len(day_tasks)

                    if confidence >= 0.5:
                        pattern = Pattern(
                            pattern_id=f"contextual_day_{day}_{common_task.replace(' ', '_')}",
                            pattern_type="contextual",
                            description=f"'{common_task}' frequently created on {self._get_day_name(day)}",
                            confidence=confidence,
                            frequency="weekly",
                        )

                        pattern.attributes = {
                            "context": "day_of_week",
                            "day": day,
                            "task_title": common_task,
                        }
                        pattern.probability = confidence * 0.7

                        patterns.append(pattern)

        return patterns

    def predict_next_tasks(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Predict likely next tasks based on patterns"""
        predictions = []
        now = datetime.now()

        for pattern in self.patterns.values():
            if pattern.next_expected and pattern.next_expected > now:
                # Check if it's time for this pattern
                time_until = (pattern.next_expected - now).total_seconds()

                # Predict if within next 24 hours
                if time_until <= 86400:
                    predictions.append({
                        "pattern_id": pattern.pattern_id,
                        "pattern_type": pattern.pattern_type,
                        "description": pattern.description,
                        "probability": pattern.probability,
                        "expected_time": pattern.next_expected.isoformat(),
                        "time_until_seconds": time_until,
                        "attributes": pattern.attributes,
                    })

        # Sort by probability
        predictions.sort(key=lambda p: p["probability"], reverse=True)

        return predictions

    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights about detected patterns"""
        insights = {
            "total_patterns": len(self.patterns),
            "by_type": defaultdict(int),
            "by_frequency": defaultdict(int),
            "high_confidence": [],
            "upcoming_predictions": [],
        }

        for pattern in self.patterns.values():
            insights["by_type"][pattern.pattern_type] += 1
            insights["by_frequency"][pattern.frequency] += 1

            if pattern.confidence >= 0.8:
                insights["high_confidence"].append(pattern.to_dict())

        # Get upcoming predictions
        predictions = self.predict_next_tasks()
        insights["upcoming_predictions"] = predictions[:5]

        return insights

    def _get_day_name(self, day: int) -> str:
        """Get day name from index"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[day] if 0 <= day < 7 else "Unknown"

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get pattern by ID"""
        return self.patterns.get(pattern_id)

    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern"""
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            self.logger.info(f"Removed pattern: {pattern_id}")
            return True
        return False

    def update_pattern_confidence(self, pattern_id: str, success: bool):
        """Update pattern confidence based on prediction success"""
        pattern = self.get_pattern(pattern_id)
        if pattern:
            # Adjust confidence
            if success:
                pattern.confidence = min(1.0, pattern.confidence + 0.05)
            else:
                pattern.confidence = max(0.0, pattern.confidence - 0.1)

            # Remove pattern if confidence too low
            if pattern.confidence < 0.3:
                self.remove_pattern(pattern_id)

    def export_patterns(self) -> str:
        """Export patterns to JSON"""
        data = {
            "patterns": {pid: p.to_dict() for pid, p in self.patterns.items()},
            "export_time": datetime.now().isoformat(),
        }
        return json.dumps(data, indent=2)

    def import_patterns(self, json_data: str):
        """Import patterns from JSON"""
        try:
            data = json.loads(json_data)

            for pid, pattern_data in data.get("patterns", {}).items():
                pattern = Pattern(
                    pattern_id=pattern_data["pattern_id"],
                    pattern_type=pattern_data["pattern_type"],
                    description=pattern_data["description"],
                    confidence=pattern_data["confidence"],
                    frequency=pattern_data["frequency"],
                )

                pattern.attributes = pattern_data.get("attributes", {})
                pattern.last_detected = datetime.fromisoformat(pattern_data["last_detected"])

                if pattern_data.get("next_expected"):
                    pattern.next_expected = datetime.fromisoformat(pattern_data["next_expected"])

                pattern.probability = pattern_data.get("probability", 0.0)

                self.patterns[pid] = pattern

            self.logger.info(f"Imported {len(self.patterns)} patterns")

        except Exception as e:
            self.logger.error(f"Error importing patterns: {e}")


# Global instance
_pattern_engine: Optional[PatternRecognitionEngine] = None


def get_pattern_engine() -> PatternRecognitionEngine:
    """Get global pattern engine"""
    global _pattern_engine
    if _pattern_engine is None:
        _pattern_engine = PatternRecognitionEngine()
    return _pattern_engine
