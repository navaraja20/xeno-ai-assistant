"""
Search Engine
Advanced search with multiple search strategies
"""

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Callable
from enum import Enum

from src.core.logger import setup_logger


class SearchMode(Enum):
    """Search mode"""

    EXACT = "exact"  # Exact match
    PARTIAL = "partial"  # Partial match (contains)
    FUZZY = "fuzzy"  # Fuzzy match
    REGEX = "regex"  # Regular expression
    SEMANTIC = "semantic"  # Semantic search


class SearchField(Enum):
    """Searchable fields"""

    TITLE = "title"
    DESCRIPTION = "description"
    TAGS = "tags"
    PRIORITY = "priority"
    STATUS = "status"
    CATEGORY = "category"
    ALL = "all"  # Search all fields


class SearchFilter:
    """Represents a search filter"""

    def __init__(
        self,
        field: SearchField,
        operator: str,
        value: Any,
    ):
        self.field = field
        self.operator = operator  # eq, ne, lt, gt, le, ge, in, contains, regex
        self.value = value

    def matches(self, item: Dict[str, Any]) -> bool:
        """Check if item matches filter"""
        # Get field value
        field_value = item.get(self.field.value)

        if field_value is None:
            return False

        # Apply operator
        if self.operator == "eq":
            return field_value == self.value

        elif self.operator == "ne":
            return field_value != self.value

        elif self.operator == "lt":
            return field_value < self.value

        elif self.operator == "gt":
            return field_value > self.value

        elif self.operator == "le":
            return field_value <= self.value

        elif self.operator == "ge":
            return field_value >= self.value

        elif self.operator == "in":
            if isinstance(self.value, (list, tuple, set)):
                return field_value in self.value
            return False

        elif self.operator == "contains":
            if isinstance(field_value, str):
                return self.value.lower() in field_value.lower()
            elif isinstance(field_value, (list, tuple)):
                return self.value in field_value
            return False

        elif self.operator == "regex":
            if isinstance(field_value, str):
                return bool(re.search(self.value, field_value, re.IGNORECASE))
            return False

        return False


class SearchQuery:
    """Represents a search query"""

    def __init__(
        self,
        query: str = "",
        mode: SearchMode = SearchMode.PARTIAL,
        fields: List[SearchField] = None,
        filters: List[SearchFilter] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ):
        self.query = query
        self.mode = mode
        self.fields = fields or [SearchField.ALL]
        self.filters = filters or []
        self.limit = limit
        self.offset = offset

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "mode": self.mode.value,
            "fields": [f.value for f in self.fields],
            "filters": [
                {"field": f.field.value, "operator": f.operator, "value": f.value}
                for f in self.filters
            ],
            "limit": self.limit,
            "offset": self.offset,
        }


class SearchResult:
    """Search result with relevance score"""

    def __init__(
        self,
        item: Dict[str, Any],
        score: float = 0.0,
        highlights: Dict[str, List[str]] = None,
    ):
        self.item = item
        self.score = score
        self.highlights = highlights or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item": self.item,
            "score": self.score,
            "highlights": self.highlights,
        }


class SearchEngine:
    """Advanced search engine"""

    def __init__(self):
        self.logger = setup_logger("search.engine")

        # Index for full-text search
        self._index: Dict[str, Set[str]] = {}  # word -> set of item IDs

        # Items storage
        self._items: Dict[str, Dict[str, Any]] = {}  # item_id -> item

    def index_item(self, item_id: str, item: Dict[str, Any]):
        """Index an item for searching"""
        self._items[item_id] = item

        # Extract searchable text
        searchable_text = self._extract_searchable_text(item)

        # Tokenize and index
        tokens = self._tokenize(searchable_text)
        for token in tokens:
            if token not in self._index:
                self._index[token] = set()
            self._index[token].add(item_id)

        self.logger.debug(f"Indexed item: {item_id}")

    def remove_item(self, item_id: str):
        """Remove item from index"""
        if item_id in self._items:
            # Remove from index
            item = self._items[item_id]
            searchable_text = self._extract_searchable_text(item)
            tokens = self._tokenize(searchable_text)

            for token in tokens:
                if token in self._index:
                    self._index[token].discard(item_id)
                    if not self._index[token]:
                        del self._index[token]

            # Remove from storage
            del self._items[item_id]
            self.logger.debug(f"Removed item: {item_id}")

    def search(self, query: SearchQuery) -> List[SearchResult]:
        """Execute search query"""
        # Start with all items
        candidate_ids = set(self._items.keys())

        # Apply filters
        if query.filters:
            candidate_ids = self._apply_filters(candidate_ids, query.filters)

        # If no text query, return filtered results
        if not query.query:
            results = [
                SearchResult(self._items[item_id], score=1.0)
                for item_id in candidate_ids
            ]
        else:
            # Apply text search
            results = self._text_search(query, candidate_ids)

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        # Apply pagination
        start = query.offset
        end = start + query.limit if query.limit else None
        results = results[start:end]

        self.logger.info(f"Search returned {len(results)} results")
        return results

    def _extract_searchable_text(self, item: Dict[str, Any]) -> str:
        """Extract searchable text from item"""
        parts = []

        # Common searchable fields
        for field in ["title", "description", "content", "notes"]:
            if field in item and item[field]:
                parts.append(str(item[field]))

        # Tags
        if "tags" in item and item["tags"]:
            if isinstance(item["tags"], list):
                parts.extend(item["tags"])
            else:
                parts.append(str(item["tags"]))

        return " ".join(parts)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable tokens"""
        # Convert to lowercase
        text = text.lower()

        # Split on non-alphanumeric characters
        tokens = re.findall(r'\w+', text)

        # Remove very short tokens
        tokens = [t for t in tokens if len(t) > 1]

        return tokens

    def _apply_filters(
        self, candidate_ids: Set[str], filters: List[SearchFilter]
    ) -> Set[str]:
        """Apply filters to candidate items"""
        filtered_ids = candidate_ids.copy()

        for search_filter in filters:
            # Check each candidate
            matching_ids = set()
            for item_id in filtered_ids:
                item = self._items[item_id]
                if search_filter.matches(item):
                    matching_ids.add(item_id)

            filtered_ids = matching_ids

        return filtered_ids

    def _text_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Perform text search"""
        if query.mode == SearchMode.EXACT:
            return self._exact_search(query, candidate_ids)

        elif query.mode == SearchMode.PARTIAL:
            return self._partial_search(query, candidate_ids)

        elif query.mode == SearchMode.FUZZY:
            return self._fuzzy_search(query, candidate_ids)

        elif query.mode == SearchMode.REGEX:
            return self._regex_search(query, candidate_ids)

        elif query.mode == SearchMode.SEMANTIC:
            return self._semantic_search(query, candidate_ids)

        return []

    def _exact_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Exact match search"""
        results = []
        query_lower = query.query.lower()

        for item_id in candidate_ids:
            item = self._items[item_id]
            searchable_text = self._extract_searchable_text(item).lower()

            if query_lower == searchable_text:
                results.append(SearchResult(item, score=1.0))
            elif query_lower in searchable_text:
                # Partial exact match
                score = len(query_lower) / len(searchable_text)
                results.append(SearchResult(item, score=score))

        return results

    def _partial_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Partial match search (contains)"""
        results = []
        query_tokens = self._tokenize(query.query)

        for item_id in candidate_ids:
            item = self._items[item_id]
            searchable_text = self._extract_searchable_text(item)
            item_tokens = self._tokenize(searchable_text)

            # Calculate match score
            matches = 0
            highlights = {}

            for query_token in query_tokens:
                for item_token in item_tokens:
                    if query_token in item_token:
                        matches += 1

                        # Add highlight
                        for field in ["title", "description"]:
                            if field in item and item[field]:
                                field_text = str(item[field])
                                if query_token.lower() in field_text.lower():
                                    if field not in highlights:
                                        highlights[field] = []
                                    highlights[field].append(query_token)

            if matches > 0:
                score = matches / len(query_tokens)
                results.append(SearchResult(item, score=score, highlights=highlights))

        return results

    def _fuzzy_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Fuzzy match search"""
        results = []
        query_tokens = self._tokenize(query.query)

        for item_id in candidate_ids:
            item = self._items[item_id]
            searchable_text = self._extract_searchable_text(item)
            item_tokens = self._tokenize(searchable_text)

            # Calculate fuzzy match score
            total_score = 0
            matches = 0

            for query_token in query_tokens:
                best_match_score = 0

                for item_token in item_tokens:
                    # Levenshtein distance
                    similarity = self._string_similarity(query_token, item_token)
                    best_match_score = max(best_match_score, similarity)

                if best_match_score > 0.6:  # Threshold
                    total_score += best_match_score
                    matches += 1

            if matches > 0:
                score = total_score / len(query_tokens)
                results.append(SearchResult(item, score=score))

        return results

    def _regex_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Regular expression search"""
        results = []

        try:
            pattern = re.compile(query.query, re.IGNORECASE)

            for item_id in candidate_ids:
                item = self._items[item_id]
                searchable_text = self._extract_searchable_text(item)

                if pattern.search(searchable_text):
                    results.append(SearchResult(item, score=1.0))

        except re.error as e:
            self.logger.error(f"Invalid regex: {e}")

        return results

    def _semantic_search(
        self, query: SearchQuery, candidate_ids: Set[str]
    ) -> List[SearchResult]:
        """Semantic search (basic implementation)"""
        # This is a simplified version
        # A full implementation would use embeddings and vector similarity

        results = []
        query_tokens = set(self._tokenize(query.query))

        for item_id in candidate_ids:
            item = self._items[item_id]
            searchable_text = self._extract_searchable_text(item)
            item_tokens = set(self._tokenize(searchable_text))

            # Jaccard similarity
            intersection = query_tokens & item_tokens
            union = query_tokens | item_tokens

            if union:
                score = len(intersection) / len(union)
                if score > 0:
                    results.append(SearchResult(item, score=score))

        return results

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity (0-1)"""
        # Levenshtein distance
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return 0.0

        distances = range(len(s2) + 1)

        for i1, c1 in enumerate(s1):
            new_distances = [i1 + 1]
            for i2, c2 in enumerate(s2):
                if c1 == c2:
                    new_distances.append(distances[i2])
                else:
                    new_distances.append(
                        1 + min(distances[i2], distances[i2 + 1], new_distances[-1])
                    )
            distances = new_distances

        # Convert distance to similarity
        max_len = max(len(s1), len(s2))
        return 1.0 - (distances[-1] / max_len)

    def get_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = set()
        partial_lower = partial_query.lower()

        # Find matching tokens in index
        for token in self._index.keys():
            if token.startswith(partial_lower):
                suggestions.add(token)

            if len(suggestions) >= limit:
                break

        return sorted(list(suggestions))[:limit]


# Global instance
_search_engine: Optional[SearchEngine] = None


def get_search_engine() -> SearchEngine:
    """Get global search engine"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SearchEngine()
    return _search_engine
