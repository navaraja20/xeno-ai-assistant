"""
Tag Analytics
Analytics and insights for tag usage
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import setup_logger
from src.tags.tag_hierarchy import get_tag_hierarchy


class TagAnalytics:
    """Analytics for tag usage and patterns"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("tags.analytics")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "tags"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.usage_file = self.storage_path / "tag_usage.json"

        # Tag usage tracking
        self.tag_usage: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Load usage data
        self._load_usage()

    def record_tag_usage(
        self, tag_id: str, item_id: str, context: Optional[Dict[str, Any]] = None
    ):
        """Record tag usage"""
        usage_record = {
            "item_id": item_id,
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
        }

        self.tag_usage[tag_id].append(usage_record)

        # Limit history per tag
        if len(self.tag_usage[tag_id]) > 1000:
            self.tag_usage[tag_id] = self.tag_usage[tag_id][-1000:]

        # Update tag usage count in hierarchy
        hierarchy = get_tag_hierarchy()
        hierarchy.increment_usage(tag_id)

        self._persist_usage()

    def get_tag_statistics(self, tag_id: str) -> Dict[str, Any]:
        """Get statistics for a specific tag"""
        hierarchy = get_tag_hierarchy()
        tag = hierarchy.get_tag(tag_id)

        if not tag:
            return {}

        usage_records = self.tag_usage.get(tag_id, [])

        return {
            "tag_id": tag_id,
            "tag_name": tag.name,
            "total_usage": tag.usage_count,
            "usage_records": len(usage_records),
            "first_used": usage_records[0]["timestamp"] if usage_records else None,
            "last_used": usage_records[-1]["timestamp"] if usage_records else None,
            "avg_usage_per_day": self._calculate_avg_usage_per_day(tag_id),
            "children_count": len(tag.children),
            "depth": len(hierarchy.get_ancestors(tag_id)),
            "path": hierarchy.get_path(tag_id),
        }

    def get_usage_trends(
        self, tag_id: str, days: int = 30
    ) -> Dict[str, int]:
        """Get usage trends over time"""
        usage_records = self.tag_usage.get(tag_id, [])
        cutoff_date = datetime.now() - timedelta(days=days)

        # Count usage per day
        daily_usage = defaultdict(int)

        for record in usage_records:
            timestamp = datetime.fromisoformat(record["timestamp"])
            if timestamp >= cutoff_date:
                date_key = timestamp.strftime("%Y-%m-%d")
                daily_usage[date_key] += 1

        return dict(daily_usage)

    def get_top_tags(self, limit: int = 10, days: Optional[int] = None) -> List[Tuple[str, int]]:
        """Get most used tags"""
        hierarchy = get_tag_hierarchy()

        if days is None:
            # All-time top tags
            tags = list(hierarchy.tags.values())
            tags.sort(key=lambda t: t.usage_count, reverse=True)
            return [(tag.name, tag.usage_count) for tag in tags[:limit]]
        else:
            # Recent top tags
            cutoff_date = datetime.now() - timedelta(days=days)
            usage_counts = defaultdict(int)

            for tag_id, records in self.tag_usage.items():
                for record in records:
                    timestamp = datetime.fromisoformat(record["timestamp"])
                    if timestamp >= cutoff_date:
                        tag = hierarchy.get_tag(tag_id)
                        if tag:
                            usage_counts[tag.name] += 1

            sorted_tags = sorted(
                usage_counts.items(), key=lambda x: x[1], reverse=True
            )
            return sorted_tags[:limit]

    def get_unused_tags(self) -> List[str]:
        """Get tags that have never been used"""
        hierarchy = get_tag_hierarchy()
        unused = []

        for tag in hierarchy.tags.values():
            if tag.usage_count == 0:
                unused.append(tag.name)

        return unused

    def get_tag_co_occurrences(
        self, tag_id: str, limit: int = 10
    ) -> List[Tuple[str, int]]:
        """Get tags frequently used together with this tag"""
        hierarchy = get_tag_hierarchy()
        co_occurrences = defaultdict(int)

        # Get items tagged with this tag
        usage_records = self.tag_usage.get(tag_id, [])
        item_ids = {record["item_id"] for record in usage_records}

        # Find other tags used on same items
        for other_tag_id, records in self.tag_usage.items():
            if other_tag_id == tag_id:
                continue

            for record in records:
                if record["item_id"] in item_ids:
                    other_tag = hierarchy.get_tag(other_tag_id)
                    if other_tag:
                        co_occurrences[other_tag.name] += 1

        sorted_co_occurrences = sorted(
            co_occurrences.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_co_occurrences[:limit]

    def get_tag_distribution(self) -> Dict[str, int]:
        """Get distribution of tags by hierarchy level"""
        hierarchy = get_tag_hierarchy()
        distribution = defaultdict(int)

        for tag in hierarchy.tags.values():
            depth = len(hierarchy.get_ancestors(tag.id))
            distribution[f"level_{depth}"] += 1

        return dict(distribution)

    def get_coverage_statistics(self) -> Dict[str, Any]:
        """Get tag coverage statistics"""
        hierarchy = get_tag_hierarchy()

        total_tags = len(hierarchy.tags)
        used_tags = sum(1 for tag in hierarchy.tags.values() if tag.usage_count > 0)
        unused_tags = total_tags - used_tags

        root_tags = len(hierarchy.get_root_tags())
        avg_children = (
            sum(len(tag.children) for tag in hierarchy.tags.values()) / total_tags
            if total_tags > 0
            else 0
        )

        return {
            "total_tags": total_tags,
            "used_tags": used_tags,
            "unused_tags": unused_tags,
            "usage_rate": (used_tags / total_tags * 100) if total_tags > 0 else 0,
            "root_tags": root_tags,
            "avg_children_per_tag": avg_children,
            "max_depth": self._get_max_depth(),
        }

    def export_analytics(self, output_path: str):
        """Export analytics to JSON file"""
        try:
            hierarchy = get_tag_hierarchy()

            data = {
                "coverage": self.get_coverage_statistics(),
                "distribution": self.get_tag_distribution(),
                "top_tags": self.get_top_tags(20),
                "unused_tags": self.get_unused_tags(),
                "tag_statistics": [
                    self.get_tag_statistics(tag_id)
                    for tag_id in list(hierarchy.tags.keys())[:50]
                ],
                "exported_at": datetime.now().isoformat(),
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Exported analytics to {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export analytics: {e}")
            return False

    def _calculate_avg_usage_per_day(self, tag_id: str) -> float:
        """Calculate average usage per day"""
        usage_records = self.tag_usage.get(tag_id, [])

        if not usage_records:
            return 0.0

        first_timestamp = datetime.fromisoformat(usage_records[0]["timestamp"])
        last_timestamp = datetime.fromisoformat(usage_records[-1]["timestamp"])

        days = (last_timestamp - first_timestamp).days + 1
        if days == 0:
            return len(usage_records)

        return len(usage_records) / days

    def _get_max_depth(self) -> int:
        """Get maximum depth of tag hierarchy"""
        hierarchy = get_tag_hierarchy()
        max_depth = 0

        for tag in hierarchy.tags.values():
            depth = len(hierarchy.get_ancestors(tag.id))
            max_depth = max(max_depth, depth)

        return max_depth

    def _persist_usage(self):
        """Save usage data to disk"""
        try:
            data = {
                "tag_usage": {
                    tag_id: records for tag_id, records in self.tag_usage.items()
                },
            }

            with open(self.usage_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist usage: {e}")

    def _load_usage(self):
        """Load usage data from disk"""
        if not self.usage_file.exists():
            return

        try:
            with open(self.usage_file, "r") as f:
                data = json.load(f)

            for tag_id, records in data.get("tag_usage", {}).items():
                self.tag_usage[tag_id] = records

            self.logger.info(f"Loaded usage data for {len(self.tag_usage)} tags")

        except Exception as e:
            self.logger.error(f"Failed to load usage: {e}")


# Global instance
_tag_analytics: Optional[TagAnalytics] = None


def get_tag_analytics() -> TagAnalytics:
    """Get global tag analytics"""
    global _tag_analytics
    if _tag_analytics is None:
        _tag_analytics = TagAnalytics()
    return _tag_analytics
