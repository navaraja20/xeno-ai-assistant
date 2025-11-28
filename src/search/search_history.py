"""
Search History
Track search queries and analytics
"""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger
from src.search.search_engine import SearchQuery, SearchMode, SearchField


class SearchHistoryEntry:
    """Single search history entry"""

    def __init__(
        self,
        query: SearchQuery,
        results_count: int,
        timestamp: datetime = None,
        execution_time_ms: float = 0,
    ):
        self.query = query
        self.results_count = results_count
        self.timestamp = timestamp or datetime.now()
        self.execution_time_ms = execution_time_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query.to_dict(),
            "results_count": self.results_count,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchHistoryEntry":
        """Create from dictionary"""
        query_data = data["query"]

        # Reconstruct filters
        filters = []
        if "filters" in query_data:
            from src.search.search_engine import SearchFilter

            filters = [
                SearchFilter(
                    field=SearchField(f["field"]),
                    operator=f["operator"],
                    value=f["value"],
                )
                for f in query_data["filters"]
            ]

        query = SearchQuery(
            query=query_data["query"],
            mode=SearchMode(query_data["mode"]),
            fields=[SearchField(f) for f in query_data.get("fields", ["all"])],
            filters=filters,
            limit=query_data.get("limit"),
            offset=query_data.get("offset", 0),
        )

        return cls(
            query=query,
            results_count=data["results_count"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            execution_time_ms=data.get("execution_time_ms", 0),
        )


class SearchHistoryTracker:
    """Tracks search history and analytics"""

    def __init__(self, storage_path: str = None, max_history: int = 1000):
        self.logger = setup_logger("search.history")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "searches"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.history_file = self.storage_path / "search_history.json"
        self.max_history = max_history

        # History entries
        self.history: List[SearchHistoryEntry] = []

        # Load history
        self._load_history()

    def add_entry(
        self,
        query: SearchQuery,
        results_count: int,
        execution_time_ms: float = 0,
    ):
        """Add search to history"""
        entry = SearchHistoryEntry(query, results_count, execution_time_ms=execution_time_ms)
        self.history.insert(0, entry)  # Add to front

        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[: self.max_history]

        self._persist_history()

    def get_recent_searches(self, limit: int = 10) -> List[SearchHistoryEntry]:
        """Get recent search entries"""
        return self.history[:limit]

    def get_searches_by_date(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> List[SearchHistoryEntry]:
        """Get searches within date range"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.now()

        return [
            entry
            for entry in self.history
            if start_date <= entry.timestamp <= end_date
        ]

    def get_frequent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequent search queries"""
        query_texts = [entry.query.query for entry in self.history]
        counter = Counter(query_texts)

        return [
            {"query": query, "count": count}
            for query, count in counter.most_common(limit)
        ]

    def get_search_modes_stats(self) -> Dict[str, int]:
        """Get statistics on search modes usage"""
        modes = [entry.query.mode.value for entry in self.history]
        counter = Counter(modes)
        return dict(counter)

    def get_average_results_count(self) -> float:
        """Get average number of results"""
        if not self.history:
            return 0

        total = sum(entry.results_count for entry in self.history)
        return total / len(self.history)

    def get_average_execution_time(self) -> float:
        """Get average search execution time"""
        if not self.history:
            return 0

        total = sum(entry.execution_time_ms for entry in self.history)
        return total / len(self.history)

    def get_searches_by_mode(self, mode: SearchMode) -> List[SearchHistoryEntry]:
        """Get all searches using specific mode"""
        return [entry for entry in self.history if entry.query.mode == mode]

    def get_empty_searches(self) -> List[SearchHistoryEntry]:
        """Get searches that returned no results"""
        return [entry for entry in self.history if entry.results_count == 0]

    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive search analytics"""
        return {
            "total_searches": len(self.history),
            "average_results": self.get_average_results_count(),
            "average_execution_time_ms": self.get_average_execution_time(),
            "search_modes_distribution": self.get_search_modes_stats(),
            "frequent_queries": self.get_frequent_queries(5),
            "empty_searches_count": len(self.get_empty_searches()),
            "empty_searches_rate": (
                len(self.get_empty_searches()) / len(self.history) * 100
                if self.history
                else 0
            ),
        }

    def clear_history(self):
        """Clear all history"""
        self.history = []
        self._persist_history()
        self.logger.info("Search history cleared")

    def clear_old_entries(self, days: int = 30):
        """Clear entries older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_count = len(self.history)

        self.history = [
            entry for entry in self.history if entry.timestamp >= cutoff_date
        ]

        removed = old_count - len(self.history)
        if removed > 0:
            self._persist_history()
            self.logger.info(f"Removed {removed} old entries")

    def export_history(self, output_path: str):
        """Export history to JSON file"""
        try:
            data = {
                "history": [entry.to_dict() for entry in self.history],
                "analytics": self.get_analytics(),
                "exported_at": datetime.now().isoformat(),
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Exported history to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export history: {e}")
            return False

    def _persist_history(self):
        """Save history to disk"""
        try:
            data = {
                "history": [entry.to_dict() for entry in self.history],
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.history_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist history: {e}")

    def _load_history(self):
        """Load history from disk"""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, "r") as f:
                data = json.load(f)

            self.history = [
                SearchHistoryEntry.from_dict(entry_data)
                for entry_data in data.get("history", [])
            ]

            self.logger.info(f"Loaded {len(self.history)} history entries")

        except Exception as e:
            self.logger.error(f"Failed to load history: {e}")


# Global instance
_search_history_tracker: Optional[SearchHistoryTracker] = None


def get_search_history_tracker() -> SearchHistoryTracker:
    """Get global search history tracker"""
    global _search_history_tracker
    if _search_history_tracker is None:
        _search_history_tracker = SearchHistoryTracker()
    return _search_history_tracker
