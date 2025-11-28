"""
Demo: Natural Language Task Creation
Demonstrates NLP-based task parsing with smart date recognition and entity extraction
"""

import json
from datetime import datetime
from typing import Any, Dict, List

from src.core.logger import setup_logger
from src.nlp import get_date_parser, get_entity_extractor, get_priority_detector, get_task_parser

logger = setup_logger("demo.nlp")


def demo_date_parsing():
    """Demonstrate date parsing capabilities"""
    print("\n" + "=" * 70)
    print("DEMO: Date Parsing")
    print("=" * 70)

    date_parser = get_date_parser()

    test_phrases = [
        "tomorrow",
        "next week",
        "next Monday",
        "in 3 days",
        "January 15",
        "15 March",
        "12/25/2024",
        "end of week",
        "end of month",
        "this Friday",
    ]

    print("\n📅 Parsing date phrases:")
    for phrase in test_phrases:
        date = date_parser.parse_date(phrase)
        if date:
            print(f"   '{phrase}' → {date.strftime('%Y-%m-%d (%A)')}")
        else:
            print(f"   '{phrase}' → [not parsed]")

    # Extract date from full text
    print("\n📝 Extracting dates from full text:")
    test_texts = [
        "Complete the report tomorrow",
        "Meeting scheduled for next Monday at 2pm",
        "Review code by end of week",
        "Submit proposal on January 15",
    ]

    for text in test_texts:
        date, cleaned = date_parser.extract_date_from_text(text)
        if date:
            print(f"   '{text}'")
            print(f"   → Date: {date.strftime('%Y-%m-%d')}")
            print(f"   → Cleaned: '{cleaned}'")
        print()


def demo_priority_detection():
    """Demonstrate priority detection"""
    print("\n" + "=" * 70)
    print("DEMO: Priority Detection")
    print("=" * 70)

    priority_detector = get_priority_detector()

    test_texts = [
        "Fix critical bug in authentication!!!",
        "URGENT: Security vulnerability needs immediate attention",
        "Update documentation when you have time",
        "Important: Review pull requests asap",
        "Maybe reorganize the files later",
        "High priority task - complete today",
        "This is a normal task",
    ]

    print("\n🎯 Detecting priorities:")
    for text in test_texts:
        priority, cleaned = priority_detector.extract_priority_from_text(text)
        print(f"\n   '{text}'")
        print(f"   → Priority: {priority.upper()}")
        print(f"   → Cleaned: '{cleaned}'")


def demo_entity_extraction():
    """Demonstrate entity extraction"""
    print("\n" + "=" * 70)
    print("DEMO: Entity Extraction")
    print("=" * 70)

    entity_extractor = get_entity_extractor()

    test_texts = [
        "Email @john about the API documentation for #XENO project",
        "Schedule meeting with Sarah at Building A to discuss roadmap",
        "Review pull request at https://github.com/user/repo/pull/123",
        "Call client at 555-123-4567 regarding invoice",
        "Update README.md file with installation instructions",
        "Send report to john.doe@example.com by Friday",
    ]

    print("\n🔍 Extracting entities:")
    for text in test_texts:
        print(f"\n   '{text}'")
        entities = entity_extractor.extract_entities(text)

        for entity_type, values in entities.items():
            if values:
                print(f"   {entity_type}: {values}")

        # Extract specific entities
        assignee = entity_extractor.extract_assignee(text)
        if assignee:
            print(f"   → Assignee: {assignee}")

        category = entity_extractor.extract_category(text)
        print(f"   → Category: {category}")

        tags = entity_extractor.extract_tags(text)
        if tags:
            print(f"   → Tags: {tags}")


def demo_task_parsing():
    """Demonstrate full task parsing"""
    print("\n" + "=" * 70)
    print("DEMO: Task Parsing")
    print("=" * 70)

    task_parser = get_task_parser()

    test_tasks = [
        "Fix critical authentication bug tomorrow @john #security",
        "Schedule team meeting next Monday to discuss Q1 roadmap",
        "Update API documentation by end of week - high priority",
        "Review pull requests when you have time",
        "URGENT: Deploy hotfix today!!!",
        "Email client about project status on Friday",
        "Research new database optimization techniques for #XENO project",
        "Create presentation slides for demo next Wednesday @sarah",
    ]

    print("\n✨ Parsing natural language tasks:")
    for i, text in enumerate(test_tasks, 1):
        print(f"\n{i}. '{text}'")
        task_data = task_parser.parse(text)

        print(f"   📋 Parsed Task:")
        print(f"   - Title: {task_data['title']}")
        if task_data.get("description"):
            print(f"   - Description: {task_data['description']}")
        print(f"   - Priority: {task_data['priority']}")
        if task_data.get("due_date"):
            print(f"   - Due Date: {task_data['due_date']}")
        print(f"   - Category: {task_data['category']}")
        if task_data.get("assignee"):
            print(f"   - Assignee: {task_data['assignee']}")
        if task_data.get("tags"):
            print(f"   - Tags: {task_data['tags']}")
        if task_data.get("urls"):
            print(f"   - URLs: {task_data['urls']}")


def demo_bulk_parsing():
    """Demonstrate bulk task parsing"""
    print("\n" + "=" * 70)
    print("DEMO: Bulk Task Parsing")
    print("=" * 70)

    task_parser = get_task_parser()

    bulk_text = """
    - Fix login bug urgently
    - Update documentation tomorrow
    - Review code next week
    - Schedule meeting on Friday
    - Deploy to production end of month
    """

    print("\n📝 Bulk text:")
    print(bulk_text)

    tasks = task_parser.parse_bulk(bulk_text)

    print(f"\n✅ Parsed {len(tasks)} tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. {task['title']}")
        print(f"   Priority: {task['priority']}")
        if task.get("due_date"):
            print(f"   Due: {task['due_date']}")
        print(f"   Category: {task['category']}")


def demo_subtask_extraction():
    """Demonstrate subtask extraction"""
    print("\n" + "=" * 70)
    print("DEMO: Subtask Extraction")
    print("=" * 70)

    task_parser = get_task_parser()

    task_with_subtasks = """
    Complete XENO project documentation:
    1. Write API reference
    2. Create user guide
    3. Add code examples
    4. Review and publish
    """

    print("\n📝 Task with subtasks:")
    print(task_with_subtasks)

    subtasks = task_parser.extract_subtasks(task_with_subtasks)

    print(f"\n✅ Extracted {len(subtasks)} subtasks:")
    for subtask in subtasks:
        print(f"   {subtask['order']}. {subtask['text']}")


def demo_suggestions():
    """Demonstrate task improvement suggestions"""
    print("\n" + "=" * 70)
    print("DEMO: Task Improvement Suggestions")
    print("=" * 70)

    task_parser = get_task_parser()

    test_tasks = [
        "Fix bug",  # Minimal task
        "Complete report tomorrow @john - high priority",  # Well-formed task
        "Email client about project status next week for review #project",  # Complete task
    ]

    print("\n💡 Analyzing tasks for improvement:")
    for i, text in enumerate(test_tasks, 1):
        print(f"\n{i}. '{text}'")
        suggestions = task_parser.suggest_improvements(text)

        print(f"   ✓ Has priority: {suggestions['has_priority']}")
        print(f"   ✓ Has due date: {suggestions['has_due_date']}")
        print(f"   ✓ Has category: {suggestions['has_category']}")
        print(f"   ✓ Has assignee: {suggestions['has_assignee']}")

        if suggestions["improvements"]:
            print(f"   💡 Suggestions:")
            for suggestion in suggestions["improvements"]:
                print(f"      - {suggestion}")


def demo_complex_scenarios():
    """Demonstrate complex parsing scenarios"""
    print("\n" + "=" * 70)
    print("DEMO: Complex Scenarios")
    print("=" * 70)

    task_parser = get_task_parser()

    complex_tasks = [
        "CRITICAL: Fix authentication vulnerability at https://github.com/proj/repo/issues/42 - assign to @john - needs to be done today!!!",
        "Schedule quarterly review meeting with leadership team next Monday at 2pm in Conference Room A to discuss roadmap and budget #planning",
        "Update project documentation including API reference, user guide, and FAQ section - send to docs@company.com for review by end of week",
        "Research and implement database optimization for slow queries in reporting module - high priority for #XENO project - complete in 3 days",
    ]

    print("\n🚀 Parsing complex tasks:")
    for i, text in enumerate(complex_tasks, 1):
        print(f"\n{'='*70}")
        print(f"Task {i}:")
        print(f"'{text}'")
        print(f"{'-'*70}")

        task_data = task_parser.parse(text)

        print(f"\n📊 Complete Parse Result:")
        print(json.dumps(task_data, indent=2, default=str))


def demo_date_edge_cases():
    """Demonstrate edge cases in date parsing"""
    print("\n" + "=" * 70)
    print("DEMO: Date Parsing Edge Cases")
    print("=" * 70)

    date_parser = get_date_parser()

    edge_cases = [
        "in 2 weeks",
        "in 5 days",
        "this Thursday",
        "next month",
        "March 32",  # Invalid date
        "yesterday",
        "end of this week",
        "2/29/2024",  # Leap year
        "on Monday",
    ]

    print("\n🔍 Testing edge cases:")
    for phrase in edge_cases:
        date = date_parser.parse_date(phrase)
        if date:
            print(f"   ✓ '{phrase}' → {date.strftime('%Y-%m-%d (%A)')}")
        else:
            print(f"   ✗ '{phrase}' → [could not parse]")


def demo_performance():
    """Demonstrate parsing performance"""
    print("\n" + "=" * 70)
    print("DEMO: Performance Metrics")
    print("=" * 70)

    import time

    task_parser = get_task_parser()

    test_task = "Fix critical bug in authentication by tomorrow @john #security - high priority"

    # Single parse performance
    print("\n⏱️  Single task parsing:")
    start = time.time()
    for _ in range(100):
        task_parser.parse(test_task)
    elapsed = (time.time() - start) * 1000
    print(f"   100 parses: {elapsed:.2f}ms ({elapsed/100:.2f}ms per task)")

    # Bulk parse performance
    print("\n⏱️  Bulk task parsing:")
    bulk_tasks = "\n".join([f"- Task number {i}" for i in range(50)])
    start = time.time()
    tasks = task_parser.parse_bulk(bulk_tasks)
    elapsed = (time.time() - start) * 1000
    print(f"   50 tasks: {elapsed:.2f}ms ({elapsed/50:.2f}ms per task)")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("XENO NATURAL LANGUAGE TASK CREATION - COMPREHENSIVE DEMO")
    print("=" * 70)

    try:
        # Date parsing
        demo_date_parsing()

        # Priority detection
        demo_priority_detection()

        # Entity extraction
        demo_entity_extraction()

        # Task parsing
        demo_task_parsing()

        # Bulk parsing
        demo_bulk_parsing()

        # Subtask extraction
        demo_subtask_extraction()

        # Suggestions
        demo_suggestions()

        # Complex scenarios
        demo_complex_scenarios()

        # Edge cases
        demo_date_edge_cases()

        # Performance
        demo_performance()

        print("\n" + "=" * 70)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
