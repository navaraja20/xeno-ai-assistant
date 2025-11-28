"""
Memory Graph System - Core Engine
Neo4j-based knowledge graph for contextual memory and relationships
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import setup_logger


class MemoryNode:
    """Node in the memory graph"""

    def __init__(
        self,
        node_id: str,
        node_type: str,
        content: str,
        metadata: Dict[str, Any] = None,
        embedding: List[float] = None,
        created_at: datetime = None,
    ):
        self.node_id = node_id
        self.node_type = node_type  # person, task, event, fact, conversation, etc.
        self.content = content
        self.metadata = metadata or {}
        self.embedding = embedding or []
        self.created_at = created_at or datetime.now()
        self.accessed_count = 0
        self.last_accessed = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
            "accessed_count": self.accessed_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }


class MemoryRelationship:
    """Relationship between nodes"""

    def __init__(
        self,
        from_node: str,
        to_node: str,
        rel_type: str,
        properties: Dict[str, Any] = None,
        strength: float = 1.0,
    ):
        self.from_node = from_node
        self.to_node = to_node
        self.rel_type = rel_type  # related_to, mentioned_in, precedes, causes, etc.
        self.properties = properties or {}
        self.strength = strength  # 0-1 relationship strength
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "rel_type": self.rel_type,
            "properties": self.properties,
            "strength": self.strength,
            "created_at": self.created_at.isoformat(),
        }


class MemoryGraph:
    """In-memory knowledge graph (Neo4j-compatible structure)"""

    def __init__(self):
        self.logger = setup_logger("memory.graph")
        self.nodes: Dict[str, MemoryNode] = {}
        self.relationships: List[MemoryRelationship] = []

        # Indexes for fast lookup
        self.nodes_by_type: Dict[str, List[str]] = {}
        self.relationships_index: Dict[str, List[MemoryRelationship]] = {}

    def add_node(self, node: MemoryNode) -> bool:
        """Add node to graph"""
        try:
            self.nodes[node.node_id] = node

            # Update type index
            if node.node_type not in self.nodes_by_type:
                self.nodes_by_type[node.node_type] = []
            self.nodes_by_type[node.node_type].append(node.node_id)

            self.logger.debug(f"Added node: {node.node_id} ({node.node_type})")
            return True
        except Exception as e:
            self.logger.error(f"Error adding node: {e}")
            return False

    def add_relationship(self, rel: MemoryRelationship) -> bool:
        """Add relationship to graph"""
        try:
            # Verify nodes exist
            if rel.from_node not in self.nodes or rel.to_node not in self.nodes:
                self.logger.error("Cannot add relationship: nodes don't exist")
                return False

            self.relationships.append(rel)

            # Update relationship index
            if rel.from_node not in self.relationships_index:
                self.relationships_index[rel.from_node] = []
            self.relationships_index[rel.from_node].append(rel)

            self.logger.debug(
                f"Added relationship: {rel.from_node} -[{rel.rel_type}]-> {rel.to_node}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Error adding relationship: {e}")
            return False

    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        """Get node by ID"""
        node = self.nodes.get(node_id)
        if node:
            node.accessed_count += 1
            node.last_accessed = datetime.now()
        return node

    def get_nodes_by_type(self, node_type: str) -> List[MemoryNode]:
        """Get all nodes of a specific type"""
        node_ids = self.nodes_by_type.get(node_type, [])
        return [self.nodes[nid] for nid in node_ids if nid in self.nodes]

    def get_relationships(
        self, node_id: str, direction: str = "outgoing"
    ) -> List[MemoryRelationship]:
        """Get relationships for a node"""
        if direction == "outgoing":
            return self.relationships_index.get(node_id, [])
        elif direction == "incoming":
            return [r for r in self.relationships if r.to_node == node_id]
        else:  # both
            outgoing = self.relationships_index.get(node_id, [])
            incoming = [r for r in self.relationships if r.to_node == node_id]
            return outgoing + incoming

    def find_path(
        self, from_node: str, to_node: str, max_depth: int = 3
    ) -> Optional[List[str]]:
        """Find shortest path between two nodes (BFS)"""
        if from_node not in self.nodes or to_node not in self.nodes:
            return None

        if from_node == to_node:
            return [from_node]

        visited = set()
        queue = [(from_node, [from_node])]

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            if current in visited:
                continue

            visited.add(current)

            # Get neighboring nodes
            rels = self.get_relationships(current, "outgoing")
            for rel in rels:
                neighbor = rel.to_node

                if neighbor == to_node:
                    return path + [neighbor]

                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_connected_subgraph(
        self, node_id: str, max_depth: int = 2
    ) -> Tuple[List[MemoryNode], List[MemoryRelationship]]:
        """Get subgraph centered around a node"""
        if node_id not in self.nodes:
            return [], []

        visited_nodes = set([node_id])
        visited_rels = []

        queue = [(node_id, 0)]

        while queue:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get relationships
            rels = self.get_relationships(current, "both")

            for rel in rels:
                if rel not in visited_rels:
                    visited_rels.append(rel)

                # Add connected nodes
                for neighbor in [rel.from_node, rel.to_node]:
                    if neighbor not in visited_nodes:
                        visited_nodes.add(neighbor)
                        queue.append((neighbor, depth + 1))

        nodes = [self.nodes[nid] for nid in visited_nodes if nid in self.nodes]
        return nodes, visited_rels

    def search_nodes(
        self, query: str, node_type: Optional[str] = None, limit: int = 10
    ) -> List[MemoryNode]:
        """Search nodes by content"""
        query_lower = query.lower()
        results = []

        for node in self.nodes.values():
            if node_type and node.node_type != node_type:
                continue

            if query_lower in node.content.lower():
                results.append(node)

        # Sort by relevance (exact match first, then by access count)
        results.sort(
            key=lambda n: (
                query_lower != n.content.lower(),
                -n.accessed_count,
            )
        )

        return results[:limit]

    def get_most_accessed_nodes(self, limit: int = 10) -> List[MemoryNode]:
        """Get most frequently accessed nodes"""
        nodes = sorted(self.nodes.values(), key=lambda n: n.accessed_count, reverse=True)
        return nodes[:limit]

    def get_recent_nodes(self, limit: int = 10) -> List[MemoryNode]:
        """Get most recently created nodes"""
        nodes = sorted(self.nodes.values(), key=lambda n: n.created_at, reverse=True)
        return nodes[:limit]

    def strengthen_relationship(self, from_node: str, to_node: str, amount: float = 0.1):
        """Strengthen a relationship between nodes"""
        for rel in self.relationships:
            if rel.from_node == from_node and rel.to_node == to_node:
                rel.strength = min(1.0, rel.strength + amount)
                self.logger.debug(f"Strengthened relationship: {rel.strength:.2f}")
                return True
        return False

    def weaken_relationship(self, from_node: str, to_node: str, amount: float = 0.1):
        """Weaken a relationship between nodes"""
        for rel in self.relationships:
            if rel.from_node == from_node and rel.to_node == to_node:
                rel.strength = max(0.0, rel.strength - amount)
                self.logger.debug(f"Weakened relationship: {rel.strength:.2f}")
                return True
        return False

    def prune_weak_relationships(self, threshold: float = 0.3):
        """Remove weak relationships below threshold"""
        before_count = len(self.relationships)
        self.relationships = [r for r in self.relationships if r.strength >= threshold]
        after_count = len(self.relationships)

        pruned = before_count - after_count
        if pruned > 0:
            self.logger.info(f"Pruned {pruned} weak relationships")

        # Rebuild index
        self.relationships_index = {}
        for rel in self.relationships:
            if rel.from_node not in self.relationships_index:
                self.relationships_index[rel.from_node] = []
            self.relationships_index[rel.from_node].append(rel)

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        return {
            "total_nodes": len(self.nodes),
            "total_relationships": len(self.relationships),
            "node_types": {
                node_type: len(node_ids)
                for node_type, node_ids in self.nodes_by_type.items()
            },
            "avg_connections_per_node": (
                len(self.relationships) / len(self.nodes) if self.nodes else 0
            ),
        }

    def export_to_json(self) -> str:
        """Export graph to JSON"""
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "stats": self.get_stats(),
            },
        }
        return json.dumps(data, indent=2)

    def import_from_json(self, json_data: str):
        """Import graph from JSON"""
        try:
            data = json.loads(json_data)

            # Clear existing data
            self.nodes = {}
            self.relationships = []
            self.nodes_by_type = {}
            self.relationships_index = {}

            # Import nodes
            for node_data in data["nodes"]:
                node = MemoryNode(
                    node_id=node_data["node_id"],
                    node_type=node_data["node_type"],
                    content=node_data["content"],
                    metadata=node_data.get("metadata", {}),
                    embedding=node_data.get("embedding", []),
                    created_at=datetime.fromisoformat(node_data["created_at"]),
                )
                node.accessed_count = node_data.get("accessed_count", 0)
                if node_data.get("last_accessed"):
                    node.last_accessed = datetime.fromisoformat(node_data["last_accessed"])

                self.add_node(node)

            # Import relationships
            for rel_data in data["relationships"]:
                rel = MemoryRelationship(
                    from_node=rel_data["from_node"],
                    to_node=rel_data["to_node"],
                    rel_type=rel_data["rel_type"],
                    properties=rel_data.get("properties", {}),
                    strength=rel_data.get("strength", 1.0),
                )
                rel.created_at = datetime.fromisoformat(rel_data["created_at"])

                self.add_relationship(rel)

            self.logger.info(f"Imported graph with {len(self.nodes)} nodes")

        except Exception as e:
            self.logger.error(f"Error importing graph: {e}")


# Global instance
_memory_graph: Optional[MemoryGraph] = None


def get_memory_graph() -> MemoryGraph:
    """Get global memory graph"""
    global _memory_graph
    if _memory_graph is None:
        _memory_graph = MemoryGraph()
    return _memory_graph
