"""
Auto-Scheduler
Intelligently schedules tasks based on priorities, deadlines, and patterns
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger


class ScheduleSlot:
    """Represents a time slot in the schedule"""

    def __init__(
        self,
        start_time: datetime,
        end_time: datetime,
        task_id: Optional[str] = None,
        is_available: bool = True,
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.task_id = task_id
        self.is_available = is_available

    @property
    def duration_minutes(self) -> float:
        """Get slot duration in minutes"""
        return (self.end_time - self.start_time).total_seconds() / 60

    def overlaps(self, other: "ScheduleSlot") -> bool:
        """Check if this slot overlaps with another"""
        return self.start_time < other.end_time and self.end_time > other.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "task_id": self.task_id,
            "is_available": self.is_available,
            "duration_minutes": self.duration_minutes,
        }


class AutoScheduler:
    """Automatically schedules tasks"""

    def __init__(self):
        self.logger = setup_logger("prediction.scheduler")

        # Scheduling preferences
        self.work_start_hour = 9  # 9 AM
        self.work_end_hour = 17  # 5 PM
        self.min_slot_duration = 15  # minutes
        self.break_duration = 10  # minutes between tasks

        # Energy levels by hour (0-1 scale)
        self.energy_curve = self._default_energy_curve()

        # Scheduled slots
        self.schedule: List[ScheduleSlot] = []

    def _default_energy_curve(self) -> Dict[int, float]:
        """Default energy levels by hour of day"""
        return {
            0: 0.1,
            1: 0.05,
            2: 0.05,
            3: 0.05,
            4: 0.1,
            5: 0.2,
            6: 0.3,
            7: 0.5,
            8: 0.7,
            9: 0.9,
            10: 0.95,
            11: 0.9,
            12: 0.7,
            13: 0.6,
            14: 0.8,
            15: 0.85,
            16: 0.75,
            17: 0.6,
            18: 0.5,
            19: 0.4,
            20: 0.3,
            21: 0.25,
            22: 0.2,
            23: 0.15,
        }

    def set_work_hours(self, start_hour: int, end_hour: int):
        """Set working hours"""
        self.work_start_hour = start_hour
        self.work_end_hour = end_hour
        self.logger.info(f"Work hours set to {start_hour}:00 - {end_hour}:00")

    def set_energy_curve(self, energy_levels: Dict[int, float]):
        """Set custom energy curve"""
        self.energy_curve = energy_levels
        self.logger.debug("Custom energy curve applied")

    def schedule_tasks(
        self,
        tasks: List[Dict[str, Any]],
        start_date: Optional[datetime] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Schedule multiple tasks over a time period"""
        if start_date is None:
            start_date = datetime.now()

        # Reset schedule
        self.schedule = []

        # Sort tasks by priority and deadline
        sorted_tasks = self._prioritize_tasks(tasks)

        # Generate available time slots
        available_slots = self._generate_time_slots(start_date, days)

        # Schedule each task
        scheduled = []
        for task in sorted_tasks:
            slot = self._find_best_slot(task, available_slots)

            if slot:
                # Mark slot as used
                slot.task_id = task.get("id", task.get("title"))
                slot.is_available = False

                scheduled.append(
                    {
                        "task": task,
                        "scheduled_time": slot.start_time.isoformat(),
                        "estimated_end": slot.end_time.isoformat(),
                        "duration_minutes": slot.duration_minutes,
                        "energy_level": self.energy_curve.get(slot.start_time.hour, 0.5),
                    }
                )

                self.logger.debug(f"Scheduled '{task.get('title')}' at {slot.start_time}")
            else:
                self.logger.warning(f"Could not find slot for '{task.get('title')}'")

        self.logger.info(f"Scheduled {len(scheduled)}/{len(tasks)} tasks")
        return scheduled

    def _prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort tasks by priority and deadline"""

        def task_score(task: Dict[str, Any]) -> float:
            score = 0.0

            # Priority score
            priority_scores = {"high": 3.0, "medium": 2.0, "low": 1.0}
            score += priority_scores.get(task.get("priority", "medium"), 2.0) * 10

            # Deadline urgency
            if "deadline" in task:
                try:
                    deadline = datetime.fromisoformat(task["deadline"])
                    days_until = (deadline - datetime.now()).days
                    if days_until < 0:
                        score += 50  # Overdue
                    elif days_until < 1:
                        score += 40  # Due today
                    elif days_until < 3:
                        score += 30  # Due soon
                    elif days_until < 7:
                        score += 20  # Due this week
                except (ValueError, KeyError):
                    pass

            # Estimated duration (shorter tasks score higher for quick wins)
            duration = task.get("estimated_duration", 60)
            if duration < 30:
                score += 5  # Quick task bonus

            return score

        return sorted(tasks, key=task_score, reverse=True)

    def _generate_time_slots(self, start_date: datetime, days: int) -> List[ScheduleSlot]:
        """Generate available time slots"""
        slots = []

        for day in range(days):
            current_date = start_date + timedelta(days=day)

            # Skip weekends (optional)
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue

            # Create slots for work hours
            for hour in range(self.work_start_hour, self.work_end_hour):
                # Create slots every 15 minutes
                for minute in [0, 15, 30, 45]:
                    slot_start = current_date.replace(
                        hour=hour, minute=minute, second=0, microsecond=0
                    )
                    slot_end = slot_start + timedelta(minutes=self.min_slot_duration)

                    # Don't create slots in the past
                    if slot_start > datetime.now():
                        slots.append(ScheduleSlot(slot_start, slot_end))

        self.logger.debug(f"Generated {len(slots)} time slots")
        return slots

    def _find_best_slot(
        self, task: Dict[str, Any], available_slots: List[ScheduleSlot]
    ) -> Optional[ScheduleSlot]:
        """Find the best time slot for a task"""
        duration = task.get("estimated_duration", 60)  # minutes
        priority = task.get("priority", "medium")

        # Filter available slots
        available = [s for s in available_slots if s.is_available]

        if not available:
            return None

        # Find consecutive slots to fit task duration
        best_slot = None
        best_score = -1

        for i, slot in enumerate(available):
            # Check if we can fit the task
            consecutive_slots = self._find_consecutive_slots(available, i, duration)

            if consecutive_slots:
                # Calculate slot score
                score = self._calculate_slot_score(consecutive_slots[0], task, duration)

                if score > best_score:
                    best_score = score
                    # Merge consecutive slots
                    best_slot = ScheduleSlot(
                        consecutive_slots[0].start_time,
                        consecutive_slots[-1].end_time,
                    )

        return best_slot

    def _find_consecutive_slots(
        self, slots: List[ScheduleSlot], start_idx: int, duration_minutes: float
    ) -> Optional[List[ScheduleSlot]]:
        """Find consecutive slots that fit the duration"""
        consecutive = []
        total_duration = 0

        for slot in slots[start_idx:]:
            if not slot.is_available:
                break

            # Check continuity
            if consecutive and slot.start_time > consecutive[-1].end_time:
                break

            consecutive.append(slot)
            total_duration += slot.duration_minutes

            if total_duration >= duration_minutes:
                return consecutive

        return None if total_duration < duration_minutes else consecutive

    def _calculate_slot_score(
        self, slot: ScheduleSlot, task: Dict[str, Any], duration: float
    ) -> float:
        """Calculate how good a slot is for a task"""
        score = 0.0

        # Energy level match
        energy = self.energy_curve.get(slot.start_time.hour, 0.5)

        # High priority tasks get high energy slots
        if task.get("priority") == "high":
            score += energy * 50
        elif task.get("priority") == "medium":
            score += energy * 30
        else:
            # Low priority tasks can use low energy times
            score += (1 - energy) * 20

        # Deadline proximity
        if "deadline" in task:
            try:
                deadline = datetime.fromisoformat(task["deadline"])
                hours_until_deadline = (deadline - slot.start_time).total_seconds() / 3600

                if hours_until_deadline < 0:
                    score += 100  # Overdue - schedule ASAP
                elif hours_until_deadline < 24:
                    score += 80  # Due soon
                elif hours_until_deadline < 72:
                    score += 50  # Due in a few days
            except (ValueError, KeyError):
                pass

        # Prefer earlier slots for high priority
        if task.get("priority") == "high":
            days_out = (slot.start_time - datetime.now()).days
            score += max(0, 20 - days_out * 2)

        # Duration fit (prefer slots that don't waste too much time)
        slot_duration = slot.duration_minutes
        if slot_duration >= duration and slot_duration < duration * 1.5:
            score += 10  # Good fit

        return score

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts"""
        conflicts = []

        for i, slot1 in enumerate(self.schedule):
            for slot2 in self.schedule[i + 1 :]:
                if slot1.overlaps(slot2):
                    conflicts.append(
                        {
                            "task1": slot1.task_id,
                            "task2": slot2.task_id,
                            "overlap_start": max(slot1.start_time, slot2.start_time).isoformat(),
                            "overlap_end": min(slot1.end_time, slot2.end_time).isoformat(),
                        }
                    )

        return conflicts

    def reschedule_task(self, task_id: str, new_time: datetime) -> Optional[Dict[str, Any]]:
        """Reschedule a specific task"""
        # Find the task in schedule
        for slot in self.schedule:
            if slot.task_id == task_id:
                duration = slot.duration_minutes

                # Create new slot
                new_slot = ScheduleSlot(
                    new_time, new_time + timedelta(minutes=duration), task_id, False
                )

                # Check for conflicts
                conflicts = [s for s in self.schedule if s != slot and s.overlaps(new_slot)]

                if conflicts:
                    self.logger.warning(f"Cannot reschedule {task_id}: conflicts detected")
                    return None

                # Update slot
                old_time = slot.start_time
                slot.start_time = new_time
                slot.end_time = new_slot.end_time

                self.logger.info(f"Rescheduled {task_id} from {old_time} to {new_time}")

                return {
                    "task_id": task_id,
                    "old_time": old_time.isoformat(),
                    "new_time": new_time.isoformat(),
                }

        return None

    def get_schedule_overview(self, days: int = 7) -> Dict[str, Any]:
        """Get schedule overview"""
        now = datetime.now()
        end_date = now + timedelta(days=days)

        upcoming = [
            s.to_dict()
            for s in self.schedule
            if now <= s.start_time <= end_date and not s.is_available
        ]

        return {
            "total_scheduled": len(upcoming),
            "schedule": sorted(upcoming, key=lambda s: s["start_time"]),
            "conflicts": self.detect_conflicts(),
        }


# Global instance
_auto_scheduler: Optional[AutoScheduler] = None


def get_auto_scheduler() -> AutoScheduler:
    """Get global auto-scheduler"""
    global _auto_scheduler
    if _auto_scheduler is None:
        _auto_scheduler = AutoScheduler()
    return _auto_scheduler
