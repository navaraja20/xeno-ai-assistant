"""
Entity Relationship Mapper
Extracts and maps entities and their relationships from conversations and tasks
"""

import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from src.core.logger import setup_logger
from src.memory.memory_graph import MemoryNode, MemoryRelationship, get_memory_graph


class EntityType(Enum):
    """Types of entities"""

    PERSON = "person"
    ORGANIZATION = "organization"
    PROJECT = "project"
    TASK = "task"
    EVENT = "event"
    LOCATION = "location"
    DOCUMENT = "document"
    CONCEPT = "concept"
    TOOL = "tool"
    UNKNOWN = "unknown"


class RelationType(Enum):
    """Types of relationships"""

    WORKS_FOR = "works_for"
    WORKS_WITH = "works_with"
    MANAGES = "manages"
    PART_OF = "part_of"
    LOCATED_IN = "located_in"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    CREATED_BY = "created_by"
    MENTIONED_WITH = "mentioned_with"
    PRECEDES = "precedes"


class Entity:
    """Represents an entity"""

    def __init__(
        self,
        entity_id: str,
        name: str,
        entity_type: EntityType,
        attributes: Dict[str, Any] = None,
    ):
        self.entity_id = entity_id
        self.name = name
        self.entity_type = entity_type
        self.attributes = attributes or {}
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.mention_count = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "type": self.entity_type.value,
            "attributes": self.attributes,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "mention_count": self.mention_count,
        }


class EntityRelationshipMapper:
    """Maps entities and their relationships"""

    def __init__(self):
        self.logger = setup_logger("memory.entity_mapper")
        self.graph = get_memory_graph()

        # Entity tracking
        self.entities: Dict[str, Entity] = {}
        self.entity_name_index: Dict[str, str] = {}  # name -> entity_id

        # Common patterns
        self.person_patterns = [
            r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # John Doe
            r"\b(?:Mr|Ms|Mrs|Dr|Prof)\.? [A-Z][a-z]+\b",  # Mr. Smith
        ]

        self.organization_patterns = [
            r"\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company)\b",
            r"\b(?:Microsoft|Google|Apple|Amazon|Facebook)\b",
        ]

        self.email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        entities = []

        # Extract people
        for pattern in self.person_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(0)
                entity = self._get_or_create_entity(name, EntityType.PERSON)
                entities.append(entity)

        # Extract organizations
        for pattern in self.organization_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(0)
                entity = self._get_or_create_entity(name, EntityType.ORGANIZATION)
                entities.append(entity)

        # Extract emails
        emails = re.finditer(self.email_pattern, text)
        for match in emails:
            email = match.group(0)
            # Create person entity from email
            name = email.split("@")[0].replace(".", " ").title()
            entity = self._get_or_create_entity(
                name, EntityType.PERSON, {"email": email}
            )
            entities.append(entity)

        # Extract projects (capitalized multi-word phrases)
        project_pattern = r"\b(?:Project|Initiative) [A-Z][a-zA-Z ]{2,15}\b"
        projects = re.finditer(project_pattern, text)
        for match in projects:
            name = match.group(0)
            entity = self._get_or_create_entity(name, EntityType.PROJECT)
            entities.append(entity)

        return entities

    def _get_or_create_entity(
        self, name: str, entity_type: EntityType, attributes: Dict[str, Any] = None
    ) -> Entity:
        """Get existing entity or create new one"""

        # Normalize name
        normalized_name = name.strip()

        # Check if entity exists
        if normalized_name in self.entity_name_index:
            entity_id = self.entity_name_index[normalized_name]
            entity = self.entities[entity_id]
            entity.last_seen = datetime.now()
            entity.mention_count += 1

            # Update attributes
            if attributes:
                entity.attributes.update(attributes)

            return entity

        # Create new entity
        entity_id = f"{entity_type.value}_{len(self.entities)}"
        entity = Entity(entity_id, normalized_name, entity_type, attributes)

        self.entities[entity_id] = entity
        self.entity_name_index[normalized_name] = entity_id

        # Add to graph
        node = MemoryNode(
            node_id=entity_id,
            node_type=entity_type.value,
            content=normalized_name,
            metadata=entity.to_dict(),
        )
        self.graph.add_node(node)

        self.logger.debug(f"Created entity: {normalized_name} ({entity_type.value})")
        return entity

    def create_relationship(
        self,
        entity1: Entity,
        entity2: Entity,
        rel_type: RelationType,
        strength: float = 0.5,
        metadata: Dict[str, Any] = None,
    ):
        """Create relationship between entities"""

        rel = MemoryRelationship(
            from_node=entity1.entity_id,
            to_node=entity2.entity_id,
            rel_type=rel_type.value,
            properties=metadata or {},
            strength=strength,
        )

        self.graph.add_relationship(rel)
        self.logger.debug(
            f"Created relationship: {entity1.name} -[{rel_type.value}]-> {entity2.name}"
        )

    def analyze_text(self, text: str, source_id: str = None) -> Dict[str, Any]:
        """Analyze text and extract entities and relationships"""

        # Extract entities
        entities = self.extract_entities(text)

        # Infer relationships (co-occurrence)
        relationships = []
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1 :]:
                # Entities mentioned together are related
                self.create_relationship(
                    entity1,
                    entity2,
                    RelationType.MENTIONED_WITH,
                    strength=0.3,
                    metadata={"source": source_id} if source_id else {},
                )

                relationships.append(
                    {
                        "from": entity1.name,
                        "to": entity2.name,
                        "type": RelationType.MENTIONED_WITH.value,
                    }
                )

        # Detect work relationships
        work_patterns = [
            (r"(\w+) works (?:for|at) (\w+)", RelationType.WORKS_FOR),
            (r"(\w+) manages (\w+)", RelationType.MANAGES),
            (r"(\w+) and (\w+) collaborate", RelationType.WORKS_WITH),
        ]

        for pattern, rel_type in work_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name1, name2 = match.group(1), match.group(2)

                # Find entities
                entity1 = self.entity_name_index.get(name1)
                entity2 = self.entity_name_index.get(name2)

                if entity1 and entity2:
                    self.create_relationship(
                        self.entities[entity1],
                        self.entities[entity2],
                        rel_type,
                        strength=0.8,
                    )

        return {
            "entities_found": len(entities),
            "entities": [e.to_dict() for e in entities],
            "relationships_created": len(relationships),
            "relationships": relationships,
        }

    def get_entity(self, name: str) -> Optional[Entity]:
        """Get entity by name"""
        entity_id = self.entity_name_index.get(name.strip())
        return self.entities.get(entity_id) if entity_id else None

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type"""
        return [e for e in self.entities.values() if e.entity_type == entity_type]

    def get_related_entities(
        self, entity: Entity, rel_type: Optional[RelationType] = None
    ) -> List[Tuple[Entity, str, float]]:
        """Get entities related to given entity"""

        # Get relationships from graph
        rels = self.graph.get_relationships(entity.entity_id, "both")

        related = []
        for rel in rels:
            if rel_type and rel.rel_type != rel_type.value:
                continue

            # Get the other entity
            other_id = (
                rel.to_node if rel.from_node == entity.entity_id else rel.from_node
            )
            other_entity = self.entities.get(other_id)

            if other_entity:
                related.append((other_entity, rel.rel_type, rel.strength))

        return related

    def get_entity_network(
        self, entity: Entity, max_depth: int = 2
    ) -> Dict[str, Any]:
        """Get network of entities around a central entity"""

        nodes, rels = self.graph.get_connected_subgraph(entity.entity_id, max_depth)

        # Convert to entity objects
        entities = []
        for node in nodes:
            if node.node_id in self.entities:
                entities.append(self.entities[node.node_id].to_dict())

        relationships = [
            {
                "from": r.from_node,
                "to": r.to_node,
                "type": r.rel_type,
                "strength": r.strength,
            }
            for r in rels
        ]

        return {
            "center": entity.to_dict(),
            "entities": entities,
            "relationships": relationships,
            "total_entities": len(entities),
            "total_relationships": len(relationships),
        }

    def get_most_mentioned_entities(self, limit: int = 10) -> List[Entity]:
        """Get most frequently mentioned entities"""
        entities = sorted(
            self.entities.values(), key=lambda e: e.mention_count, reverse=True
        )
        return entities[:limit]

    def get_recent_entities(self, limit: int = 10) -> List[Entity]:
        """Get most recently seen entities"""
        entities = sorted(
            self.entities.values(), key=lambda e: e.last_seen, reverse=True
        )
        return entities[:limit]

    def merge_entities(self, entity1_id: str, entity2_id: str) -> bool:
        """Merge two entities (e.g., discovered they're the same)"""

        if entity1_id not in self.entities or entity2_id not in self.entities:
            return False

        entity1 = self.entities[entity1_id]
        entity2 = self.entities[entity2_id]

        # Merge attributes
        entity1.attributes.update(entity2.attributes)
        entity1.mention_count += entity2.mention_count

        # Update name index
        if entity2.name in self.entity_name_index:
            del self.entity_name_index[entity2.name]

        # Transfer relationships
        rels = self.graph.get_relationships(entity2_id, "both")
        for rel in rels:
            if rel.from_node == entity2_id:
                new_rel = MemoryRelationship(
                    from_node=entity1_id,
                    to_node=rel.to_node,
                    rel_type=rel.rel_type,
                    properties=rel.properties,
                    strength=rel.strength,
                )
                self.graph.add_relationship(new_rel)
            elif rel.to_node == entity2_id:
                new_rel = MemoryRelationship(
                    from_node=rel.from_node,
                    to_node=entity1_id,
                    rel_type=rel.rel_type,
                    properties=rel.properties,
                    strength=rel.strength,
                )
                self.graph.add_relationship(new_rel)

        # Remove entity2
        del self.entities[entity2_id]

        self.logger.info(f"Merged entities: {entity2.name} -> {entity1.name}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get entity statistics"""
        entity_counts = {}
        for entity_type in EntityType:
            count = len(self.get_entities_by_type(entity_type))
            if count > 0:
                entity_counts[entity_type.value] = count

        return {
            "total_entities": len(self.entities),
            "entity_types": entity_counts,
            "most_mentioned": [
                e.to_dict() for e in self.get_most_mentioned_entities(5)
            ],
        }


# Global instance
_entity_mapper: Optional[EntityRelationshipMapper] = None


def get_entity_mapper() -> EntityRelationshipMapper:
    """Get global entity mapper"""
    global _entity_mapper
    if _entity_mapper is None:
        _entity_mapper = EntityRelationshipMapper()
    return _entity_mapper
