"""
Demo: Advanced Search & Filters
Demonstrates search engine capabilities with saved searches and history tracking
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.core.logger import setup_logger
from src.search import (
    get_search_engine,
    get_saved_search_manager,
    get_search_history_tracker,
    SearchQuery,
    SearchMode,
    SearchField,
    SearchFilter,
)


logger = setup_logger("demo.search")


def create_sample_tasks() -> List[Dict[str, Any]]:
    """Create sample tasks for demonstration"""
    return [
        {
            "id": "task_1",
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the XENO project including API references and user guides",
            "priority": "high",
            "status": "in_progress",
            "category": "Development",
            "tags": ["documentation", "project", "important"],
            "due_date": "2024-01-15",
        },
        {
            "id": "task_2",
            "title": "Review pull requests",
            "description": "Review and merge pending pull requests from team members",
            "priority": "medium",
            "status": "pending",
            "category": "Code Review",
            "tags": ["review", "team", "code"],
            "due_date": "2024-01-10",
        },
        {
            "id": "task_3",
            "title": "Fix critical bug in authentication",
            "description": "Urgent bug causing authentication failures for some users",
            "priority": "critical",
            "status": "in_progress",
            "category": "Bug Fix",
            "tags": ["bug", "critical", "authentication", "security"],
            "due_date": "2024-01-08",
        },
        {
            "id": "task_4",
            "title": "Prepare quarterly presentation",
            "description": "Create slides and prepare presentation for Q1 review meeting",
            "priority": "high",
            "status": "not_started",
            "category": "Meetings",
            "tags": ["presentation", "meeting", "quarterly"],
            "due_date": "2024-01-20",
        },
        {
            "id": "task_5",
            "title": "Update dependencies",
            "description": "Update all project dependencies to latest stable versions",
            "priority": "low",
            "status": "not_started",
            "category": "Maintenance",
            "tags": ["dependencies", "maintenance", "upgrade"],
            "due_date": "2024-01-25",
        },
        {
            "id": "task_6",
            "title": "Implement user feedback",
            "description": "Review and implement user feedback from recent survey",
            "priority": "medium",
            "status": "pending",
            "category": "Feature",
            "tags": ["feedback", "users", "improvement"],
            "due_date": "2024-01-18",
        },
        {
            "id": "task_7",
            "title": "Database optimization",
            "description": "Optimize database queries and add necessary indexes for better performance",
            "priority": "high",
            "status": "in_progress",
            "category": "Performance",
            "tags": ["database", "optimization", "performance"],
            "due_date": "2024-01-12",
        },
        {
            "id": "task_8",
            "title": "Security audit",
            "description": "Conduct comprehensive security audit of the application",
            "priority": "critical",
            "status": "not_started",
            "category": "Security",
            "tags": ["security", "audit", "compliance"],
            "due_date": "2024-01-30",
        },
        {
            "id": "task_9",
            "title": "Team training session",
            "description": "Organize training session on new features for the team",
            "priority": "low",
            "status": "pending",
            "category": "Training",
            "tags": ["training", "team", "knowledge"],
            "due_date": "2024-02-01",
        },
        {
            "id": "task_10",
            "title": "API documentation update",
            "description": "Update API documentation with recent endpoint changes",
            "priority": "medium",
            "status": "in_progress",
            "category": "Documentation",
            "tags": ["api", "documentation", "update"],
            "due_date": "2024-01-16",
        },
    ]


def demo_basic_search():
    """Demonstrate basic search functionality"""
    print("\n" + "=" * 70)
    print("DEMO: Basic Search Functionality")
    print("=" * 70)

    engine = get_search_engine()
    tasks = create_sample_tasks()

    # Index tasks
    print("\n📚 Indexing sample tasks...")
    for task in tasks:
        engine.index_item(task["id"], task)
    print(f"✓ Indexed {len(tasks)} tasks")

    # 1. Exact search
    print("\n1️⃣ EXACT SEARCH - Find 'documentation'")
    query = SearchQuery(query="documentation", mode=SearchMode.EXACT)
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - {result.item['title']} (Score: {result.score:.2f})")

    # 2. Partial search
    print("\n2️⃣ PARTIAL SEARCH - Find tasks with 'auth'")
    query = SearchQuery(query="auth", mode=SearchMode.PARTIAL)
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - {result.item['title']} (Score: {result.score:.2f})")
        if result.highlights:
            print(f"     Highlights: {result.highlights}")

    # 3. Fuzzy search
    print("\n3️⃣ FUZZY SEARCH - Find 'documantation' (typo)")
    query = SearchQuery(query="documantation", mode=SearchMode.FUZZY)
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results[:3]:
        print(f"   - {result.item['title']} (Score: {result.score:.2f})")

    # 4. Regex search
    print("\n4️⃣ REGEX SEARCH - Find tasks starting with 'Update'")
    query = SearchQuery(query=r"^Update", mode=SearchMode.REGEX)
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - {result.item['title']}")

    # 5. Semantic search
    print("\n5️⃣ SEMANTIC SEARCH - Find 'bug fix security'")
    query = SearchQuery(query="bug fix security", mode=SearchMode.SEMANTIC)
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results[:5]:
        print(f"   - {result.item['title']} (Score: {result.score:.2f})")


def demo_advanced_filtering():
    """Demonstrate advanced filtering"""
    print("\n" + "=" * 70)
    print("DEMO: Advanced Filtering")
    print("=" * 70)

    engine = get_search_engine()

    # 1. Filter by priority
    print("\n1️⃣ FILTER - High priority tasks")
    query = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.PRIORITY, "eq", "high")],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} high priority tasks:")
    for result in results:
        print(f"   - {result.item['title']} (Priority: {result.item['priority']})")

    # 2. Filter by status
    print("\n2️⃣ FILTER - In progress tasks")
    query = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.STATUS, "eq", "in_progress")],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} in-progress tasks:")
    for result in results:
        print(f"   - {result.item['title']}")

    # 3. Multiple filters
    print("\n3️⃣ MULTIPLE FILTERS - Critical tasks in progress")
    query = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[
            SearchFilter(SearchField.PRIORITY, "eq", "critical"),
            SearchFilter(SearchField.STATUS, "eq", "in_progress"),
        ],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} critical in-progress tasks:")
    for result in results:
        print(f"   - {result.item['title']}")

    # 4. Tag contains filter
    print("\n4️⃣ TAG FILTER - Tasks tagged with 'security'")
    query = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.TAGS, "contains", "security")],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} security-related tasks:")
    for result in results:
        print(f"   - {result.item['title']} (Tags: {result.item['tags']})")

    # 5. Category filter
    print("\n5️⃣ CATEGORY FILTER - Development tasks")
    query = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.CATEGORY, "eq", "Development")],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} development tasks:")
    for result in results:
        print(f"   - {result.item['title']}")


def demo_search_with_filters():
    """Demonstrate combined search and filters"""
    print("\n" + "=" * 70)
    print("DEMO: Combined Search and Filters")
    print("=" * 70)

    engine = get_search_engine()

    # 1. Search + priority filter
    print("\n1️⃣ SEARCH + FILTER - 'bug' with high/critical priority")
    query = SearchQuery(
        query="bug",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.PRIORITY, "in", ["high", "critical"])],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(
            f"   - {result.item['title']} (Priority: {result.item['priority']}, Score: {result.score:.2f})"
        )

    # 2. Search specific field
    print("\n2️⃣ FIELD SEARCH - Search in title only")
    query = SearchQuery(
        query="update", mode=SearchMode.PARTIAL, fields=[SearchField.TITLE]
    )
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - {result.item['title']}")

    # 3. Complex query
    print("\n3️⃣ COMPLEX QUERY - Documentation tasks, not started, medium+ priority")
    query = SearchQuery(
        query="documentation",
        mode=SearchMode.PARTIAL,
        fields=[SearchField.TITLE, SearchField.DESCRIPTION],
        filters=[
            SearchFilter(SearchField.STATUS, "ne", "not_started"),
            SearchFilter(SearchField.PRIORITY, "in", ["medium", "high", "critical"]),
        ],
    )
    results = engine.search(query)
    print(f"   Found {len(results)} results:")
    for result in results:
        print(
            f"   - {result.item['title']} (Status: {result.item['status']}, Priority: {result.item['priority']})"
        )


def demo_saved_searches():
    """Demonstrate saved searches"""
    print("\n" + "=" * 70)
    print("DEMO: Saved Searches")
    print("=" * 70)

    manager = get_saved_search_manager()

    # 1. Save common searches
    print("\n1️⃣ SAVING COMMON SEARCHES")

    # Critical tasks
    query1 = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.PRIORITY, "eq", "critical")],
    )
    saved1 = manager.save_search(
        "Critical Tasks", query1, "All tasks with critical priority"
    )
    print(f"   ✓ Saved: {saved1.name}")

    # In progress tasks
    query2 = SearchQuery(
        query="",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.STATUS, "eq", "in_progress")],
    )
    saved2 = manager.save_search("In Progress", query2, "Tasks currently in progress")
    print(f"   ✓ Saved: {saved2.name}")

    # Security-related
    query3 = SearchQuery(
        query="security",
        mode=SearchMode.PARTIAL,
        filters=[SearchFilter(SearchField.TAGS, "contains", "security")],
    )
    saved3 = manager.save_search(
        "Security Tasks", query3, "All security-related tasks"
    )
    print(f"   ✓ Saved: {saved3.name}")

    # 2. List saved searches
    print("\n2️⃣ LISTING SAVED SEARCHES")
    searches = manager.list_searches()
    print(f"   Total saved searches: {len(searches)}")
    for search in searches:
        print(f"   - {search.name}: {search.description}")

    # 3. Execute saved search
    print("\n3️⃣ EXECUTING SAVED SEARCH")
    engine = get_search_engine()
    critical_search = manager.get_search_by_name("Critical Tasks")
    if critical_search:
        results = engine.search(critical_search.query)
        manager.mark_used(critical_search.id)
        print(f"   Executed '{critical_search.name}' - Found {len(results)} results:")
        for result in results:
            print(f"   - {result.item['title']}")

    # 4. Popular searches
    print("\n4️⃣ POPULAR SEARCHES")
    # Mark some searches as used
    for _ in range(3):
        manager.mark_used(saved1.id)
    manager.mark_used(saved2.id)

    popular = manager.get_popular_searches(3)
    print(f"   Top {len(popular)} popular searches:")
    for search in popular:
        print(f"   - {search.name} (Used {search.use_count} times)")


def demo_search_history():
    """Demonstrate search history tracking"""
    print("\n" + "=" * 70)
    print("DEMO: Search History Tracking")
    print("=" * 70)

    engine = get_search_engine()
    tracker = get_search_history_tracker()

    # 1. Perform searches with tracking
    print("\n1️⃣ PERFORMING SEARCHES WITH TRACKING")

    searches = [
        ("documentation", SearchMode.PARTIAL),
        ("bug", SearchMode.PARTIAL),
        ("security", SearchMode.SEMANTIC),
        ("authentication", SearchMode.FUZZY),
        ("update", SearchMode.EXACT),
    ]

    for query_text, mode in searches:
        query = SearchQuery(query=query_text, mode=mode)
        start_time = time.time()
        results = engine.search(query)
        execution_time = (time.time() - start_time) * 1000

        tracker.add_entry(query, len(results), execution_time)
        print(f"   ✓ Searched '{query_text}' - {len(results)} results ({execution_time:.2f}ms)")

    # 2. Recent searches
    print("\n2️⃣ RECENT SEARCHES")
    recent = tracker.get_recent_searches(5)
    print(f"   Last {len(recent)} searches:")
    for entry in recent:
        print(
            f"   - '{entry.query.query}' ({entry.query.mode.value}) - {entry.results_count} results"
        )

    # 3. Frequent queries
    print("\n3️⃣ FREQUENT QUERIES")
    frequent = tracker.get_frequent_queries(3)
    print(f"   Top {len(frequent)} frequent queries:")
    for item in frequent:
        print(f"   - '{item['query']}' (Searched {item['count']} times)")

    # 4. Search mode statistics
    print("\n4️⃣ SEARCH MODE STATISTICS")
    mode_stats = tracker.get_search_modes_stats()
    print("   Search mode usage:")
    for mode, count in mode_stats.items():
        print(f"   - {mode}: {count} searches")

    # 5. Analytics
    print("\n5️⃣ SEARCH ANALYTICS")
    analytics = tracker.get_analytics()
    print(f"   Total searches: {analytics['total_searches']}")
    print(f"   Average results: {analytics['average_results']:.1f}")
    print(f"   Average execution time: {analytics['average_execution_time_ms']:.2f}ms")
    print(f"   Empty searches: {analytics['empty_searches_count']} ({analytics['empty_searches_rate']:.1f}%)")


def demo_autocomplete():
    """Demonstrate autocomplete suggestions"""
    print("\n" + "=" * 70)
    print("DEMO: Autocomplete Suggestions")
    print("=" * 70)

    engine = get_search_engine()

    prefixes = ["doc", "sec", "upd", "bug", "auth"]

    for prefix in prefixes:
        suggestions = engine.get_suggestions(prefix, limit=5)
        print(f"\n'{prefix}' → {suggestions}")


def demo_performance():
    """Demonstrate search performance"""
    print("\n" + "=" * 70)
    print("DEMO: Search Performance")
    print("=" * 70)

    engine = get_search_engine()

    # Test different search modes
    modes = [
        SearchMode.EXACT,
        SearchMode.PARTIAL,
        SearchMode.FUZZY,
        SearchMode.REGEX,
        SearchMode.SEMANTIC,
    ]

    print("\n⏱️  Performance comparison:")
    for mode in modes:
        query = SearchQuery(query="documentation", mode=mode)

        # Run 10 times and average
        times = []
        for _ in range(10):
            start_time = time.time()
            results = engine.search(query)
            execution_time = (time.time() - start_time) * 1000
            times.append(execution_time)

        avg_time = sum(times) / len(times)
        print(
            f"   {mode.value:12} - Avg: {avg_time:.2f}ms, Min: {min(times):.2f}ms, Max: {max(times):.2f}ms"
        )


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("XENO ADVANCED SEARCH & FILTERS - COMPREHENSIVE DEMO")
    print("=" * 70)

    try:
        # Basic search
        demo_basic_search()

        # Advanced filtering
        demo_advanced_filtering()

        # Combined search and filters
        demo_search_with_filters()

        # Saved searches
        demo_saved_searches()

        # Search history
        demo_search_history()

        # Autocomplete
        demo_autocomplete()

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
