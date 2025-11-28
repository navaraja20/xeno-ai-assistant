"""
Demo: Smart Tags & Organization
Demonstrates hierarchical tags, ML suggestions, and auto-tagging
"""

import time
from typing import Any, Dict, List

from src.core.logger import setup_logger
from src.tags import (
    get_tag_hierarchy,
    get_tag_suggestion_engine,
    get_auto_tagger,
    get_tag_analytics,
)


logger = setup_logger("demo.tags")


def create_sample_tag_hierarchy():
    """Create a sample tag hierarchy"""
    hierarchy = get_tag_hierarchy()

    # Clear existing tags for demo
    hierarchy.tags.clear()

    # Create root categories
    work = hierarchy.create_tag("Work", color="#3498db", icon="💼")
    personal = hierarchy.create_tag("Personal", color="#2ecc71", icon="🏠")
    learning = hierarchy.create_tag("Learning", color="#9b59b6", icon="📚")

    # Work subcategories
    projects = hierarchy.create_tag(
        "Projects", parent_id=work.id, color="#2980b9", icon="📁"
    )
    meetings = hierarchy.create_tag(
        "Meetings", parent_id=work.id, color="#3498db", icon="📅"
    )
    tasks = hierarchy.create_tag(
        "Tasks", parent_id=work.id, color="#5dade2", icon="✓"
    )

    # Project subcategories
    xeno = hierarchy.create_tag(
        "XENO", parent_id=projects.id, color="#1abc9c", icon="🚀"
    )
    client_work = hierarchy.create_tag(
        "Client Work", parent_id=projects.id, color="#16a085", icon="👥"
    )

    # XENO specific tags
    hierarchy.create_tag("Frontend", parent_id=xeno.id, color="#f39c12", icon="🎨")
    hierarchy.create_tag("Backend", parent_id=xeno.id, color="#d35400", icon="⚙️")
    hierarchy.create_tag("Database", parent_id=xeno.id, color="#c0392b", icon="🗄️")

    # Personal subcategories
    health = hierarchy.create_tag(
        "Health", parent_id=personal.id, color="#27ae60", icon="💪"
    )
    finance = hierarchy.create_tag(
        "Finance", parent_id=personal.id, color="#2ecc71", icon="💰"
    )
    home = hierarchy.create_tag(
        "Home", parent_id=personal.id, color="#1abc9c", icon="🏡"
    )

    # Learning subcategories
    courses = hierarchy.create_tag(
        "Courses", parent_id=learning.id, color="#8e44ad", icon="🎓"
    )
    books = hierarchy.create_tag(
        "Books", parent_id=learning.id, color="#9b59b6", icon="📖"
    )
    tutorials = hierarchy.create_tag(
        "Tutorials", parent_id=learning.id, color="#a569bd", icon="🎬"
    )

    # Additional standalone tags
    hierarchy.create_tag("Urgent", color="#e74c3c", icon="⚡")
    hierarchy.create_tag("Important", color="#c0392b", icon="⭐")
    hierarchy.create_tag("Bug", color="#e67e22", icon="🐛")
    hierarchy.create_tag("Feature", color="#f39c12", icon="✨")
    hierarchy.create_tag("Documentation", color="#95a5a6", icon="📝")

    logger.info(f"Created tag hierarchy with {len(hierarchy.tags)} tags")
    return hierarchy


def demo_tag_hierarchy():
    """Demonstrate tag hierarchy"""
    print("\n" + "=" * 70)
    print("DEMO: Tag Hierarchy")
    print("=" * 70)

    hierarchy = create_sample_tag_hierarchy()

    # 1. List root tags
    print("\n1️⃣ ROOT TAGS")
    root_tags = hierarchy.get_root_tags()
    print(f"   Found {len(root_tags)} root tags:")
    for tag in root_tags:
        print(f"   {tag.icon} {tag.name} (ID: {tag.id})")

    # 2. Show hierarchy
    print("\n2️⃣ TAG HIERARCHY")

    def print_tag_tree(tag, indent=0):
        """Print tag tree recursively"""
        prefix = "   " * indent
        print(f"{prefix}{tag.icon} {tag.name} - {hierarchy.get_path(tag.id)}")

        children = hierarchy.get_children(tag.id)
        for child in children:
            print_tag_tree(child, indent + 1)

    for root in root_tags[:3]:  # Show first 3 root categories
        print_tag_tree(root)

    # 3. Tag operations
    print("\n3️⃣ TAG OPERATIONS")

    work_tag = hierarchy.get_tag_by_name("Work")
    if work_tag:
        children = hierarchy.get_children(work_tag.id, recursive=True)
        print(f"   'Work' has {len(children)} total descendants")

        ancestors = hierarchy.get_ancestors(work_tag.id)
        print(f"   'Work' has {len(ancestors)} ancestors")

    xeno_tag = hierarchy.get_tag_by_name("XENO")
    if xeno_tag:
        path = hierarchy.get_path(xeno_tag.id)
        print(f"   'XENO' path: {path}")

        children = hierarchy.get_children(xeno_tag.id)
        print(f"   'XENO' children: {[c.name for c in children]}")

    # 4. Search tags
    print("\n4️⃣ TAG SEARCH")
    results = hierarchy.search_tags("work")
    print(f"   Search 'work': {[tag.name for tag in results]}")

    results = hierarchy.search_tags("learn")
    print(f"   Search 'learn': {[tag.name for tag in results]}")


def create_sample_tasks() -> List[Dict[str, Any]]:
    """Create sample tasks for tagging"""
    return [
        {
            "id": "task_1",
            "title": "Fix critical authentication bug",
            "description": "Users are experiencing login failures due to security vulnerability",
            "priority": "critical",
            "category": "Bug Fix",
        },
        {
            "id": "task_2",
            "title": "Implement new search feature",
            "description": "Add advanced search with filters and fuzzy matching",
            "priority": "high",
            "category": "Feature",
        },
        {
            "id": "task_3",
            "title": "Update API documentation",
            "description": "Document new endpoints and update examples",
            "priority": "medium",
            "category": "Documentation",
        },
        {
            "id": "task_4",
            "title": "Weekly team meeting",
            "description": "Discuss project progress and upcoming tasks",
            "priority": "low",
            "category": "Meeting",
        },
        {
            "id": "task_5",
            "title": "Optimize database queries",
            "description": "Improve performance of slow queries in reporting module",
            "priority": "high",
            "category": "Performance",
        },
        {
            "id": "task_6",
            "title": "Read Python best practices book",
            "description": "Continue reading chapter on design patterns",
            "priority": "low",
            "category": "Learning",
        },
        {
            "id": "task_7",
            "title": "Security audit preparation",
            "description": "Prepare documentation and fix security issues before audit",
            "priority": "critical",
            "category": "Security",
        },
        {
            "id": "task_8",
            "title": "Review pull requests",
            "description": "Review and provide feedback on team member PRs",
            "priority": "medium",
            "category": "Code Review",
        },
    ]


def demo_auto_tagging():
    """Demonstrate automatic tagging"""
    print("\n" + "=" * 70)
    print("DEMO: Auto-Tagging")
    print("=" * 70)

    auto_tagger = get_auto_tagger()
    tasks = create_sample_tasks()

    for i, task in enumerate(tasks[:5], 1):
        print(f"\n{i}️⃣ TASK: {task['title']}")
        print(f"   Category: {task['category']}")
        print(f"   Priority: {task['priority']}")

        # Get auto-tag suggestions
        suggestions = auto_tagger.auto_tag(task, min_confidence=0.7)

        print(f"   Auto-tag suggestions:")
        for tag, confidence in suggestions[:5]:
            print(f"   - {tag} ({confidence:.0%} confidence)")


def demo_tag_suggestions():
    """Demonstrate tag suggestions"""
    print("\n" + "=" * 70)
    print("DEMO: ML-Based Tag Suggestions")
    print("=" * 70)

    engine = get_tag_suggestion_engine()
    tasks = create_sample_tasks()

    # Train the engine with some examples
    print("\n1️⃣ TRAINING SUGGESTION ENGINE")
    training_data = [
        (tasks[0], ["bug", "security", "urgent", "critical"]),
        (tasks[1], ["feature", "search", "enhancement"]),
        (tasks[2], ["documentation", "api", "work"]),
        (tasks[3], ["meeting", "team", "work"]),
        (tasks[4], ["performance", "database", "optimization"]),
    ]

    for task, tags in training_data:
        engine.learn_from_item(task, tags)
        print(f"   ✓ Learned: {task['title'][:40]}... → {tags}")

    # Get suggestions for new tasks
    print("\n2️⃣ GETTING SUGGESTIONS FOR NEW TASKS")

    new_task = {
        "id": "task_new",
        "title": "Fix security vulnerability in authentication",
        "description": "Critical bug allowing unauthorized access",
        "priority": "critical",
    }

    print(f"\n   Task: {new_task['title']}")
    suggestions = engine.suggest_tags(new_task, existing_tags=[], limit=5)
    print(f"   Suggestions:")
    for tag, score in suggestions:
        print(f"   - {tag} (score: {score:.2f})")

    # Autocomplete
    print("\n3️⃣ TAG NAME AUTOCOMPLETE")
    prefixes = ["sec", "bug", "doc"]
    for prefix in prefixes:
        suggestions = engine.suggest_tag_names(prefix, limit=5)
        print(f"   '{prefix}' → {suggestions}")


def demo_tag_analytics():
    """Demonstrate tag analytics"""
    print("\n" + "=" * 70)
    print("DEMO: Tag Analytics")
    print("=" * 70)

    hierarchy = get_tag_hierarchy()
    analytics = get_tag_analytics()

    # Simulate some usage
    print("\n1️⃣ SIMULATING TAG USAGE")
    tasks = create_sample_tasks()

    usage_patterns = [
        ("bug", ["task_1", "task_7"]),
        ("security", ["task_1", "task_7"]),
        ("feature", ["task_2"]),
        ("documentation", ["task_3"]),
        ("meeting", ["task_4"]),
        ("performance", ["task_5"]),
        ("urgent", ["task_1", "task_7"]),
    ]

    for tag_name, item_ids in usage_patterns:
        tag = hierarchy.get_tag_by_name(tag_name)
        if tag:
            for item_id in item_ids:
                analytics.record_tag_usage(tag.id, item_id)
                # Simulate multiple uses
                for _ in range(2):
                    analytics.record_tag_usage(tag.id, item_id)

    print(f"   ✓ Simulated usage for {len(usage_patterns)} tags")

    # Coverage statistics
    print("\n2️⃣ COVERAGE STATISTICS")
    coverage = analytics.get_coverage_statistics()
    print(f"   Total tags: {coverage['total_tags']}")
    print(f"   Used tags: {coverage['used_tags']}")
    print(f"   Unused tags: {coverage['unused_tags']}")
    print(f"   Usage rate: {coverage['usage_rate']:.1f}%")
    print(f"   Root tags: {coverage['root_tags']}")
    print(f"   Max depth: {coverage['max_depth']}")

    # Top tags
    print("\n3️⃣ TOP USED TAGS")
    top_tags = analytics.get_top_tags(limit=10)
    for i, (tag_name, count) in enumerate(top_tags, 1):
        print(f"   {i}. {tag_name}: {count} uses")

    # Tag statistics
    print("\n4️⃣ TAG STATISTICS")
    bug_tag = hierarchy.get_tag_by_name("bug")
    if bug_tag:
        stats = analytics.get_tag_statistics(bug_tag.id)
        print(f"\n   Tag: {stats['tag_name']}")
        print(f"   Path: {stats['path']}")
        print(f"   Total usage: {stats['total_usage']}")
        print(f"   Depth: {stats['depth']}")

        # Co-occurrences
        co_occur = analytics.get_tag_co_occurrences(bug_tag.id, limit=5)
        if co_occur:
            print(f"   Often used with:")
            for other_tag, count in co_occur:
                print(f"   - {other_tag} ({count} times)")

    # Distribution
    print("\n5️⃣ TAG DISTRIBUTION BY LEVEL")
    distribution = analytics.get_tag_distribution()
    for level, count in sorted(distribution.items()):
        print(f"   {level}: {count} tags")


def demo_tag_organization():
    """Demonstrate tag organization features"""
    print("\n" + "=" * 70)
    print("DEMO: Tag Organization")
    print("=" * 70)

    hierarchy = get_tag_hierarchy()

    # 1. Create project-specific tags
    print("\n1️⃣ CREATING PROJECT TAGS")

    xeno_tag = hierarchy.get_tag_by_name("XENO")
    if xeno_tag:
        sprint1 = hierarchy.create_tag(
            "Sprint 1", parent_id=xeno_tag.id, color="#e74c3c"
        )
        sprint2 = hierarchy.create_tag(
            "Sprint 2", parent_id=xeno_tag.id, color="#3498db"
        )

        print(f"   Created: {sprint1.name} under XENO")
        print(f"   Created: {sprint2.name} under XENO")

    # 2. Move tags
    print("\n2️⃣ MOVING TAGS")

    bug_tag = hierarchy.get_tag_by_name("Bug")
    work_tag = hierarchy.get_tag_by_name("Work")

    if bug_tag and work_tag:
        print(f"   Original path: {hierarchy.get_path(bug_tag.id)}")
        hierarchy.move_tag(bug_tag.id, work_tag.id)
        print(f"   New path: {hierarchy.get_path(bug_tag.id)}")

    # 3. Update tag properties
    print("\n3️⃣ UPDATING TAG PROPERTIES")

    urgent_tag = hierarchy.get_tag_by_name("Urgent")
    if urgent_tag:
        hierarchy.update_tag(
            urgent_tag.id,
            description="Tasks requiring immediate attention",
            metadata={"severity": "high", "notify": True},
        )
        print(f"   Updated: {urgent_tag.name}")
        print(f"   Description: {urgent_tag.description}")
        print(f"   Metadata: {urgent_tag.metadata}")

    # 4. Popular tags
    print("\n4️⃣ POPULAR TAGS")
    popular = hierarchy.get_popular_tags(limit=5)
    for tag in popular:
        print(f"   {tag.icon} {tag.name} - used {tag.usage_count} times")


def demo_performance():
    """Demonstrate tagging performance"""
    print("\n" + "=" * 70)
    print("DEMO: Performance Metrics")
    print("=" * 70)

    hierarchy = get_tag_hierarchy()
    auto_tagger = get_auto_tagger()
    tasks = create_sample_tasks()

    # 1. Tag lookup performance
    print("\n1️⃣ TAG LOOKUP PERFORMANCE")
    iterations = 1000

    start_time = time.time()
    for _ in range(iterations):
        hierarchy.get_tag_by_name("Work")
    elapsed = (time.time() - start_time) * 1000
    print(f"   {iterations} lookups: {elapsed:.2f}ms ({elapsed/iterations:.3f}ms each)")

    # 2. Auto-tagging performance
    print("\n2️⃣ AUTO-TAGGING PERFORMANCE")

    start_time = time.time()
    for task in tasks:
        auto_tagger.auto_tag(task)
    elapsed = (time.time() - start_time) * 1000
    print(f"   {len(tasks)} tasks: {elapsed:.2f}ms ({elapsed/len(tasks):.2f}ms per task)")

    # 3. Hierarchy traversal performance
    print("\n3️⃣ HIERARCHY TRAVERSAL PERFORMANCE")

    work_tag = hierarchy.get_tag_by_name("Work")
    if work_tag:
        start_time = time.time()
        for _ in range(iterations):
            hierarchy.get_children(work_tag.id, recursive=True)
        elapsed = (time.time() - start_time) * 1000
        print(
            f"   {iterations} recursive lookups: {elapsed:.2f}ms ({elapsed/iterations:.3f}ms each)"
        )


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("XENO SMART TAGS & ORGANIZATION - COMPREHENSIVE DEMO")
    print("=" * 70)

    try:
        # Tag hierarchy
        demo_tag_hierarchy()

        # Auto-tagging
        demo_auto_tagging()

        # Tag suggestions
        demo_tag_suggestions()

        # Tag analytics
        demo_tag_analytics()

        # Tag organization
        demo_tag_organization()

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
