"""
Tag Hierarchy
Hierarchical tag structure with parent-child relationships
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from src.core.logger import setup_logger


class Tag:
    """Represents a tag with hierarchy support"""

    def __init__(
        self,
        id: str,
        name: str,
        parent_id: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.color = color or "#808080"
        self.icon = icon
        self.description = description
        self.metadata = metadata or {}
        self.children: List[str] = []
        self.usage_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "color": self.color,
            "icon": self.icon,
            "description": self.description,
            "metadata": self.metadata,
            "children": self.children,
            "usage_count": self.usage_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Tag":
        """Create from dictionary"""
        tag = cls(
            id=data["id"],
            name=data["name"],
            parent_id=data.get("parent_id"),
            color=data.get("color"),
            icon=data.get("icon"),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )
        tag.children = data.get("children", [])
        tag.usage_count = data.get("usage_count", 0)
        return tag


class TagHierarchy:
    """Manages hierarchical tag structure"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("tags.hierarchy")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "tags"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.tags_file = self.storage_path / "tag_hierarchy.json"

        # Tag storage
        self.tags: Dict[str, Tag] = {}

        # Load tags
        self._load_tags()

    def create_tag(
        self,
        name: str,
        parent_id: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tag:
        """Create a new tag"""
        # Check if tag exists
        existing = self.get_tag_by_name(name, parent_id)
        if existing:
            self.logger.warning(f"Tag '{name}' already exists")
            return existing

        # Validate parent
        if parent_id and parent_id not in self.tags:
            raise ValueError(f"Parent tag '{parent_id}' not found")

        # Generate ID
        tag_id = f"tag_{name.lower().replace(' ', '_')}_{len(self.tags)}"

        tag = Tag(
            id=tag_id,
            name=name,
            parent_id=parent_id,
            color=color,
            icon=icon,
            description=description,
            metadata=metadata,
        )

        self.tags[tag_id] = tag

        # Update parent's children
        if parent_id:
            parent = self.tags[parent_id]
            if tag_id not in parent.children:
                parent.children.append(tag_id)

        self._persist_tags()
        self.logger.info(f"Created tag: {name}")
        return tag

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Get tag by ID"""
        return self.tags.get(tag_id)

    def get_tag_by_name(self, name: str, parent_id: Optional[str] = None) -> Optional[Tag]:
        """Get tag by name and optional parent"""
        for tag in self.tags.values():
            if tag.name == name and tag.parent_id == parent_id:
                return tag
        return None

    def update_tag(
        self,
        tag_id: str,
        name: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update tag properties"""
        if tag_id not in self.tags:
            return False

        tag = self.tags[tag_id]

        if name:
            tag.name = name
        if color:
            tag.color = color
        if icon:
            tag.icon = icon
        if description is not None:
            tag.description = description
        if metadata:
            tag.metadata.update(metadata)

        self._persist_tags()
        self.logger.info(f"Updated tag: {tag_id}")
        return True

    def delete_tag(self, tag_id: str, delete_children: bool = False) -> bool:
        """Delete tag and optionally its children"""
        if tag_id not in self.tags:
            return False

        tag = self.tags[tag_id]

        # Handle children
        if tag.children:
            if delete_children:
                # Recursively delete children
                for child_id in list(tag.children):
                    self.delete_tag(child_id, delete_children=True)
            else:
                # Move children to parent
                for child_id in tag.children:
                    if child_id in self.tags:
                        self.tags[child_id].parent_id = tag.parent_id
                        if tag.parent_id:
                            parent = self.tags[tag.parent_id]
                            if child_id not in parent.children:
                                parent.children.append(child_id)

        # Remove from parent's children
        if tag.parent_id and tag.parent_id in self.tags:
            parent = self.tags[tag.parent_id]
            if tag_id in parent.children:
                parent.children.remove(tag_id)

        # Delete tag
        del self.tags[tag_id]

        self._persist_tags()
        self.logger.info(f"Deleted tag: {tag_id}")
        return True

    def move_tag(self, tag_id: str, new_parent_id: Optional[str]) -> bool:
        """Move tag to new parent"""
        if tag_id not in self.tags:
            return False

        if new_parent_id and new_parent_id not in self.tags:
            return False

        tag = self.tags[tag_id]

        # Check for circular reference
        if new_parent_id and self._would_create_cycle(tag_id, new_parent_id):
            self.logger.error("Cannot move tag: would create circular reference")
            return False

        # Remove from old parent
        if tag.parent_id and tag.parent_id in self.tags:
            old_parent = self.tags[tag.parent_id]
            if tag_id in old_parent.children:
                old_parent.children.remove(tag_id)

        # Add to new parent
        if new_parent_id:
            new_parent = self.tags[new_parent_id]
            if tag_id not in new_parent.children:
                new_parent.children.append(tag_id)

        tag.parent_id = new_parent_id

        self._persist_tags()
        self.logger.info(f"Moved tag {tag_id} to parent {new_parent_id}")
        return True

    def get_children(self, tag_id: str, recursive: bool = False) -> List[Tag]:
        """Get tag's children"""
        if tag_id not in self.tags:
            return []

        tag = self.tags[tag_id]
        children = [self.tags[child_id] for child_id in tag.children if child_id in self.tags]

        if recursive:
            for child in list(children):
                children.extend(self.get_children(child.id, recursive=True))

        return children

    def get_ancestors(self, tag_id: str) -> List[Tag]:
        """Get all ancestors of a tag"""
        if tag_id not in self.tags:
            return []

        ancestors = []
        current = self.tags[tag_id]

        while current.parent_id:
            if current.parent_id not in self.tags:
                break
            parent = self.tags[current.parent_id]
            ancestors.append(parent)
            current = parent

        return ancestors

    def get_path(self, tag_id: str) -> str:
        """Get tag path (e.g., 'Work/Projects/XENO')"""
        if tag_id not in self.tags:
            return ""

        tag = self.tags[tag_id]
        ancestors = self.get_ancestors(tag_id)
        ancestors.reverse()

        path_parts = [a.name for a in ancestors]
        path_parts.append(tag.name)

        return "/".join(path_parts)

    def get_root_tags(self) -> List[Tag]:
        """Get all root-level tags"""
        return [tag for tag in self.tags.values() if tag.parent_id is None]

    def search_tags(self, query: str, case_sensitive: bool = False) -> List[Tag]:
        """Search tags by name"""
        if not case_sensitive:
            query = query.lower()

        results = []
        for tag in self.tags.values():
            tag_name = tag.name if case_sensitive else tag.name.lower()
            if query in tag_name:
                results.append(tag)

        return results

    def increment_usage(self, tag_id: str):
        """Increment tag usage count"""
        if tag_id in self.tags:
            self.tags[tag_id].usage_count += 1
            self._persist_tags()

    def get_popular_tags(self, limit: int = 10) -> List[Tag]:
        """Get most used tags"""
        tags = list(self.tags.values())
        tags.sort(key=lambda t: t.usage_count, reverse=True)
        return tags[:limit]

    def _would_create_cycle(self, tag_id: str, new_parent_id: str) -> bool:
        """Check if moving tag would create circular reference"""
        current_id = new_parent_id
        visited = set()

        while current_id:
            if current_id == tag_id:
                return True
            if current_id in visited:
                break
            visited.add(current_id)

            if current_id not in self.tags:
                break
            current_id = self.tags[current_id].parent_id

        return False

    def _persist_tags(self):
        """Save tags to disk"""
        try:
            data = {
                "tags": {tag_id: tag.to_dict() for tag_id, tag in self.tags.items()},
            }

            with open(self.tags_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist tags: {e}")

    def _load_tags(self):
        """Load tags from disk"""
        if not self.tags_file.exists():
            return

        try:
            with open(self.tags_file, "r") as f:
                data = json.load(f)

            for tag_id, tag_data in data.get("tags", {}).items():
                self.tags[tag_id] = Tag.from_dict(tag_data)

            self.logger.info(f"Loaded {len(self.tags)} tags")

        except Exception as e:
            self.logger.error(f"Failed to load tags: {e}")


# Global instance
_tag_hierarchy: Optional[TagHierarchy] = None


def get_tag_hierarchy() -> TagHierarchy:
    """Get global tag hierarchy"""
    global _tag_hierarchy
    if _tag_hierarchy is None:
        _tag_hierarchy = TagHierarchy()
    return _tag_hierarchy
