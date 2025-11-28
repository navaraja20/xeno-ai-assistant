"""
AI Module
Local LLM integration with Ollama + Gemini fallback
"""

from src.ai.ai_agent import (
    AIAgent,
    ModelProvider,
    Message,
    Tool,
    get_ai_agent,
)

from src.ai.ai_chat_ui import AIChatWidget


__all__ = [
    # Core
    "AIAgent",
    "ModelProvider",
    "Message",
    "Tool",
    "get_ai_agent",
    
    # UI
    "AIChatWidget",
]
