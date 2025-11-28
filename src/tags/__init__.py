"""
Tags Module
Smart tags and organization
"""

from src.tags.tag_hierarchy import Tag, TagHierarchy, get_tag_hierarchy
from src.tags.tag_suggestions import TagSuggestionEngine, get_tag_suggestion_engine
from src.tags.auto_tagger import AutoTagger, get_auto_tagger
from src.tags.tag_analytics import TagAnalytics, get_tag_analytics

__all__ = [
    # Tag Hierarchy
    "Tag",
    "TagHierarchy",
    "get_tag_hierarchy",
    # Tag Suggestions
    "TagSuggestionEngine",
    "get_tag_suggestion_engine",
    # Auto-Tagging
    "AutoTagger",
    "get_auto_tagger",
    # Tag Analytics
    "TagAnalytics",
    "get_tag_analytics",
]
