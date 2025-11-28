"""
Search Module
Advanced search and filters
"""

from src.search.saved_searches import SavedSearch, SavedSearchManager, get_saved_search_manager
from src.search.search_engine import (
    SearchEngine,
    SearchField,
    SearchFilter,
    SearchMode,
    SearchQuery,
    SearchResult,
    get_search_engine,
)
from src.search.search_history import (
    SearchHistoryEntry,
    SearchHistoryTracker,
    get_search_history_tracker,
)

__all__ = [
    # Search Engine
    "SearchEngine",
    "SearchQuery",
    "SearchResult",
    "SearchMode",
    "SearchField",
    "SearchFilter",
    "get_search_engine",
    # Saved Searches
    "SavedSearch",
    "SavedSearchManager",
    "get_saved_search_manager",
    # Search History
    "SearchHistoryEntry",
    "SearchHistoryTracker",
    "get_search_history_tracker",
]
