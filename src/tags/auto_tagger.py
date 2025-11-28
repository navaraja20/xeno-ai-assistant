"""
Auto-Tagging
Automatic tag assignment based on content analysis
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.logger import setup_logger
from src.tags.tag_hierarchy import get_tag_hierarchy
from src.tags.tag_suggestions import get_tag_suggestion_engine


class AutoTagger:
    """Automatically assigns tags to items"""

    def __init__(self):
        self.logger = setup_logger("tags.auto")

        # Predefined rules
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> List[Dict[str, Any]]:
        """Initialize tagging rules"""
        return [
            # Priority-based rules
            {
                "name": "critical_priority",
                "condition": lambda item: item.get("priority") == "critical",
                "tags": ["urgent", "important"],
                "confidence": 0.9,
            },
            {
                "name": "high_priority",
                "condition": lambda item: item.get("priority") == "high",
                "tags": ["important"],
                "confidence": 0.8,
            },
            # Time-based rules
            {
                "name": "overdue",
                "condition": lambda item: self._is_overdue(item),
                "tags": ["overdue", "urgent"],
                "confidence": 0.95,
            },
            {
                "name": "due_soon",
                "condition": lambda item: self._is_due_soon(item),
                "tags": ["due-soon"],
                "confidence": 0.85,
            },
            # Content-based rules
            {
                "name": "bug_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["bug", "error", "crash", "failure", "broken"]
                ),
                "tags": ["bug"],
                "confidence": 0.9,
            },
            {
                "name": "feature_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["feature", "enhancement", "improvement", "new"]
                ),
                "tags": ["feature"],
                "confidence": 0.85,
            },
            {
                "name": "documentation_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["documentation", "docs", "readme", "guide"]
                ),
                "tags": ["documentation"],
                "confidence": 0.9,
            },
            {
                "name": "security_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["security", "vulnerability", "exploit", "attack", "breach"]
                ),
                "tags": ["security"],
                "confidence": 0.95,
            },
            {
                "name": "performance_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["performance", "optimization", "slow", "speed", "faster"]
                ),
                "tags": ["performance"],
                "confidence": 0.85,
            },
            {
                "name": "testing_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["test", "testing", "qa", "quality"]
                ),
                "tags": ["testing"],
                "confidence": 0.85,
            },
            {
                "name": "meeting_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["meeting", "call", "presentation", "demo"]
                ),
                "tags": ["meeting"],
                "confidence": 0.8,
            },
            {
                "name": "review_mention",
                "condition": lambda item: self._contains_keywords(
                    item, ["review", "feedback", "comment", "approval"]
                ),
                "tags": ["review"],
                "confidence": 0.8,
            },
        ]

    def auto_tag(
        self,
        item: Dict[str, Any],
        existing_tags: List[str] = None,
        min_confidence: float = 0.7,
    ) -> List[Tuple[str, float]]:
        """Automatically assign tags to an item"""
        existing_tags = existing_tags or []
        suggestions = {}

        # 1. Apply rule-based tagging
        for rule in self.rules:
            try:
                if rule["condition"](item):
                    for tag in rule["tags"]:
                        if tag not in existing_tags:
                            suggestions[tag] = max(suggestions.get(tag, 0), rule["confidence"])
            except Exception as e:
                self.logger.error(f"Rule '{rule['name']}' failed: {e}")

        # 2. Use ML-based suggestions
        engine = get_tag_suggestion_engine()
        ml_suggestions = engine.suggest_tags(item, existing_tags, limit=10)

        for tag, score in ml_suggestions:
            if tag not in existing_tags:
                # Combine with rule-based score
                suggestions[tag] = max(suggestions.get(tag, 0), score * 0.8)

        # 3. Category-based tagging
        if "category" in item and item["category"]:
            category_tag = item["category"].lower().replace(" ", "-")
            if category_tag not in existing_tags:
                suggestions[category_tag] = 0.9

        # 4. Extract entities (simple version)
        entities = self._extract_entities(item)
        for entity in entities:
            if entity not in existing_tags:
                suggestions[entity] = suggestions.get(entity, 0) + 0.6

        # Filter by minimum confidence
        filtered_suggestions = {
            tag: score for tag, score in suggestions.items() if score >= min_confidence
        }

        # Sort by confidence
        sorted_suggestions = sorted(filtered_suggestions.items(), key=lambda x: x[1], reverse=True)

        return sorted_suggestions

    def add_rule(self, name: str, condition: callable, tags: List[str], confidence: float = 0.8):
        """Add a custom tagging rule"""
        self.rules.append(
            {
                "name": name,
                "condition": condition,
                "tags": tags,
                "confidence": confidence,
            }
        )
        self.logger.info(f"Added tagging rule: {name}")

    def remove_rule(self, name: str) -> bool:
        """Remove a tagging rule"""
        for i, rule in enumerate(self.rules):
            if rule["name"] == name:
                del self.rules[i]
                self.logger.info(f"Removed tagging rule: {name}")
                return True
        return False

    def _contains_keywords(self, item: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if item contains any of the keywords"""
        text = ""

        # Combine text fields
        for field in ["title", "description", "content", "notes"]:
            if field in item:
                text += " " + str(item[field]).lower()

        # Check keywords
        for keyword in keywords:
            if keyword.lower() in text:
                return True

        return False

    def _is_overdue(self, item: Dict[str, Any]) -> bool:
        """Check if item is overdue"""
        # This is a simplified version
        # In production, compare due_date with current date
        if "due_date" in item and "status" in item:
            if item["status"] not in ["completed", "done"]:
                # Would parse date and compare
                return False
        return False

    def _is_due_soon(self, item: Dict[str, Any], days: int = 3) -> bool:
        """Check if item is due soon"""
        # Simplified version
        # In production, check if due_date is within X days
        return False

    def _extract_entities(self, item: Dict[str, Any]) -> Set[str]:
        """Extract named entities from item (simplified)"""
        entities = set()

        text = ""
        for field in ["title", "description", "content"]:
            if field in item:
                text += " " + str(item[field])

        # Extract capitalized words (potential entities)
        # This is a very simple approach; use NER in production
        words = re.findall(r"\b[A-Z][a-z]+\b", text)

        # Filter common words
        common_words = {
            "The",
            "This",
            "That",
            "With",
            "From",
            "Have",
            "Been",
            "Will",
        }

        for word in words:
            if word not in common_words and len(word) > 2:
                entities.add(word.lower())

        return entities


# Global instance
_auto_tagger: Optional[AutoTagger] = None


def get_auto_tagger() -> AutoTagger:
    """Get global auto-tagger"""
    global _auto_tagger
    if _auto_tagger is None:
        _auto_tagger = AutoTagger()
    return _auto_tagger
