"""
Memory System Module
Complete knowledge graph and vector store implementation
"""

# Core components
from src.memory.memory_graph import (
    MemoryGraph,
    MemoryNode,
    MemoryRelationship,
    get_memory_graph,
)
from src.memory.vector_store import (
    MemoryManager,
    VectorStore,
    get_memory_manager,
    recall,
    remember,
)

# Specialized components
from src.memory.conversation_tracker import (
    ConversationContextTracker,
    ConversationSession,
    ConversationTurn,
    get_conversation_tracker,
)
from src.memory.entity_mapper import (
    Entity,
    EntityRelationshipMapper,
    EntityType,
    RelationType,
    get_entity_mapper,
)
from src.memory.memory_persistence import (
    MemoryPersistence,
    get_memory_persistence,
)

__all__ = [
    # Memory Graph
    "MemoryGraph",
    "MemoryNode",
    "MemoryRelationship",
    "get_memory_graph",
    # Vector Store
    "VectorStore",
    "MemoryManager",
    "get_memory_manager",
    "remember",
    "recall",
    # Conversation Tracking
    "ConversationContextTracker",
    "ConversationSession",
    "ConversationTurn",
    "get_conversation_tracker",
    # Entity Mapping
    "EntityRelationshipMapper",
    "Entity",
    "EntityType",
    "RelationType",
    "get_entity_mapper",
    # Persistence
    "MemoryPersistence",
    "get_memory_persistence",
]
