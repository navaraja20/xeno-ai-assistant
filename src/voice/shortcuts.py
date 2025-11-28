"""
Voice Command Shortcuts System
Custom voice shortcuts for quick actions
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class VoiceShortcut:
    """Individual voice shortcut definition"""

    def __init__(
        self,
        name: str,
        triggers: List[str],
        action: Callable,
        description: str = "",
        category: str = "general",
        enabled: bool = True,
        requires_confirmation: bool = False,
    ):
        self.name = name
        self.triggers = [t.lower() for t in triggers]  # Case-insensitive
        self.action = action
        self.description = description
        self.category = category
        self.enabled = enabled
        self.requires_confirmation = requires_confirmation
        self.usage_count = 0
        self.last_used = None

    def matches(self, text: str) -> bool:
        """Check if text matches any trigger"""
        text_lower = text.lower().strip()

        for trigger in self.triggers:
            # Exact match
            if text_lower == trigger:
                return True

            # Pattern match (for wildcards)
            if "*" in trigger:
                pattern = trigger.replace("*", ".*")
                if re.match(f"^{pattern}$", text_lower):
                    return True

        return False

    def execute(self, context: Dict[str, Any] = None) -> Any:
        """Execute shortcut action"""
        if not self.enabled:
            return {"success": False, "error": "Shortcut is disabled"}

        try:
            self.usage_count += 1
            self.last_used = datetime.now()

            result = self.action(context or {})
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "triggers": self.triggers,
            "description": self.description,
            "category": self.category,
            "enabled": self.enabled,
            "requires_confirmation": self.requires_confirmation,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class ShortcutManager:
    """Manages voice shortcuts"""

    def __init__(self, shortcuts_file: str = "data/voice_shortcuts.json"):
        self.logger = setup_logger("voice.shortcuts")
        self.shortcuts_file = Path(shortcuts_file)
        self.shortcuts: Dict[str, VoiceShortcut] = {}

        # Ensure data directory exists
        self.shortcuts_file.parent.mkdir(parents=True, exist_ok=True)

        # Load shortcuts
        self._load_shortcuts()
        self._register_default_shortcuts()

    def add_shortcut(self, shortcut: VoiceShortcut) -> bool:
        """Add or update a shortcut"""
        try:
            self.shortcuts[shortcut.name] = shortcut
            self._save_shortcuts()
            self.logger.info(f"Added shortcut: {shortcut.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding shortcut: {e}")
            return False

    def remove_shortcut(self, name: str) -> bool:
        """Remove a shortcut"""
        if name in self.shortcuts:
            del self.shortcuts[name]
            self._save_shortcuts()
            self.logger.info(f"Removed shortcut: {name}")
            return True
        return False

    def get_shortcut(self, name: str) -> Optional[VoiceShortcut]:
        """Get shortcut by name"""
        return self.shortcuts.get(name)

    def find_matching_shortcut(self, text: str) -> Optional[VoiceShortcut]:
        """Find shortcut that matches the text"""
        for shortcut in self.shortcuts.values():
            if shortcut.enabled and shortcut.matches(text):
                return shortcut
        return None

    def execute_shortcut(
        self, text: str, context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Find and execute matching shortcut"""
        shortcut = self.find_matching_shortcut(text)

        if shortcut:
            self.logger.info(f"Executing shortcut: {shortcut.name}")
            return shortcut.execute(context)

        return None

    def list_shortcuts(
        self, category: Optional[str] = None, enabled_only: bool = False
    ) -> List[VoiceShortcut]:
        """List shortcuts with optional filtering"""
        shortcuts = list(self.shortcuts.values())

        if category:
            shortcuts = [s for s in shortcuts if s.category == category]

        if enabled_only:
            shortcuts = [s for s in shortcuts if s.enabled]

        # Sort by usage count
        shortcuts.sort(key=lambda s: s.usage_count, reverse=True)

        return shortcuts

    def get_categories(self) -> List[str]:
        """Get all shortcut categories"""
        categories = set(s.category for s in self.shortcuts.values())
        return sorted(categories)

    def enable_shortcut(self, name: str):
        """Enable a shortcut"""
        if name in self.shortcuts:
            self.shortcuts[name].enabled = True
            self._save_shortcuts()

    def disable_shortcut(self, name: str):
        """Disable a shortcut"""
        if name in self.shortcuts:
            self.shortcuts[name].enabled = False
            self._save_shortcuts()

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total = len(self.shortcuts)
        enabled = sum(1 for s in self.shortcuts.values() if s.enabled)
        total_usage = sum(s.usage_count for s in self.shortcuts.values())

        # Most used
        most_used = sorted(
            self.shortcuts.values(), key=lambda s: s.usage_count, reverse=True
        )[:5]

        return {
            "total_shortcuts": total,
            "enabled_shortcuts": enabled,
            "total_usage": total_usage,
            "most_used": [
                {"name": s.name, "usage": s.usage_count} for s in most_used
            ],
            "categories": len(self.get_categories()),
        }

    def _save_shortcuts(self):
        """Save shortcuts to file"""
        try:
            data = {
                name: {
                    "triggers": shortcut.triggers,
                    "description": shortcut.description,
                    "category": shortcut.category,
                    "enabled": shortcut.enabled,
                    "requires_confirmation": shortcut.requires_confirmation,
                    "usage_count": shortcut.usage_count,
                    "last_used": (
                        shortcut.last_used.isoformat() if shortcut.last_used else None
                    ),
                }
                for name, shortcut in self.shortcuts.items()
            }

            with open(self.shortcuts_file, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.debug(f"Saved {len(self.shortcuts)} shortcuts")
        except Exception as e:
            self.logger.error(f"Error saving shortcuts: {e}")

    def _load_shortcuts(self):
        """Load shortcuts from file"""
        if not self.shortcuts_file.exists():
            return

        try:
            with open(self.shortcuts_file, "r") as f:
                data = json.load(f)

            # Note: Actions cannot be serialized, so loaded shortcuts
            # need actions re-registered via _register_default_shortcuts()
            self.logger.info(f"Loaded {len(data)} shortcuts from file")

        except Exception as e:
            self.logger.error(f"Error loading shortcuts: {e}")

    def _register_default_shortcuts(self):
        """Register default built-in shortcuts"""

        # Email shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="check_email",
                triggers=["check my email", "check email", "any new emails"],
                action=lambda ctx: self._check_email_action(),
                description="Check for new emails",
                category="email",
            )
        )

        self.add_shortcut(
            VoiceShortcut(
                name="send_quick_email",
                triggers=["send quick email", "quick email"],
                action=lambda ctx: self._send_quick_email_action(ctx),
                description="Send a quick email",
                category="email",
            )
        )

        # Calendar shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="today_schedule",
                triggers=[
                    "what's my schedule",
                    "what's on my calendar",
                    "today's schedule",
                ],
                action=lambda ctx: self._today_schedule_action(),
                description="Show today's schedule",
                category="calendar",
            )
        )

        self.add_shortcut(
            VoiceShortcut(
                name="next_meeting",
                triggers=["next meeting", "when is my next meeting"],
                action=lambda ctx: self._next_meeting_action(),
                description="Show next meeting",
                category="calendar",
            )
        )

        # Task shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="my_tasks",
                triggers=["my tasks", "what are my tasks", "show tasks"],
                action=lambda ctx: self._my_tasks_action(),
                description="Show pending tasks",
                category="tasks",
            )
        )

        # GitHub shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="github_notifications",
                triggers=["github notifications", "check github"],
                action=lambda ctx: self._github_notifications_action(),
                description="Check GitHub notifications",
                category="github",
            )
        )

        # LinkedIn shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="job_updates",
                triggers=["job updates", "check jobs", "new jobs"],
                action=lambda ctx: self._job_updates_action(),
                description="Check for new job postings",
                category="linkedin",
            )
        )

        # System shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="focus_mode",
                triggers=["enter focus mode", "focus mode", "start focusing"],
                action=lambda ctx: self._focus_mode_action(True),
                description="Enable focus mode (DND + minimal UI)",
                category="system",
            )
        )

        self.add_shortcut(
            VoiceShortcut(
                name="exit_focus_mode",
                triggers=["exit focus mode", "stop focusing", "end focus"],
                action=lambda ctx: self._focus_mode_action(False),
                description="Disable focus mode",
                category="system",
            )
        )

        # AI shortcuts
        self.add_shortcut(
            VoiceShortcut(
                name="summarize_day",
                triggers=["summarize my day", "daily summary", "what did I do today"],
                action=lambda ctx: self._summarize_day_action(),
                description="AI summary of your day",
                category="ai",
            )
        )

        # Quick actions
        self.add_shortcut(
            VoiceShortcut(
                name="good_morning",
                triggers=["good morning", "start my day"],
                action=lambda ctx: self._good_morning_routine(),
                description="Morning routine (emails, calendar, tasks, news)",
                category="routines",
            )
        )

        self.add_shortcut(
            VoiceShortcut(
                name="good_night",
                triggers=["good night", "end my day", "wrap up"],
                action=lambda ctx: self._good_night_routine(),
                description="Evening routine (summary, tomorrow prep, cleanup)",
                category="routines",
            )
        )

    # Action implementations (placeholders - will be connected to actual modules)
    def _check_email_action(self):
        """Check email action"""
        # TODO: Connect to email_handler
        return "Checking emails..."

    def _send_quick_email_action(self, context):
        """Send quick email action"""
        # TODO: Connect to email_handler
        return "Quick email feature"

    def _today_schedule_action(self):
        """Today's schedule action"""
        # TODO: Connect to calendar_manager
        return "Fetching today's schedule..."

    def _next_meeting_action(self):
        """Next meeting action"""
        # TODO: Connect to calendar_manager
        return "Checking next meeting..."

    def _my_tasks_action(self):
        """My tasks action"""
        # TODO: Connect to task manager
        return "Loading tasks..."

    def _github_notifications_action(self):
        """GitHub notifications action"""
        # TODO: Connect to github_manager
        return "Checking GitHub..."

    def _job_updates_action(self):
        """Job updates action"""
        # TODO: Connect to linkedin_automation
        return "Checking job postings..."

    def _focus_mode_action(self, enable: bool):
        """Focus mode action"""
        # TODO: Connect to notification system + UI
        if enable:
            return "Focus mode activated. Notifications paused."
        else:
            return "Focus mode deactivated."

    def _summarize_day_action(self):
        """Summarize day action"""
        # TODO: Connect to AI + analytics
        return "Generating daily summary..."

    def _good_morning_routine(self):
        """Morning routine"""
        # TODO: Multi-step routine
        return "Good morning! Running morning routine..."

    def _good_night_routine(self):
        """Evening routine"""
        # TODO: Multi-step routine
        return "Good night! Running evening routine..."


# Global instance
_shortcut_manager: Optional[ShortcutManager] = None


def get_shortcut_manager() -> ShortcutManager:
    """Get global shortcut manager"""
    global _shortcut_manager
    if _shortcut_manager is None:
        _shortcut_manager = ShortcutManager()
    return _shortcut_manager


# Convenience function
def execute_voice_shortcut(text: str, context: Dict[str, Any] = None):
    """Quick function to execute voice shortcut"""
    return get_shortcut_manager().execute_shortcut(text, context)
