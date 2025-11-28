"""
Vector Memory Store - ChromaDB Integration
Semantic search and embedding-based memory retrieval
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.core.logger import setup_logger


class VectorStore:
    """Vector-based memory store (ChromaDB-compatible)"""

    def __init__(self, persist_dir: str = "data/vector_store"):
        self.logger = setup_logger("memory.vector")
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage (simulating ChromaDB)
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}

        # Collections (like ChromaDB collections)
        self.collections: Dict[str, List[str]] = {
            "conversations": [],
            "facts": [],
            "tasks": [],
            "events": [],
            "people": [],
            "code": [],
        }

        self._load_from_disk()

    def add_document(
        self,
        doc_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None,
        collection: str = "conversations",
    ) -> bool:
        """Add document with embedding"""
        try:
            self.documents[doc_id] = {
                "content": content,
                "collection": collection,
                "created_at": datetime.now().isoformat(),
            }

            self.embeddings[doc_id] = np.array(embedding, dtype=np.float32)
            self.metadata[doc_id] = metadata or {}

            # Add to collection
            if collection not in self.collections:
                self.collections[collection] = []
            if doc_id not in self.collections[collection]:
                self.collections[collection].append(doc_id)

            self.logger.debug(f"Added document: {doc_id} to collection: {collection}")
            self._save_to_disk()
            return True

        except Exception as e:
            self.logger.error(f"Error adding document: {e}")
            return False

    def search(
        self,
        query_embedding: List[float],
        collection: Optional[str] = None,
        limit: int = 5,
        threshold: float = 0.7,
    ) -> List[Tuple[str, float, str]]:
        """Semantic search using cosine similarity"""

        if not self.embeddings:
            return []

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)

        if query_norm == 0:
            return []

        # Filter by collection
        doc_ids = []
        if collection and collection in self.collections:
            doc_ids = self.collections[collection]
        else:
            doc_ids = list(self.documents.keys())

        # Calculate similarities
        similarities = []

        for doc_id in doc_ids:
            if doc_id not in self.embeddings:
                continue

            doc_vec = self.embeddings[doc_id]
            doc_norm = np.linalg.norm(doc_vec)

            if doc_norm == 0:
                continue

            # Cosine similarity
            similarity = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)

            if similarity >= threshold:
                content = self.documents[doc_id]["content"]
                similarities.append((doc_id, float(similarity), content))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:limit]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        if doc_id not in self.documents:
            return None

        return {
            "content": self.documents[doc_id]["content"],
            "metadata": self.metadata.get(doc_id, {}),
            "embedding": self.embeddings.get(doc_id, []).tolist(),
        }

    def update_metadata(self, doc_id: str, metadata: Dict[str, Any]) -> bool:
        """Update document metadata"""
        if doc_id not in self.documents:
            return False

        self.metadata[doc_id].update(metadata)
        self._save_to_disk()
        return True

    def delete_document(self, doc_id: str) -> bool:
        """Delete document"""
        if doc_id not in self.documents:
            return False

        collection = self.documents[doc_id]["collection"]

        del self.documents[doc_id]
        if doc_id in self.embeddings:
            del self.embeddings[doc_id]
        if doc_id in self.metadata:
            del self.metadata[doc_id]

        # Remove from collection
        if collection in self.collections and doc_id in self.collections[collection]:
            self.collections[collection].remove(doc_id)

        self._save_to_disk()
        return True

    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        if collection not in self.collections:
            return {"count": 0, "collection": collection}

        doc_ids = self.collections[collection]

        return {
            "collection": collection,
            "count": len(doc_ids),
            "documents": [
                {
                    "id": doc_id,
                    "content_preview": self.documents[doc_id]["content"][:100] + "...",
                    "created_at": self.documents[doc_id]["created_at"],
                }
                for doc_id in doc_ids[:10]  # Preview first 10
            ],
        }

    def find_similar_documents(self, doc_id: str, limit: int = 5) -> List[Tuple[str, float, str]]:
        """Find documents similar to a given document"""
        if doc_id not in self.embeddings:
            return []

        query_embedding = self.embeddings[doc_id].tolist()
        collection = self.documents[doc_id]["collection"]

        results = self.search(query_embedding, collection, limit + 1, threshold=0.5)

        # Remove the query document itself
        return [(id, score, content) for id, score, content in results if id != doc_id]

    def create_embedding(self, text: str) -> List[float]:
        """Create simple embedding (placeholder - replace with actual model)"""
        # This is a simple hash-based embedding for demonstration
        # In production, use sentence-transformers, OpenAI embeddings, etc.

        # Use MD5 hash to create deterministic vector
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()

        # Convert to 384-dimensional vector (common embedding size)
        embedding = []
        for i in range(384):
            byte_idx = i % len(hash_bytes)
            embedding.append(float(hash_bytes[byte_idx]) / 255.0)

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def _save_to_disk(self):
        """Persist to disk"""
        try:
            data = {
                "documents": self.documents,
                "metadata": self.metadata,
                "collections": self.collections,
                "embeddings": {doc_id: emb.tolist() for doc_id, emb in self.embeddings.items()},
            }

            with open(self.persist_dir / "vector_store.json", "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving to disk: {e}")

    def _load_from_disk(self):
        """Load from disk"""
        try:
            store_file = self.persist_dir / "vector_store.json"
            if not store_file.exists():
                return

            with open(store_file, "r") as f:
                data = json.load(f)

            self.documents = data.get("documents", {})
            self.metadata = data.get("metadata", {})
            self.collections = data.get("collections", {})

            # Convert embeddings back to numpy arrays
            embeddings_data = data.get("embeddings", {})
            for doc_id, emb_list in embeddings_data.items():
                self.embeddings[doc_id] = np.array(emb_list, dtype=np.float32)

            self.logger.info(f"Loaded {len(self.documents)} documents from disk")

        except Exception as e:
            self.logger.error(f"Error loading from disk: {e}")


class MemoryManager:
    """High-level memory management combining graph and vector stores"""

    def __init__(self):
        self.logger = setup_logger("memory.manager")
        self.vector_store = VectorStore()

        # Import graph
        from src.memory.memory_graph import get_memory_graph

        self.graph = get_memory_graph()

    def remember(
        self,
        content: str,
        memory_type: str = "fact",
        metadata: Dict[str, Any] = None,
        related_to: List[str] = None,
    ) -> str:
        """Store a memory (both graph and vector)"""

        # Generate ID
        memory_id = f"{memory_type}_{datetime.now().timestamp()}"

        # Create embedding
        embedding = self.vector_store.create_embedding(content)

        # Store in vector database
        self.vector_store.add_document(
            doc_id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            collection=memory_type + "s",  # conversations, facts, tasks, etc.
        )

        # Store in graph
        from src.memory.memory_graph import MemoryNode, MemoryRelationship

        node = MemoryNode(
            node_id=memory_id,
            node_type=memory_type,
            content=content,
            metadata=metadata or {},
            embedding=embedding,
        )
        self.graph.add_node(node)

        # Create relationships
        if related_to:
            for related_id in related_to:
                rel = MemoryRelationship(
                    from_node=memory_id,
                    to_node=related_id,
                    rel_type="related_to",
                    strength=0.8,
                )
                self.graph.add_relationship(rel)

        self.logger.info(f"Stored memory: {memory_id} ({memory_type})")
        return memory_id

    def recall(
        self,
        query: str,
        memory_type: Optional[str] = None,
        limit: int = 5,
        use_graph: bool = True,
    ) -> List[Dict[str, Any]]:
        """Recall memories based on query"""

        # Vector search
        query_embedding = self.vector_store.create_embedding(query)
        collection = memory_type + "s" if memory_type else None

        results = self.vector_store.search(
            query_embedding, collection=collection, limit=limit, threshold=0.6
        )

        memories = []

        for doc_id, score, content in results:
            memory = {
                "id": doc_id,
                "content": content,
                "similarity": score,
                "metadata": self.vector_store.metadata.get(doc_id, {}),
            }

            # Enrich with graph data if requested
            if use_graph:
                node = self.graph.get_node(doc_id)
                if node:
                    memory["accessed_count"] = node.accessed_count
                    memory["last_accessed"] = (
                        node.last_accessed.isoformat() if node.last_accessed else None
                    )

                    # Get related memories
                    rels = self.graph.get_relationships(doc_id, "both")
                    memory["related_count"] = len(rels)

            memories.append(memory)

        return memories

    def get_context(self, memory_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get contextual information around a memory"""

        # Get from vector store
        doc = self.vector_store.get_document(memory_id)

        if not doc:
            return {}

        # Get from graph
        nodes, rels = self.graph.get_connected_subgraph(memory_id, max_depth=depth)

        return {
            "memory": doc,
            "connected_memories": [
                {
                    "id": n.node_id,
                    "type": n.node_type,
                    "content": n.content[:100] + "...",
                }
                for n in nodes
                if n.node_id != memory_id
            ],
            "relationships": [
                {"from": r.from_node, "to": r.to_node, "type": r.rel_type} for r in rels
            ],
        }

    def find_connections(self, memory_id1: str, memory_id2: str) -> Optional[List[str]]:
        """Find connection path between two memories"""
        return self.graph.find_path(memory_id1, memory_id2)

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        return {
            "graph_stats": self.graph.get_stats(),
            "vector_stats": {
                collection: self.vector_store.get_collection_stats(collection)["count"]
                for collection in self.vector_store.collections.keys()
            },
            "total_memories": len(self.vector_store.documents),
        }


# Global instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get global memory manager"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


# Convenience functions
def remember(content: str, memory_type: str = "fact", **kwargs) -> str:
    """Quick function to store a memory"""
    return get_memory_manager().remember(content, memory_type, **kwargs)


def recall(query: str, **kwargs) -> List[Dict[str, Any]]:
    """Quick function to recall memories"""
    return get_memory_manager().recall(query, **kwargs)
