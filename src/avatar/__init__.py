"""
Avatar Module
3D Avatar and Holographic UI system
"""

from src.avatar.avatar_engine import (
    Avatar3DModel,
    AvatarEngine,
    AvatarPose,
    EmotionState,
    get_avatar_engine,
)
from src.avatar.avatar_widget import AvatarWidget, create_avatar_widget
from src.avatar.holographic_effects import (
    HologramEffect,
    HolographicGlow,
    HolographicRenderer,
    get_holographic_renderer,
)

__all__ = [
    # Engine
    "AvatarEngine",
    "Avatar3DModel",
    "get_avatar_engine",
    # Enums
    "EmotionState",
    "AvatarPose",
    "HologramEffect",
    # Effects
    "HolographicRenderer",
    "HolographicGlow",
    "get_holographic_renderer",
    # Widget
    "AvatarWidget",
    "create_avatar_widget",
]
