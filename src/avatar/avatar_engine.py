"""
3D Avatar Engine
Renders and animates 3D avatar with AI-driven emotions
"""

import json
import math
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import setup_logger


class EmotionState(Enum):
    """Avatar emotion states"""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    THINKING = "thinking"
    CONFUSED = "confused"
    FOCUSED = "focused"
    TIRED = "tired"
    SURPRISED = "surprised"
    CALM = "calm"
    ENERGETIC = "energetic"


class AvatarPose(Enum):
    """Avatar body poses"""

    IDLE = "idle"
    SPEAKING = "speaking"
    LISTENING = "listening"
    TYPING = "typing"
    POINTING = "pointing"
    CELEBRATING = "celebrating"
    THINKING_POSE = "thinking_pose"
    WAVING = "waving"


class Avatar3DModel:
    """3D avatar model with skeletal animation"""

    def __init__(self, model_id: str = "xeno_default"):
        self.logger = setup_logger("avatar.model")
        self.model_id = model_id

        # Model properties
        self.position = [0.0, 0.0, 0.0]  # x, y, z
        self.rotation = [0.0, 0.0, 0.0]  # pitch, yaw, roll
        self.scale = 1.0

        # Animation state
        self.current_emotion = EmotionState.NEUTRAL
        self.current_pose = AvatarPose.IDLE
        self.is_speaking = False
        self.animation_time = 0.0

        # Skeletal bones (simplified)
        self.bones = {
            "head": {"position": [0, 1.7, 0], "rotation": [0, 0, 0]},
            "neck": {"position": [0, 1.5, 0], "rotation": [0, 0, 0]},
            "torso": {"position": [0, 1.0, 0], "rotation": [0, 0, 0]},
            "left_shoulder": {"position": [-0.3, 1.4, 0], "rotation": [0, 0, 0]},
            "right_shoulder": {"position": [0.3, 1.4, 0], "rotation": [0, 0, 0]},
            "left_arm": {"position": [-0.3, 1.1, 0], "rotation": [0, 0, 0]},
            "right_arm": {"position": [0.3, 1.1, 0], "rotation": [0, 0, 0]},
            "left_hand": {"position": [-0.3, 0.8, 0], "rotation": [0, 0, 0]},
            "right_hand": {"position": [0.3, 0.8, 0], "rotation": [0, 0, 0]},
        }

        # Facial expressions (blend shapes)
        self.expressions = {
            "smile": 0.0,
            "frown": 0.0,
            "eyebrows_raised": 0.0,
            "eyebrows_furrowed": 0.0,
            "eyes_closed": 0.0,
            "mouth_open": 0.0,
            "jaw_drop": 0.0,
            "cheek_raise": 0.0,
        }

        # Particle effects
        self.particles: List[Dict[str, Any]] = []

        self.logger.info(f"Initialized 3D avatar model: {model_id}")

    def set_emotion(self, emotion: EmotionState, transition_time: float = 0.5):
        """Set avatar emotion with smooth transition"""
        self.current_emotion = emotion

        # Apply emotion-specific expressions
        target_expressions = self._get_emotion_expressions(emotion)

        # Smooth blend to target (simplified - would use proper interpolation)
        for expr, value in target_expressions.items():
            self.expressions[expr] = value

        self.logger.debug(f"Avatar emotion set to: {emotion.value}")

    def set_pose(self, pose: AvatarPose):
        """Set avatar body pose"""
        self.current_pose = pose

        # Apply pose-specific bone rotations
        bone_rotations = self._get_pose_rotations(pose)

        for bone, rotation in bone_rotations.items():
            if bone in self.bones:
                self.bones[bone]["rotation"] = rotation

        self.logger.debug(f"Avatar pose set to: {pose.value}")

    def speak(self, text: str, audio_amplitude: float = 0.5):
        """Trigger speaking animation"""
        self.is_speaking = True

        # Animate mouth based on audio amplitude
        self.expressions["mouth_open"] = audio_amplitude
        self.expressions["jaw_drop"] = audio_amplitude * 0.5

        # Subtle head nod
        head_nod = math.sin(self.animation_time * 3.0) * 0.05
        self.bones["head"]["rotation"][0] = head_nod  # Pitch

    def stop_speaking(self):
        """Stop speaking animation"""
        self.is_speaking = False
        self.expressions["mouth_open"] = 0.0
        self.expressions["jaw_drop"] = 0.0

    def update(self, delta_time: float):
        """Update animation (called every frame)"""
        self.animation_time += delta_time

        # Idle breathing animation
        if self.current_pose == AvatarPose.IDLE:
            breath = math.sin(self.animation_time * 1.5) * 0.02
            self.bones["torso"]["position"][1] = 1.0 + breath

        # Blinking
        if int(self.animation_time * 4) % 20 == 0:  # Blink every 5 seconds
            self.expressions["eyes_closed"] = 1.0
        else:
            self.expressions["eyes_closed"] = 0.0

        # Update particles
        self._update_particles(delta_time)

    def add_particle_effect(self, effect_type: str, position: List[float]):
        """Add particle effect (sparkles, glow, etc.)"""
        particle = {
            "type": effect_type,
            "position": position.copy(),
            "velocity": [0.0, 0.1, 0.0],
            "lifetime": 2.0,
            "age": 0.0,
            "color": [1.0, 1.0, 1.0, 1.0],  # RGBA
        }
        self.particles.append(particle)

    def _get_emotion_expressions(self, emotion: EmotionState) -> Dict[str, float]:
        """Get blend shape values for emotion"""
        expressions = {
            EmotionState.NEUTRAL: {"smile": 0.0, "frown": 0.0},
            EmotionState.HAPPY: {"smile": 0.8, "cheek_raise": 0.6},
            EmotionState.EXCITED: {"smile": 1.0, "eyebrows_raised": 0.7, "mouth_open": 0.3},
            EmotionState.THINKING: {"eyebrows_furrowed": 0.5, "mouth_open": 0.1},
            EmotionState.CONFUSED: {"eyebrows_raised": 0.8, "frown": 0.3},
            EmotionState.FOCUSED: {"eyebrows_furrowed": 0.4},
            EmotionState.TIRED: {"eyes_closed": 0.5, "frown": 0.2},
            EmotionState.SURPRISED: {"eyebrows_raised": 1.0, "jaw_drop": 0.8},
            EmotionState.CALM: {"smile": 0.3},
            EmotionState.ENERGETIC: {"smile": 0.7, "eyebrows_raised": 0.4},
        }

        return expressions.get(emotion, {})

    def _get_pose_rotations(self, pose: AvatarPose) -> Dict[str, List[float]]:
        """Get bone rotations for pose"""
        rotations = {
            AvatarPose.IDLE: {},
            AvatarPose.SPEAKING: {
                "head": [0.1, 0.0, 0.0],  # Slight head tilt
            },
            AvatarPose.LISTENING: {
                "head": [0.2, 0.0, 0.0],  # Head tilted forward
            },
            AvatarPose.TYPING: {
                "head": [0.3, 0.0, 0.0],
                "left_arm": [0.5, 0.0, 0.2],
                "right_arm": [0.5, 0.0, -0.2],
            },
            AvatarPose.POINTING: {
                "right_arm": [0.0, 0.5, 0.0],
                "right_hand": [0.0, 0.0, 0.3],
            },
            AvatarPose.CELEBRATING: {
                "left_arm": [-0.8, 0.5, 0.0],
                "right_arm": [-0.8, -0.5, 0.0],
            },
            AvatarPose.THINKING_POSE: {
                "head": [0.2, 0.3, 0.0],
                "right_hand": [0.0, 0.5, 0.0],
            },
            AvatarPose.WAVING: {
                "right_arm": [-0.5, 0.5, 0.0],
            },
        }

        return rotations.get(pose, {})

    def _update_particles(self, delta_time: float):
        """Update particle effects"""
        # Update existing particles
        particles_to_remove = []

        for i, particle in enumerate(self.particles):
            particle["age"] += delta_time

            # Move particle
            for j in range(3):
                particle["position"][j] += particle["velocity"][j] * delta_time

            # Fade out
            alpha = 1.0 - (particle["age"] / particle["lifetime"])
            particle["color"][3] = max(0.0, alpha)

            # Mark for removal if dead
            if particle["age"] >= particle["lifetime"]:
                particles_to_remove.append(i)

        # Remove dead particles
        for i in reversed(particles_to_remove):
            self.particles.pop(i)

    def get_render_data(self) -> Dict[str, Any]:
        """Get data for rendering"""
        return {
            "model_id": self.model_id,
            "position": self.position,
            "rotation": self.rotation,
            "scale": self.scale,
            "bones": self.bones,
            "expressions": self.expressions,
            "particles": self.particles,
            "emotion": self.current_emotion.value,
            "pose": self.current_pose.value,
            "is_speaking": self.is_speaking,
        }


class AvatarEngine:
    """Main avatar engine coordinating 3D avatar"""

    def __init__(self):
        self.logger = setup_logger("avatar.engine")

        # Avatar model
        self.avatar = Avatar3DModel()

        # Animation state
        self.is_active = False
        self.last_update_time = time.time()

        # Emotion detection
        self.emotion_history: List[Tuple[datetime, EmotionState]] = []

        # Voice sync
        self.audio_amplitude = 0.0
        self.is_voice_active = False

        self.logger.info("Avatar engine initialized")

    def start(self):
        """Start avatar engine"""
        self.is_active = True
        self.avatar.set_emotion(EmotionState.HAPPY)
        self.avatar.set_pose(AvatarPose.WAVING)

        # Welcome particle effect
        self.avatar.add_particle_effect("sparkle", [0.0, 2.0, 0.0])

        self.logger.info("Avatar engine started")

    def stop(self):
        """Stop avatar engine"""
        self.is_active = False
        self.avatar.set_emotion(EmotionState.CALM)
        self.avatar.set_pose(AvatarPose.IDLE)

        self.logger.info("Avatar engine stopped")

    def update(self):
        """Update avatar (call every frame)"""
        if not self.is_active:
            return

        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time

        # Update avatar animation
        self.avatar.update(delta_time)

        # Sync with voice
        if self.is_voice_active:
            self.avatar.speak("", self.audio_amplitude)
        else:
            if self.avatar.is_speaking:
                self.avatar.stop_speaking()

    def set_emotion_from_context(self, context: str):
        """Set emotion based on context/sentiment"""
        # Simple keyword-based emotion detection
        context_lower = context.lower()

        if any(word in context_lower for word in ["error", "failed", "problem"]):
            emotion = EmotionState.CONFUSED
        elif any(word in context_lower for word in ["success", "done", "complete"]):
            emotion = EmotionState.HAPPY
        elif any(word in context_lower for word in ["thinking", "analyzing", "processing"]):
            emotion = EmotionState.THINKING
        elif any(word in context_lower for word in ["urgent", "alert", "critical"]):
            emotion = EmotionState.SURPRISED
        elif any(word in context_lower for word in ["focus", "work", "task"]):
            emotion = EmotionState.FOCUSED
        else:
            emotion = EmotionState.NEUTRAL

        self.avatar.set_emotion(emotion)
        self.emotion_history.append((datetime.now(), emotion))

    def set_voice_activity(self, is_active: bool, amplitude: float = 0.5):
        """Update voice activity for lip sync"""
        self.is_voice_active = is_active
        self.audio_amplitude = amplitude

    def trigger_action(self, action: str):
        """Trigger avatar action"""
        actions = {
            "wave": (AvatarPose.WAVING, EmotionState.HAPPY),
            "celebrate": (AvatarPose.CELEBRATING, EmotionState.EXCITED),
            "think": (AvatarPose.THINKING_POSE, EmotionState.THINKING),
            "point": (AvatarPose.POINTING, EmotionState.NEUTRAL),
            "type": (AvatarPose.TYPING, EmotionState.FOCUSED),
            "listen": (AvatarPose.LISTENING, EmotionState.CALM),
        }

        if action in actions:
            pose, emotion = actions[action]
            self.avatar.set_pose(pose)
            self.avatar.set_emotion(emotion)

            # Add particle effect
            self.avatar.add_particle_effect("glow", [0.0, 1.7, 0.0])

            self.logger.info(f"Triggered action: {action}")

    def get_render_data(self) -> Dict[str, Any]:
        """Get current avatar state for rendering"""
        return self.avatar.get_render_data()

    def get_emotion_stats(self) -> Dict[str, Any]:
        """Get emotion statistics"""
        if not self.emotion_history:
            return {"dominant_emotion": "neutral", "emotion_changes": 0}

        # Count emotions
        emotion_counts = {}
        for _, emotion in self.emotion_history[-100:]:  # Last 100 emotions
            emotion_value = emotion.value
            emotion_counts[emotion_value] = emotion_counts.get(emotion_value, 0) + 1

        # Find dominant emotion
        dominant = max(emotion_counts.items(), key=lambda x: x[1])[0]

        return {
            "dominant_emotion": dominant,
            "emotion_changes": len(self.emotion_history),
            "emotion_distribution": emotion_counts,
            "current_emotion": self.avatar.current_emotion.value,
        }


# Global instance
_avatar_engine: Optional[AvatarEngine] = None


def get_avatar_engine() -> AvatarEngine:
    """Get global avatar engine"""
    global _avatar_engine
    if _avatar_engine is None:
        _avatar_engine = AvatarEngine()
    return _avatar_engine
