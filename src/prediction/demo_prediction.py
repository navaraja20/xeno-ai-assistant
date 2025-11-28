"""
Predictive Task Automation - Comprehensive Demo
Demonstrates pattern recognition, ML prediction, auto-scheduling, and suggestions
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.prediction import (
    get_auto_scheduler,
    get_pattern_engine,
    get_suggestion_system,
    get_task_predictor,
)


def generate_sample_tasks() -> List[Dict[str, Any]]:
    """Generate realistic task history"""
    tasks = []
    base_date = datetime.now() - timedelta(days=60)

    # Weekly standup (every Monday at 9 AM)
    for week in range(8):
        date = base_date + timedelta(weeks=week)
        # Move to Monday
        date = date - timedelta(days=date.weekday())
        date = date.replace(hour=9, minute=0)

        tasks.append(
            {
                "id": f"standup_{week}",
                "title": "Daily standup",
                "created_at": date.isoformat(),
                "priority": "high",
                "tags": ["meeting", "team"],
                "completed_at": (date + timedelta(hours=1)).isoformat(),
            }
        )

    # Weekly report (every Friday afternoon)
    for week in range(8):
        date = base_date + timedelta(weeks=week)
        # Move to Friday
        date = date + timedelta(days=(4 - date.weekday()))
        date = date.replace(hour=15, minute=0)

        tasks.append(
            {
                "id": f"report_{week}",
                "title": "Weekly progress report",
                "created_at": date.isoformat(),
                "priority": "medium",
                "tags": ["report", "weekly"],
                "completed_at": (date + timedelta(hours=2)).isoformat(),
            }
        )

    # Design review sequence (every 2 weeks)
    for iteration in range(4):
        base = base_date + timedelta(weeks=iteration * 2)

        # Design mockup
        date1 = base.replace(hour=10, minute=0)
        tasks.append(
            {
                "id": f"design_{iteration}_1",
                "title": "Design mockup",
                "created_at": date1.isoformat(),
                "priority": "medium",
                "tags": ["design"],
                "completed_at": (date1 + timedelta(hours=3)).isoformat(),
            }
        )

        # Review design (1 hour later)
        date2 = date1 + timedelta(minutes=30)
        tasks.append(
            {
                "id": f"design_{iteration}_2",
                "title": "Review design",
                "created_at": date2.isoformat(),
                "priority": "high",
                "tags": ["design", "review"],
                "completed_at": (date2 + timedelta(hours=1)).isoformat(),
            }
        )

        # Implement changes (1 hour later)
        date3 = date2 + timedelta(minutes=30)
        tasks.append(
            {
                "id": f"design_{iteration}_3",
                "title": "Implement changes",
                "created_at": date3.isoformat(),
                "priority": "high",
                "tags": ["design", "implementation"],
                "completed_at": (date3 + timedelta(hours=4)).isoformat(),
            }
        )

    # Daily email check (every weekday at 8 AM)
    for day in range(40):
        date = base_date + timedelta(days=day)
        if date.weekday() < 5:  # Weekdays only
            date = date.replace(hour=8, minute=0)
            tasks.append(
                {
                    "id": f"email_{day}",
                    "title": "Check emails",
                    "created_at": date.isoformat(),
                    "priority": "low",
                    "tags": ["email", "routine"],
                    "completed_at": (date + timedelta(minutes=30)).isoformat(),
                }
            )

    # Monthly planning (first Monday of month)
    for month in range(2):
        date = base_date + timedelta(days=month * 30)
        # Find first Monday
        while date.weekday() != 0:
            date += timedelta(days=1)
        date = date.replace(hour=14, minute=0)

        tasks.append(
            {
                "id": f"planning_{month}",
                "title": "Monthly planning session",
                "created_at": date.isoformat(),
                "priority": "high",
                "tags": ["planning", "monthly"],
                "completed_at": (date + timedelta(hours=2)).isoformat(),
            }
        )

    return tasks


def demo_pattern_recognition():
    """Demo 1: Pattern Recognition"""
    print("\n" + "=" * 60)
    print("DEMO 1: Pattern Recognition")
    print("=" * 60)

    # Get pattern engine
    engine = get_pattern_engine()

    # Generate sample tasks
    tasks = generate_sample_tasks()
    print(f"\n📊 Analyzing {len(tasks)} historical tasks...")

    # Analyze patterns
    patterns = engine.analyze_task_history(tasks)
    print(f"✅ Detected {len(patterns)} patterns\n")

    # Show pattern insights
    insights = engine.get_pattern_insights()
    print(f"Pattern Breakdown:")
    for pattern_type, count in insights.get("pattern_types", {}).items():
        print(f"  • {pattern_type}: {count}")

    # Show high-confidence patterns
    print(f"\n🎯 High-Confidence Patterns (≥0.7):")
    for pattern in insights.get("high_confidence_patterns", []):
        print(f"  • {pattern['description']}")
        print(f"    Confidence: {pattern['confidence']:.2f}, Frequency: {pattern['frequency']}")

    # Get predictions
    print(f"\n🔮 Predictions for next 24 hours:")
    predictions = engine.predict_next_tasks()
    for pred in predictions[:5]:
        print(f"  • {pred.get('description', 'Unknown task')}")
        print(
            f"    Probability: {pred.get('probability', 0):.2f}, Expected: {pred.get('expected_time', 'N/A')}"
        )


def demo_task_prediction():
    """Demo 2: ML-based Task Prediction"""
    print("\n" + "=" * 60)
    print("DEMO 2: ML-Based Task Prediction")
    print("=" * 60)

    # Get predictor
    predictor = get_task_predictor()

    # Train on historical data
    tasks = generate_sample_tasks()
    print(f"\n🧠 Training predictor on {len(tasks)} tasks...")
    predictor.train(tasks)

    # Show learned templates
    print(f"✅ Learned {len(predictor.task_templates)} task templates\n")
    print("📋 Task Templates:")
    for title, template in list(predictor.task_templates.items())[:5]:
        print(f"  • {title}")
        print(f"    Occurrences: {template['count']}, Priority: {template['avg_priority']}")
        if template.get("typical_duration"):
            print(f"    Avg Duration: {template['typical_duration']:.1f} minutes")

    # Make predictions
    print(f"\n🔮 Predictions for current context:")
    context = {
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().weekday(),
    }
    predictions = predictor.predict_tasks(context, max_predictions=5)

    for pred in predictions:
        print(f"  • {pred['title']}")
        print(f"    Probability: {pred['probability']:.2f}, Priority: {pred['priority']}")
        print(f"    Reason: {pred['reason']}")

    # Test accuracy
    print(f"\n📊 Prediction Accuracy:")
    test_tasks = [
        {"title": "Daily standup"},
        {"title": "Check emails"},
        {"title": "Weekly progress report"},
    ]
    accuracy = predictor.get_prediction_accuracy(test_tasks)
    print(f"  Precision: {accuracy['precision']:.2%}")
    print(f"  Recall: {accuracy['recall']:.2%}")
    print(f"  F1-Score: {accuracy['accuracy']:.2%}")


def demo_auto_scheduling():
    """Demo 3: Auto-Scheduling"""
    print("\n" + "=" * 60)
    print("DEMO 3: Auto-Scheduling")
    print("=" * 60)

    # Get scheduler
    scheduler = get_auto_scheduler()

    # Configure work hours
    scheduler.set_work_hours(9, 17)
    print(f"\n⚙️  Work hours: 9:00 AM - 5:00 PM")

    # Create tasks to schedule
    tasks_to_schedule = [
        {
            "id": "task1",
            "title": "High priority urgent task",
            "priority": "high",
            "estimated_duration": 120,  # 2 hours
            "deadline": (datetime.now() + timedelta(hours=4)).isoformat(),
        },
        {
            "id": "task2",
            "title": "Medium priority task",
            "priority": "medium",
            "estimated_duration": 60,
        },
        {
            "id": "task3",
            "title": "Quick low priority task",
            "priority": "low",
            "estimated_duration": 15,
        },
        {
            "id": "task4",
            "title": "Important meeting prep",
            "priority": "high",
            "estimated_duration": 45,
            "deadline": (datetime.now() + timedelta(days=1)).isoformat(),
        },
        {
            "id": "task5",
            "title": "Code review",
            "priority": "medium",
            "estimated_duration": 90,
        },
    ]

    print(f"\n📅 Scheduling {len(tasks_to_schedule)} tasks...")
    scheduled = scheduler.schedule_tasks(tasks_to_schedule, days=3)

    print(f"✅ Successfully scheduled {len(scheduled)} tasks\n")
    print("📋 Schedule:")
    for item in scheduled:
        task = item["task"]
        print(f"  • {task['title']}")
        print(f"    Time: {item['scheduled_time']}")
        print(f"    Duration: {item['duration_minutes']:.0f} min")
        print(f"    Energy Level: {item['energy_level']:.2f}")

    # Check for conflicts
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print(f"\n⚠️  Detected {len(conflicts)} conflicts")
    else:
        print(f"\n✅ No scheduling conflicts")

    # Get schedule overview
    overview = scheduler.get_schedule_overview(days=7)
    print(f"\n📊 7-Day Overview:")
    print(f"  Total scheduled: {overview['total_scheduled']} tasks")


def demo_suggestions():
    """Demo 4: Proactive Suggestions"""
    print("\n" + "=" * 60)
    print("DEMO 4: Proactive Task Suggestions")
    print("=" * 60)

    # Get suggestion system
    suggestions = get_suggestion_system()

    # Train predictor and pattern engine first
    tasks = generate_sample_tasks()
    get_task_predictor().train(tasks)
    get_pattern_engine().analyze_task_history(tasks)

    # Generate suggestions
    context = {
        "recent_completed_count": 3,
        "overdue_count": 0,
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().weekday(),
    }

    print(f"\n🤖 Generating suggestions...")
    active_suggestions = suggestions.generate_suggestions(context)

    print(f"✅ Generated {len(active_suggestions)} suggestions\n")
    print("💡 Suggestions:")
    for i, suggestion in enumerate(active_suggestions[:7], 1):
        print(f"  {i}. {suggestion.title}")
        print(f"     Confidence: {suggestion.confidence:.2f}, Priority: {suggestion.priority}")
        print(f"     Reason: {suggestion.reason}")
        print(f"     Source: {suggestion.source}")

    # Simulate user feedback
    print(f"\n👤 User Feedback Simulation:")
    if active_suggestions:
        # Accept first suggestion
        accepted = active_suggestions[0]
        suggestions.accept_suggestion(accepted.title)
        print(f"  ✅ Accepted: {accepted.title}")

        # Reject second suggestion
        if len(active_suggestions) > 1:
            rejected = active_suggestions[1]
            suggestions.reject_suggestion(rejected.title)
            print(f"  ❌ Rejected: {rejected.title}")

    # Show stats
    stats = suggestions.get_suggestion_stats()
    print(f"\n📊 Suggestion Statistics:")
    print(f"  Total suggestions: {stats['total_suggestions']}")
    print(f"  Acceptance rate: {stats['acceptance_rate']:.1%}")
    print(f"  Rejection rate: {stats['rejection_rate']:.1%}")


def demo_integrated_workflow():
    """Demo 5: Integrated Predictive Workflow"""
    print("\n" + "=" * 60)
    print("DEMO 5: Integrated Predictive Workflow")
    print("=" * 60)

    print("\n🔄 Complete predictive automation workflow:\n")

    # Step 1: Analyze historical data
    print("1️⃣  Analyzing historical patterns...")
    tasks = generate_sample_tasks()
    pattern_engine = get_pattern_engine()
    patterns = pattern_engine.analyze_task_history(tasks)
    print(f"   ✅ Detected {len(patterns)} patterns")

    # Step 2: Train predictor
    print("\n2️⃣  Training ML predictor...")
    predictor = get_task_predictor()
    predictor.train(tasks)
    print(f"   ✅ Learned {len(predictor.task_templates)} task templates")

    # Step 3: Generate suggestions
    print("\n3️⃣  Generating task suggestions...")
    suggestion_system = get_suggestion_system()
    active_suggestions = suggestion_system.generate_suggestions()
    print(f"   ✅ Generated {len(active_suggestions)} suggestions")

    # Step 4: Auto-schedule predicted tasks
    print("\n4️⃣  Auto-scheduling predicted tasks...")
    predicted_tasks = predictor.predict_tasks(max_predictions=5)

    # Convert predictions to schedulable tasks
    tasks_to_schedule = []
    for pred in predicted_tasks:
        tasks_to_schedule.append(
            {
                "id": pred["title"].replace(" ", "_"),
                "title": pred["title"],
                "priority": pred["priority"],
                "estimated_duration": pred.get("estimated_duration", 60),
            }
        )

    scheduler = get_auto_scheduler()
    scheduled = scheduler.schedule_tasks(tasks_to_schedule, days=2)
    print(f"   ✅ Scheduled {len(scheduled)} tasks")

    # Step 5: Show integrated results
    print("\n5️⃣  Integrated Results:")
    print("\n   📅 Next 24 Hours Schedule:")
    for item in scheduled[:3]:
        task = item["task"]
        print(f"     • {task['title']} at {item['scheduled_time'][:16]}")

    print("\n   💡 Active Suggestions:")
    for suggestion in active_suggestions[:3]:
        print(f"     • {suggestion.title} (confidence: {suggestion.confidence:.2f})")

    print("\n   🎯 High-Priority Patterns:")
    insights = pattern_engine.get_pattern_insights()
    for pattern in insights.get("high_confidence_patterns", [])[:3]:
        print(f"     • {pattern['description']}")


def demo_performance_metrics():
    """Demo 6: Performance Metrics"""
    print("\n" + "=" * 60)
    print("DEMO 6: Performance Metrics")
    print("=" * 60)

    tasks = generate_sample_tasks()

    # Pattern recognition metrics
    print("\n📊 Pattern Recognition Performance:")
    pattern_engine = get_pattern_engine()
    patterns = pattern_engine.analyze_task_history(tasks)

    pattern_types = {}
    for pattern in patterns.values():
        ptype = pattern.pattern_type
        pattern_types[ptype] = pattern_types.get(ptype, 0) + 1

    for ptype, count in pattern_types.items():
        print(f"  • {ptype}: {count} patterns")

    # Prediction accuracy
    print("\n📊 Prediction Accuracy:")
    predictor = get_task_predictor()
    predictor.train(tasks)

    test_tasks = [
        {"title": "Daily standup"},
        {"title": "Check emails"},
        {"title": "Weekly progress report"},
        {"title": "Random unknown task"},
    ]

    accuracy = predictor.get_prediction_accuracy(test_tasks)
    print(f"  Precision: {accuracy['precision']:.1%}")
    print(f"  Recall: {accuracy['recall']:.1%}")
    print(f"  F1-Score: {accuracy['accuracy']:.1%}")
    print(f"  True Positives: {accuracy['true_positives']}")
    print(f"  False Positives: {accuracy['false_positives']}")

    # Scheduling efficiency
    print("\n📊 Scheduling Efficiency:")
    scheduler = get_auto_scheduler()
    tasks_to_schedule = [
        {"id": f"task{i}", "title": f"Task {i}", "priority": "medium", "estimated_duration": 60}
        for i in range(10)
    ]

    scheduled = scheduler.schedule_tasks(tasks_to_schedule, days=2)
    efficiency = len(scheduled) / len(tasks_to_schedule) if tasks_to_schedule else 0

    print(f"  Scheduled: {len(scheduled)}/{len(tasks_to_schedule)} tasks")
    print(f"  Efficiency: {efficiency:.1%}")

    # Suggestion acceptance
    print("\n📊 Suggestion System:")
    suggestion_system = get_suggestion_system()
    stats = suggestion_system.get_suggestion_stats()

    print(f"  Total suggestions: {stats['total_suggestions']}")
    print(f"  Active suggestions: {stats['active_suggestions']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🚀 PREDICTIVE TASK AUTOMATION - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("\nDemonstrating:")
    print("  • Pattern Recognition")
    print("  • ML-Based Task Prediction")
    print("  • Auto-Scheduling")
    print("  • Proactive Suggestions")
    print("  • Integrated Workflow")
    print("  • Performance Metrics")

    # Run demos
    demo_pattern_recognition()
    demo_task_prediction()
    demo_auto_scheduling()
    demo_suggestions()
    demo_integrated_workflow()
    demo_performance_metrics()

    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
