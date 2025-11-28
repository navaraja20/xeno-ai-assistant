"""
Memory Persistence Manager
Handles saving and loading of memory graph and vector store
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.core.logger import setup_logger
from src.memory.conversation_tracker import get_conversation_tracker
from src.memory.entity_mapper import get_entity_mapper
from src.memory.memory_graph import get_memory_graph
from src.memory.vector_store import get_memory_manager


class MemoryPersistence:
    """Manages persistence of all memory components"""

    def __init__(self, data_dir: str = "data/memory"):
        self.logger = setup_logger("memory.persistence")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.graph_file = self.data_dir / "memory_graph.json"
        self.conversations_file = self.data_dir / "conversations.json"
        self.entities_file = self.data_dir / "entities.json"
        self.metadata_file = self.data_dir / "metadata.json"

    def save_all(self) -> bool:
        """Save all memory components"""
        try:
            self.logger.info("Saving all memory components...")

            # Save graph
            self._save_graph()

            # Save conversations
            self._save_conversations()

            # Save entities
            self._save_entities()

            # Save metadata
            self._save_metadata()

            self.logger.info("All memory components saved successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error saving memory: {e}")
            return False

    def load_all(self) -> bool:
        """Load all memory components"""
        try:
            self.logger.info("Loading all memory components...")

            # Load graph
            self._load_graph()

            # Load conversations
            self._load_conversations()

            # Load entities
            self._load_entities()

            self.logger.info("All memory components loaded successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error loading memory: {e}")
            return False

    def _save_graph(self):
        """Save memory graph"""
        graph = get_memory_graph()
        graph_json = graph.export_to_json()

        with open(self.graph_file, "w") as f:
            f.write(graph_json)

        self.logger.debug(f"Saved graph to {self.graph_file}")

    def _load_graph(self):
        """Load memory graph"""
        if not self.graph_file.exists():
            self.logger.debug("No graph file found, starting fresh")
            return

        with open(self.graph_file, "r") as f:
            graph_json = f.read()

        graph = get_memory_graph()
        graph.import_from_json(graph_json)

        self.logger.debug(f"Loaded graph from {self.graph_file}")

    def _save_conversations(self):
        """Save conversation history"""
        tracker = get_conversation_tracker()

        data = {
            "sessions": {
                session_id: session.to_dict()
                for session_id, session in tracker.sessions.items()
            },
            "current_session_id": (
                tracker.current_session.session_id if tracker.current_session else None
            ),
        }

        with open(self.conversations_file, "w") as f:
            json.dump(data, f, indent=2)

        self.logger.debug(f"Saved conversations to {self.conversations_file}")

    def _load_conversations(self):
        """Load conversation history"""
        if not self.conversations_file.exists():
            self.logger.debug("No conversations file found, starting fresh")
            return

        with open(self.conversations_file, "r") as f:
            data = json.load(f)

        tracker = get_conversation_tracker()

        # Reconstruct sessions
        from src.memory.conversation_tracker import ConversationSession, ConversationTurn

        for session_id, session_data in data["sessions"].items():
            session = ConversationSession(session_id, session_data["topic"])
            session.started_at = datetime.fromisoformat(session_data["started_at"])
            if session_data["ended_at"]:
                session.ended_at = datetime.fromisoformat(session_data["ended_at"])
            session.summary = session_data.get("summary")
            session.key_facts = session_data.get("key_facts", [])

            # Reconstruct turns
            for turn_data in session_data["turns"]:
                turn = ConversationTurn(
                    turn_id=turn_data["turn_id"],
                    speaker=turn_data["speaker"],
                    content=turn_data["content"],
                    timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                    metadata=turn_data.get("metadata", {}),
                )
                session.add_turn(turn)

            tracker.sessions[session_id] = session

        # Restore current session
        current_session_id = data.get("current_session_id")
        if current_session_id and current_session_id in tracker.sessions:
            tracker.current_session = tracker.sessions[current_session_id]

        self.logger.debug(f"Loaded conversations from {self.conversations_file}")

    def _save_entities(self):
        """Save entity mapper data"""
        mapper = get_entity_mapper()

        data = {
            "entities": {
                entity_id: entity.to_dict()
                for entity_id, entity in mapper.entities.items()
            },
            "entity_name_index": mapper.entity_name_index,
        }

        with open(self.entities_file, "w") as f:
            json.dump(data, f, indent=2)

        self.logger.debug(f"Saved entities to {self.entities_file}")

    def _load_entities(self):
        """Load entity mapper data"""
        if not self.entities_file.exists():
            self.logger.debug("No entities file found, starting fresh")
            return

        with open(self.entities_file, "r") as f:
            data = json.load(f)

        mapper = get_entity_mapper()

        # Reconstruct entities
        from src.memory.entity_mapper import Entity, EntityType

        for entity_id, entity_data in data["entities"].items():
            entity = Entity(
                entity_id=entity_id,
                name=entity_data["name"],
                entity_type=EntityType(entity_data["type"]),
                attributes=entity_data.get("attributes", {}),
            )
            entity.first_seen = datetime.fromisoformat(entity_data["first_seen"])
            entity.last_seen = datetime.fromisoformat(entity_data["last_seen"])
            entity.mention_count = entity_data.get("mention_count", 1)

            mapper.entities[entity_id] = entity

        mapper.entity_name_index = data.get("entity_name_index", {})

        self.logger.debug(f"Loaded entities from {self.entities_file}")

    def _save_metadata(self):
        """Save metadata about memory system"""
        graph = get_memory_graph()
        tracker = get_conversation_tracker()
        mapper = get_entity_mapper()

        metadata = {
            "last_save": datetime.now().isoformat(),
            "graph_stats": graph.get_stats(),
            "conversation_stats": tracker.get_statistics(),
            "entity_stats": mapper.get_statistics(),
        }

        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        self.logger.debug(f"Saved metadata to {self.metadata_file}")

    def auto_save_enabled(self, interval_minutes: int = 5):
        """Enable automatic saving at intervals"""
        # This would typically use a background thread/timer
        # For now, just log the intent
        self.logger.info(f"Auto-save would run every {interval_minutes} minutes")

    def export_memory_dump(self, output_file: str = None) -> str:
        """Export complete memory dump for backup"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.data_dir / f"memory_dump_{timestamp}.json")

        graph = get_memory_graph()
        tracker = get_conversation_tracker()
        mapper = get_entity_mapper()
        manager = get_memory_manager()

        dump = {
            "export_timestamp": datetime.now().isoformat(),
            "graph": json.loads(graph.export_to_json()),
            "conversations": {
                session_id: session.to_dict()
                for session_id, session in tracker.sessions.items()
            },
            "entities": {
                entity_id: entity.to_dict()
                for entity_id, entity in mapper.entities.items()
            },
            "vector_store": {
                "documents": manager.vector_store.documents,
                "metadata": manager.vector_store.metadata,
                "collections": manager.vector_store.collections,
            },
        }

        with open(output_file, "w") as f:
            json.dump(dump, f, indent=2)

        self.logger.info(f"Exported memory dump to {output_file}")
        return output_file

    def import_memory_dump(self, dump_file: str) -> bool:
        """Import memory dump from backup"""
        try:
            with open(dump_file, "r") as f:
                dump = json.load(f)

            # Load graph
            graph = get_memory_graph()
            graph.import_from_json(json.dumps(dump["graph"]))

            # Load conversations
            from src.memory.conversation_tracker import ConversationSession, ConversationTurn

            tracker = get_conversation_tracker()
            for session_id, session_data in dump["conversations"].items():
                session = ConversationSession(session_id, session_data["topic"])
                session.started_at = datetime.fromisoformat(session_data["started_at"])
                if session_data["ended_at"]:
                    session.ended_at = datetime.fromisoformat(session_data["ended_at"])
                session.summary = session_data.get("summary")
                session.key_facts = session_data.get("key_facts", [])

                for turn_data in session_data["turns"]:
                    turn = ConversationTurn(
                        turn_id=turn_data["turn_id"],
                        speaker=turn_data["speaker"],
                        content=turn_data["content"],
                        timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                        metadata=turn_data.get("metadata", {}),
                    )
                    session.add_turn(turn)

                tracker.sessions[session_id] = session

            # Load entities
            from src.memory.entity_mapper import Entity, EntityType

            mapper = get_entity_mapper()
            for entity_id, entity_data in dump["entities"].items():
                entity = Entity(
                    entity_id=entity_id,
                    name=entity_data["name"],
                    entity_type=EntityType(entity_data["type"]),
                    attributes=entity_data.get("attributes", {}),
                )
                entity.first_seen = datetime.fromisoformat(entity_data["first_seen"])
                entity.last_seen = datetime.fromisoformat(entity_data["last_seen"])
                entity.mention_count = entity_data.get("mention_count", 1)
                mapper.entities[entity_id] = entity

            # Load vector store
            manager = get_memory_manager()
            vector_data = dump.get("vector_store", {})
            manager.vector_store.documents = vector_data.get("documents", {})
            manager.vector_store.metadata = vector_data.get("metadata", {})
            manager.vector_store.collections = vector_data.get("collections", {})

            self.logger.info(f"Imported memory dump from {dump_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error importing memory dump: {e}")
            return False

    def get_memory_size(self) -> Dict[str, int]:
        """Get size of memory components in bytes"""
        sizes = {}

        for file_name, file_path in [
            ("graph", self.graph_file),
            ("conversations", self.conversations_file),
            ("entities", self.entities_file),
            ("metadata", self.metadata_file),
        ]:
            if file_path.exists():
                sizes[file_name] = file_path.stat().st_size
            else:
                sizes[file_name] = 0

        sizes["total"] = sum(sizes.values())
        return sizes


# Global instance
_memory_persistence: Optional[MemoryPersistence] = None


def get_memory_persistence() -> MemoryPersistence:
    """Get global memory persistence manager"""
    global _memory_persistence
    if _memory_persistence is None:
        _memory_persistence = MemoryPersistence()
    return _memory_persistence
