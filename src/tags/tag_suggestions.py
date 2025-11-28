"""
Tag Suggestions
ML-based tag suggestions and predictions
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.logger import setup_logger
from src.tags.tag_hierarchy import Tag, get_tag_hierarchy


class TagSuggestionEngine:
    """Generates intelligent tag suggestions"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("tags.suggestions")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "tags"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.storage_path / "tag_patterns.json"

        # Tag co-occurrence patterns
        self.co_occurrences: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Content-to-tag mappings
        self.keyword_tag_map: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

        # Load patterns
        self._load_patterns()

    def learn_from_item(self, item: Dict[str, Any], tags: List[str]):
        """Learn tag patterns from an item"""
        if not tags:
            return

        # Learn co-occurrences
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i + 1 :]:
                self.co_occurrences[tag1][tag2] += 1
                self.co_occurrences[tag2][tag1] += 1

        # Learn keyword associations
        keywords = self._extract_keywords(item)
        for keyword in keywords:
            for tag in tags:
                self.keyword_tag_map[keyword][tag] += 1

        self._persist_patterns()

    def suggest_tags(
        self,
        item: Dict[str, Any],
        existing_tags: List[str] = None,
        limit: int = 5,
    ) -> List[Tuple[str, float]]:
        """Suggest tags for an item"""
        existing_tags = existing_tags or []
        suggestions = {}

        # 1. Co-occurrence based suggestions
        for tag in existing_tags:
            if tag in self.co_occurrences:
                for related_tag, count in self.co_occurrences[tag].items():
                    if related_tag not in existing_tags:
                        suggestions[related_tag] = suggestions.get(related_tag, 0) + count * 2

        # 2. Keyword based suggestions
        keywords = self._extract_keywords(item)
        for keyword in keywords:
            if keyword in self.keyword_tag_map:
                for tag, count in self.keyword_tag_map[keyword].items():
                    if tag not in existing_tags:
                        suggestions[tag] = suggestions.get(tag, 0) + count

        # 3. Category based suggestions
        if "category" in item:
            category_tag = item["category"].lower()
            if category_tag not in existing_tags:
                suggestions[category_tag] = suggestions.get(category_tag, 0) + 5

        # 4. Priority based suggestions
        if "priority" in item:
            priority = item["priority"].lower()
            if priority in ["critical", "high"]:
                if "urgent" not in existing_tags:
                    suggestions["urgent"] = suggestions.get("urgent", 0) + 3
                if "important" not in existing_tags:
                    suggestions["important"] = suggestions.get("important", 0) + 3

        # Normalize scores to 0-1 range
        if suggestions:
            max_score = max(suggestions.values())
            suggestions = {tag: score / max_score for tag, score in suggestions.items()}

        # Sort by score
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)

        return sorted_suggestions[:limit]

    def suggest_similar_tags(self, tag_id: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Suggest tags similar to given tag"""
        hierarchy = get_tag_hierarchy()
        tag = hierarchy.get_tag(tag_id)

        if not tag:
            return []

        suggestions = {}

        # 1. Siblings (same parent)
        if tag.parent_id:
            parent = hierarchy.get_tag(tag.parent_id)
            if parent:
                for sibling_id in parent.children:
                    if sibling_id != tag_id:
                        suggestions[sibling_id] = 0.8

        # 2. Co-occurring tags
        if tag.name in self.co_occurrences:
            for related_tag, count in self.co_occurrences[tag.name].items():
                related = hierarchy.get_tag_by_name(related_tag)
                if related and related.id != tag_id:
                    suggestions[related.id] = suggestions.get(related.id, 0) + (count / 100)

        # 3. Children
        children = hierarchy.get_children(tag_id)
        for child in children:
            suggestions[child.id] = 0.6

        # Sort by score
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)

        return sorted_suggestions[:limit]

    def suggest_tag_names(self, prefix: str, limit: int = 10) -> List[str]:
        """Suggest tag names based on prefix (autocomplete)"""
        hierarchy = get_tag_hierarchy()
        prefix_lower = prefix.lower()

        suggestions = []
        for tag in hierarchy.tags.values():
            if tag.name.lower().startswith(prefix_lower):
                suggestions.append(tag.name)

        # Also check learned keywords
        for keyword in self.keyword_tag_map.keys():
            if keyword.startswith(prefix_lower) and keyword not in suggestions:
                suggestions.append(keyword)

        return sorted(suggestions)[:limit]

    def get_trending_tags(self, days: int = 7, limit: int = 10) -> List[Tuple[str, int]]:
        """Get trending tags based on recent usage"""
        hierarchy = get_tag_hierarchy()

        # In production, this would track usage over time
        # For now, use overall usage counts
        tags = list(hierarchy.tags.values())
        tags.sort(key=lambda t: t.usage_count, reverse=True)

        return [(tag.name, tag.usage_count) for tag in tags[:limit]]

    def _extract_keywords(self, item: Dict[str, Any]) -> Set[str]:
        """Extract keywords from item"""
        keywords = set()

        # Extract from text fields
        text_fields = ["title", "description", "content", "notes"]
        for field in text_fields:
            if field in item:
                text = str(item[field]).lower()
                # Extract words (3+ characters, alphanumeric)
                words = re.findall(r"\b[a-z]{3,}\b", text)
                keywords.update(words)

        # Remove common stop words
        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "from",
            "that",
            "this",
            "are",
            "was",
            "will",
            "has",
            "have",
            "been",
        }
        keywords -= stop_words

        return keywords

    def _persist_patterns(self):
        """Save patterns to disk"""
        try:
            data = {
                "co_occurrences": {
                    tag: dict(related) for tag, related in self.co_occurrences.items()
                },
                "keyword_tag_map": {
                    keyword: dict(tags) for keyword, tags in self.keyword_tag_map.items()
                },
            }

            with open(self.patterns_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist patterns: {e}")

    def _load_patterns(self):
        """Load patterns from disk"""
        if not self.patterns_file.exists():
            return

        try:
            with open(self.patterns_file, "r") as f:
                data = json.load(f)

            # Load co-occurrences
            for tag, related in data.get("co_occurrences", {}).items():
                self.co_occurrences[tag] = defaultdict(int, related)

            # Load keyword mappings
            for keyword, tags in data.get("keyword_tag_map", {}).items():
                self.keyword_tag_map[keyword] = defaultdict(int, tags)

            self.logger.info(
                f"Loaded {len(self.co_occurrences)} tag patterns and {len(self.keyword_tag_map)} keyword mappings"
            )

        except Exception as e:
            self.logger.error(f"Failed to load patterns: {e}")


# Global instance
_tag_suggestion_engine: Optional[TagSuggestionEngine] = None


def get_tag_suggestion_engine() -> TagSuggestionEngine:
    """Get global tag suggestion engine"""
    global _tag_suggestion_engine
    if _tag_suggestion_engine is None:
        _tag_suggestion_engine = TagSuggestionEngine()
    return _tag_suggestion_engine
