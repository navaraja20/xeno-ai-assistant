"""
Conversation Context Tracker
Maintains conversational memory and context awareness
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger
from src.memory.memory_graph import MemoryNode, MemoryRelationship, get_memory_graph
from src.memory.vector_store import get_memory_manager


class ConversationTurn:
    """Single turn in a conversation"""

    def __init__(
        self,
        turn_id: str,
        speaker: str,
        content: str,
        timestamp: datetime = None,
        metadata: Dict[str, Any] = None,
    ):
        self.turn_id = turn_id
        self.speaker = speaker  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "turn_id": self.turn_id,
            "speaker": self.speaker,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ConversationSession:
    """A conversation session with multiple turns"""

    def __init__(self, session_id: str, topic: str = None):
        self.session_id = session_id
        self.topic = topic or "General"
        self.turns: List[ConversationTurn] = []
        self.started_at = datetime.now()
        self.ended_at: Optional[datetime] = None
        self.summary: Optional[str] = None
        self.key_facts: List[str] = []

    def add_turn(self, turn: ConversationTurn):
        """Add conversation turn"""
        self.turns.append(turn)

    def end_session(self, summary: str = None):
        """End conversation session"""
        self.ended_at = datetime.now()
        self.summary = summary

    def get_duration(self) -> timedelta:
        """Get session duration"""
        end = self.ended_at or datetime.now()
        return end - self.started_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "turns": [turn.to_dict() for turn in self.turns],
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.get_duration().total_seconds(),
            "summary": self.summary,
            "key_facts": self.key_facts,
        }


class ConversationContextTracker:
    """Tracks conversation context and manages conversational memory"""

    def __init__(self):
        self.logger = setup_logger("memory.conversation")
        self.memory_manager = get_memory_manager()
        self.graph = get_memory_graph()

        # Current session
        self.current_session: Optional[ConversationSession] = None

        # Session history
        self.sessions: Dict[str, ConversationSession] = {}

        # Context window (recent turns for quick access)
        self.context_window: List[ConversationTurn] = []
        self.context_window_size = 10

    def start_session(self, session_id: str = None, topic: str = None) -> str:
        """Start new conversation session"""
        if session_id is None:
            session_id = f"session_{datetime.now().timestamp()}"

        self.current_session = ConversationSession(session_id, topic)
        self.sessions[session_id] = self.current_session

        self.logger.info(f"Started conversation session: {session_id}")
        return session_id

    def add_turn(
        self,
        speaker: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Add turn to current session"""

        # Auto-start session if needed
        if self.current_session is None:
            self.start_session()

        turn_id = f"turn_{datetime.now().timestamp()}"
        turn = ConversationTurn(turn_id, speaker, content, metadata=metadata)

        self.current_session.add_turn(turn)
        self.context_window.append(turn)

        # Maintain window size
        if len(self.context_window) > self.context_window_size:
            self.context_window.pop(0)

        # Store in memory graph
        self._store_turn_in_memory(turn)

        self.logger.debug(f"Added turn: {speaker} - {content[:50]}...")
        return turn_id

    def _store_turn_in_memory(self, turn: ConversationTurn):
        """Store conversation turn in memory graph"""

        # Create node
        node = MemoryNode(
            node_id=turn.turn_id,
            node_type="conversation",
            content=f"{turn.speaker}: {turn.content}",
            metadata={
                "speaker": turn.speaker,
                "session_id": self.current_session.session_id,
                "topic": self.current_session.topic,
                **turn.metadata,
            },
        )
        self.graph.add_node(node)

        # Link to previous turn
        if len(self.current_session.turns) > 1:
            prev_turn = self.current_session.turns[-2]
            rel = MemoryRelationship(
                from_node=prev_turn.turn_id,
                to_node=turn.turn_id,
                rel_type="precedes",
                strength=1.0,
            )
            self.graph.add_relationship(rel)

        # Store in vector database for semantic search
        embedding = self.memory_manager.vector_store.create_embedding(turn.content)
        self.memory_manager.vector_store.add_document(
            doc_id=turn.turn_id,
            content=turn.content,
            embedding=embedding,
            metadata=node.metadata,
            collection="conversations",
        )

    def extract_facts(self, content: str) -> List[str]:
        """Extract key facts from conversation content"""

        # Simple fact extraction (can be enhanced with NLP)
        facts = []

        # Look for definitive statements
        sentences = content.split(".")
        for sentence in sentences:
            sentence = sentence.strip()

            # Heuristics for facts
            if any(
                keyword in sentence.lower()
                for keyword in [
                    "is",
                    "are",
                    "was",
                    "were",
                    "has",
                    "have",
                    "will",
                    "my name is",
                    "i am",
                    "i work",
                    "i live",
                ]
            ):
                if len(sentence) > 10 and len(sentence) < 200:
                    facts.append(sentence)

        return facts

    def remember_fact(self, fact: str, related_to_turn: str = None):
        """Remember a fact from conversation"""

        # Store fact in memory
        fact_id = self.memory_manager.remember(
            content=fact,
            memory_type="fact",
            metadata={
                "source": "conversation",
                "session_id": self.current_session.session_id if self.current_session else None,
            },
        )

        # Link to conversation turn
        if related_to_turn:
            rel = MemoryRelationship(
                from_node=related_to_turn,
                to_node=fact_id,
                rel_type="mentioned_in",
                strength=1.0,
            )
            self.graph.add_relationship(rel)

        # Add to session facts
        if self.current_session:
            self.current_session.key_facts.append(fact)

        self.logger.info(f"Remembered fact: {fact[:50]}...")

    def get_context(self, max_turns: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        recent_turns = self.context_window[-max_turns:]
        return [turn.to_dict() for turn in recent_turns]

    def search_conversation_history(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search past conversations"""
        return self.memory_manager.recall(
            query=query,
            memory_type="conversation",
            limit=limit,
        )

    def get_session_summary(self, session_id: str = None) -> Optional[Dict[str, Any]]:
        """Get summary of a conversation session"""

        session = None
        if session_id:
            session = self.sessions.get(session_id)
        else:
            session = self.current_session

        if not session:
            return None

        # Generate summary if not exists
        if not session.summary and len(session.turns) > 0:
            # Simple summary generation
            turn_count = len(session.turns)
            user_turns = [t for t in session.turns if t.speaker == "user"]
            assistant_turns = [t for t in session.turns if t.speaker == "assistant"]

            session.summary = (
                f"Conversation about {session.topic} with {turn_count} turns "
                f"({len(user_turns)} user, {len(assistant_turns)} assistant)"
            )

        return session.to_dict()

    def end_current_session(self):
        """End current conversation session"""
        if self.current_session:
            # Extract facts from conversation
            for turn in self.current_session.turns:
                facts = self.extract_facts(turn.content)
                for fact in facts:
                    self.remember_fact(fact, turn.turn_id)

            # Generate summary
            summary = self.get_session_summary()
            self.current_session.end_session(summary=summary.get("summary") if summary else None)

            self.logger.info(
                f"Ended session: {self.current_session.session_id} "
                f"with {len(self.current_session.turns)} turns"
            )

            self.current_session = None

    def get_related_memories(
        self, query: str, include_facts: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get related memories for a query"""

        result = {
            "conversations": self.search_conversation_history(query, limit=3),
            "facts": [],
        }

        if include_facts:
            result["facts"] = self.memory_manager.recall(
                query=query,
                memory_type="fact",
                limit=5,
            )

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        total_turns = sum(len(session.turns) for session in self.sessions.values())
        total_sessions = len(self.sessions)

        return {
            "total_sessions": total_sessions,
            "total_turns": total_turns,
            "avg_turns_per_session": total_turns / total_sessions if total_sessions > 0 else 0,
            "current_session": (
                self.current_session.session_id if self.current_session else None
            ),
            "context_window_size": len(self.context_window),
        }


# Global instance
_conversation_tracker: Optional[ConversationContextTracker] = None


def get_conversation_tracker() -> ConversationContextTracker:
    """Get global conversation tracker"""
    global _conversation_tracker
    if _conversation_tracker is None:
        _conversation_tracker = ConversationContextTracker()
    return _conversation_tracker
