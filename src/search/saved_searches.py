"""
Saved Searches
Manage saved search queries
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger
from src.search.search_engine import SearchField, SearchFilter, SearchMode, SearchQuery


class SavedSearch:
    """Represents a saved search"""

    def __init__(
        self,
        id: str,
        name: str,
        query: SearchQuery,
        description: str = "",
        created_at: datetime = None,
        last_used: datetime = None,
        use_count: int = 0,
    ):
        self.id = id
        self.name = name
        self.query = query
        self.description = description
        self.created_at = created_at or datetime.now()
        self.last_used = last_used
        self.use_count = use_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "query": self.query.to_dict(),
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SavedSearch":
        """Create from dictionary"""
        # Reconstruct query
        query_data = data["query"]
        filters = [
            SearchFilter(
                field=SearchField(f["field"]),
                operator=f["operator"],
                value=f["value"],
            )
            for f in query_data.get("filters", [])
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
            id=data["id"],
            name=data["name"],
            query=query,
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None,
            use_count=data.get("use_count", 0),
        )


class SavedSearchManager:
    """Manages saved searches"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("search.saved")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "searches"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.searches_file = self.storage_path / "saved_searches.json"

        # Saved searches
        self.searches: Dict[str, SavedSearch] = {}

        # Load saved searches
        self._load_searches()

    def save_search(self, name: str, query: SearchQuery, description: str = "") -> SavedSearch:
        """Save a search query"""
        # Generate ID
        search_id = f"search_{int(datetime.now().timestamp() * 1000)}"

        saved_search = SavedSearch(id=search_id, name=name, query=query, description=description)

        self.searches[search_id] = saved_search
        self._persist_searches()

        self.logger.info(f"Saved search: {name}")
        return saved_search

    def get_search(self, search_id: str) -> Optional[SavedSearch]:
        """Get saved search by ID"""
        return self.searches.get(search_id)

    def get_search_by_name(self, name: str) -> Optional[SavedSearch]:
        """Get saved search by name"""
        for search in self.searches.values():
            if search.name == name:
                return search
        return None

    def list_searches(self) -> List[SavedSearch]:
        """List all saved searches"""
        return sorted(self.searches.values(), key=lambda s: s.created_at, reverse=True)

    def update_search(
        self,
        search_id: str,
        name: Optional[str] = None,
        query: Optional[SearchQuery] = None,
        description: Optional[str] = None,
    ) -> bool:
        """Update saved search"""
        if search_id not in self.searches:
            return False

        search = self.searches[search_id]

        if name:
            search.name = name
        if query:
            search.query = query
        if description is not None:
            search.description = description

        self._persist_searches()
        self.logger.info(f"Updated search: {search_id}")
        return True

    def delete_search(self, search_id: str) -> bool:
        """Delete saved search"""
        if search_id in self.searches:
            del self.searches[search_id]
            self._persist_searches()
            self.logger.info(f"Deleted search: {search_id}")
            return True
        return False

    def mark_used(self, search_id: str):
        """Mark search as used"""
        if search_id in self.searches:
            search = self.searches[search_id]
            search.last_used = datetime.now()
            search.use_count += 1
            self._persist_searches()

    def get_popular_searches(self, limit: int = 10) -> List[SavedSearch]:
        """Get most popular saved searches"""
        searches = list(self.searches.values())
        searches.sort(key=lambda s: s.use_count, reverse=True)
        return searches[:limit]

    def get_recent_searches(self, limit: int = 10) -> List[SavedSearch]:
        """Get recently used searches"""
        searches = [s for s in self.searches.values() if s.last_used]
        searches.sort(key=lambda s: s.last_used, reverse=True)
        return searches[:limit]

    def _persist_searches(self):
        """Save searches to disk"""
        try:
            data = {
                "searches": [s.to_dict() for s in self.searches.values()],
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.searches_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist searches: {e}")

    def _load_searches(self):
        """Load searches from disk"""
        if not self.searches_file.exists():
            return

        try:
            with open(self.searches_file, "r") as f:
                data = json.load(f)

            for search_data in data.get("searches", []):
                search = SavedSearch.from_dict(search_data)
                self.searches[search.id] = search

            self.logger.info(f"Loaded {len(self.searches)} saved searches")

        except Exception as e:
            self.logger.error(f"Failed to load searches: {e}")


# Global instance
_saved_search_manager: Optional[SavedSearchManager] = None


def get_saved_search_manager() -> SavedSearchManager:
    """Get global saved search manager"""
    global _saved_search_manager
    if _saved_search_manager is None:
        _saved_search_manager = SavedSearchManager()
    return _saved_search_manager
