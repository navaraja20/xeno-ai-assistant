"""
Voice Macros - Multi-Step Automation
Record and execute complex multi-step voice workflows
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class MacroStep:
    """Individual step in a macro"""

    def __init__(
        self,
        action: str,
        parameters: Dict[str, Any] = None,
        delay: float = 0,
        wait_for_completion: bool = True,
        description: str = "",
    ):
        self.action = action
        self.parameters = parameters or {}
        self.delay = delay  # Delay before executing (seconds)
        self.wait_for_completion = wait_for_completion
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action,
            "parameters": self.parameters,
            "delay": self.delay,
            "wait_for_completion": self.wait_for_completion,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "MacroStep":
        """Create from dictionary"""
        return MacroStep(
            action=data["action"],
            parameters=data.get("parameters", {}),
            delay=data.get("delay", 0),
            wait_for_completion=data.get("wait_for_completion", True),
            description=data.get("description", ""),
        )


class VoiceMacro:
    """Multi-step voice macro"""

    def __init__(
        self,
        name: str,
        steps: List[MacroStep] = None,
        triggers: List[str] = None,
        description: str = "",
        category: str = "custom",
        enabled: bool = True,
    ):
        self.name = name
        self.steps = steps or []
        self.triggers = [t.lower() for t in (triggers or [])]
        self.description = description
        self.category = category
        self.enabled = enabled
        self.created_at = datetime.now()
        self.usage_count = 0
        self.last_used = None

    def add_step(
        self,
        action: str,
        parameters: Dict[str, Any] = None,
        delay: float = 0,
        description: str = "",
    ):
        """Add a step to the macro"""
        step = MacroStep(action, parameters, delay, description=description)
        self.steps.append(step)

    def execute(
        self, context: Dict[str, Any] = None, action_executor: Callable = None
    ) -> Dict[str, Any]:
        """Execute macro steps"""
        if not self.enabled:
            return {"success": False, "error": "Macro is disabled"}

        if not action_executor:
            return {"success": False, "error": "No action executor provided"}

        results = []
        context = context or {}

        try:
            for i, step in enumerate(self.steps):
                # Apply delay
                if step.delay > 0:
                    time.sleep(step.delay)

                # Execute step
                result = action_executor(step.action, step.parameters, context)

                results.append(
                    {
                        "step": i + 1,
                        "action": step.action,
                        "result": result,
                        "success": result.get("success", False),
                    }
                )

                # Update context with step results
                context[f"step_{i+1}_result"] = result

                # Check if step failed and we should stop
                if not result.get("success", False) and step.wait_for_completion:
                    return {
                        "success": False,
                        "error": f"Step {i+1} failed: {result.get('error', 'Unknown error')}",
                        "completed_steps": i,
                        "results": results,
                    }

            self.usage_count += 1
            self.last_used = datetime.now()

            return {"success": True, "results": results, "completed_steps": len(self.steps)}

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "completed_steps": len(results),
                "results": results,
            }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
            "triggers": self.triggers,
            "description": self.description,
            "category": self.category,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "VoiceMacro":
        """Create from dictionary"""
        macro = VoiceMacro(
            name=data["name"],
            triggers=data.get("triggers", []),
            description=data.get("description", ""),
            category=data.get("category", "custom"),
            enabled=data.get("enabled", True),
        )

        # Load steps
        for step_data in data.get("steps", []):
            macro.steps.append(MacroStep.from_dict(step_data))

        # Load metadata
        if "created_at" in data:
            macro.created_at = datetime.fromisoformat(data["created_at"])
        if "usage_count" in data:
            macro.usage_count = data["usage_count"]
        if "last_used" in data and data["last_used"]:
            macro.last_used = datetime.fromisoformat(data["last_used"])

        return macro


class MacroManager:
    """Manages voice macros"""

    def __init__(self, macros_file: str = "data/voice_macros.json"):
        self.logger = setup_logger("voice.macros")
        self.macros_file = Path(macros_file)
        self.macros: Dict[str, VoiceMacro] = {}
        self.action_handlers: Dict[str, Callable] = {}

        # Recording state
        self.recording_macro: Optional[VoiceMacro] = None
        self.recording_start_time: Optional[float] = None

        # Ensure data directory exists
        self.macros_file.parent.mkdir(parents=True, exist_ok=True)

        # Load macros
        self._load_macros()
        self._register_default_actions()
        self._register_default_macros()

    def add_macro(self, macro: VoiceMacro) -> bool:
        """Add or update a macro"""
        try:
            self.macros[macro.name] = macro
            self._save_macros()
            self.logger.info(f"Added macro: {macro.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error adding macro: {e}")
            return False

    def remove_macro(self, name: str) -> bool:
        """Remove a macro"""
        if name in self.macros:
            del self.macros[name]
            self._save_macros()
            self.logger.info(f"Removed macro: {name}")
            return True
        return False

    def get_macro(self, name: str) -> Optional[VoiceMacro]:
        """Get macro by name"""
        return self.macros.get(name)

    def execute_macro(
        self, name: str, context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute a macro by name"""
        macro = self.get_macro(name)

        if macro:
            self.logger.info(f"Executing macro: {name}")
            return macro.execute(context, self._execute_action)

        return None

    def find_matching_macro(self, text: str) -> Optional[VoiceMacro]:
        """Find macro matching text"""
        text_lower = text.lower().strip()

        for macro in self.macros.values():
            if macro.enabled and text_lower in macro.triggers:
                return macro

        return None

    def register_action_handler(self, action: str, handler: Callable):
        """Register an action handler"""
        self.action_handlers[action] = handler
        self.logger.debug(f"Registered action handler: {action}")

    def start_recording(self, name: str, description: str = ""):
        """Start recording a new macro"""
        self.recording_macro = VoiceMacro(name=name, description=description)
        self.recording_start_time = time.time()
        self.logger.info(f"Started recording macro: {name}")

    def record_step(
        self, action: str, parameters: Dict[str, Any] = None, description: str = ""
    ):
        """Record a step in the current macro"""
        if not self.recording_macro:
            self.logger.error("No macro recording in progress")
            return False

        # Calculate delay from previous step
        delay = 0
        if self.recording_start_time and len(self.recording_macro.steps) > 0:
            delay = time.time() - self.recording_start_time

        self.recording_macro.add_step(action, parameters, delay, description)
        self.recording_start_time = time.time()

        self.logger.info(f"Recorded step: {action}")
        return True

    def stop_recording(self, triggers: List[str] = None) -> Optional[VoiceMacro]:
        """Stop recording and save macro"""
        if not self.recording_macro:
            return None

        if triggers:
            self.recording_macro.triggers = [t.lower() for t in triggers]

        # Save macro
        self.add_macro(self.recording_macro)

        macro = self.recording_macro
        self.recording_macro = None
        self.recording_start_time = None

        self.logger.info(f"Stopped recording macro: {macro.name}")
        return macro

    def cancel_recording(self):
        """Cancel current recording"""
        if self.recording_macro:
            self.logger.info(f"Cancelled recording macro: {self.recording_macro.name}")
            self.recording_macro = None
            self.recording_start_time = None

    def list_macros(
        self, category: Optional[str] = None, enabled_only: bool = False
    ) -> List[VoiceMacro]:
        """List macros with optional filtering"""
        macros = list(self.macros.values())

        if category:
            macros = [m for m in macros if m.category == category]

        if enabled_only:
            macros = [m for m in macros if m.enabled]

        # Sort by usage count
        macros.sort(key=lambda m: m.usage_count, reverse=True)

        return macros

    def _execute_action(
        self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single action"""
        handler = self.action_handlers.get(action)

        if not handler:
            return {"success": False, "error": f"No handler for action: {action}"}

        try:
            result = handler(parameters, context)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_macros(self):
        """Save macros to file"""
        try:
            data = {name: macro.to_dict() for name, macro in self.macros.items()}

            with open(self.macros_file, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.debug(f"Saved {len(self.macros)} macros")
        except Exception as e:
            self.logger.error(f"Error saving macros: {e}")

    def _load_macros(self):
        """Load macros from file"""
        if not self.macros_file.exists():
            return

        try:
            with open(self.macros_file, "r") as f:
                data = json.load(f)

            for name, macro_data in data.items():
                self.macros[name] = VoiceMacro.from_dict(macro_data)

            self.logger.info(f"Loaded {len(self.macros)} macros")
        except Exception as e:
            self.logger.error(f"Error loading macros: {e}")

    def _register_default_actions(self):
        """Register default action handlers"""

        # Email actions
        self.register_action_handler("check_email", self._check_email_handler)
        self.register_action_handler("read_email", self._read_email_handler)
        self.register_action_handler("send_email", self._send_email_handler)

        # Calendar actions
        self.register_action_handler("check_calendar", self._check_calendar_handler)
        self.register_action_handler("create_event", self._create_event_handler)

        # Task actions
        self.register_action_handler("list_tasks", self._list_tasks_handler)
        self.register_action_handler("create_task", self._create_task_handler)

        # System actions
        self.register_action_handler("enable_dnd", self._enable_dnd_handler)
        self.register_action_handler("disable_dnd", self._disable_dnd_handler)
        self.register_action_handler("speak", self._speak_handler)
        self.register_action_handler("wait", self._wait_handler)

        # AI actions
        self.register_action_handler("ai_query", self._ai_query_handler)

    def _register_default_macros(self):
        """Register default pre-built macros"""

        # Morning routine macro
        morning = VoiceMacro(
            name="morning_routine",
            triggers=["run morning routine", "good morning xeno"],
            description="Complete morning startup routine",
            category="routines",
        )
        morning.add_step("speak", {"text": "Good morning! Starting your daily briefing."})
        morning.add_step("check_email", {}, delay=1)
        morning.add_step("check_calendar", {}, delay=1)
        morning.add_step("list_tasks", {"filter": "due_today"}, delay=1)
        morning.add_step("speak", {"text": "Your morning briefing is complete."})
        self.add_macro(morning)

        # Evening wrap-up macro
        evening = VoiceMacro(
            name="evening_routine",
            triggers=["run evening routine", "wrap up my day"],
            description="Complete evening wrap-up routine",
            category="routines",
        )
        evening.add_step("speak", {"text": "Let's wrap up your day."})
        evening.add_step("list_tasks", {"filter": "completed_today"}, delay=1)
        evening.add_step("check_calendar", {"scope": "tomorrow"}, delay=1)
        evening.add_step(
            "ai_query",
            {"query": "Generate a summary of my productivity today"},
            delay=1,
        )
        evening.add_step("enable_dnd", {"duration_hours": 12})
        evening.add_step("speak", {"text": "Have a great evening!"})
        self.add_macro(evening)

        # Deep focus mode macro
        focus = VoiceMacro(
            name="deep_focus",
            triggers=["enter deep focus", "deep work mode"],
            description="Activate deep focus mode for concentrated work",
            category="productivity",
        )
        focus.add_step("enable_dnd", {"duration_hours": 2, "allow_critical": False})
        focus.add_step("speak", {"text": "Deep focus mode activated. All notifications paused."})
        self.add_macro(focus)

        # Quick email check macro
        quick_email = VoiceMacro(
            name="quick_email_check",
            triggers=["quick email check", "check important emails"],
            description="Check only important/urgent emails",
            category="email",
        )
        quick_email.add_step("check_email", {"filter": "important_only"})
        quick_email.add_step("speak", {"text": "Important emails checked."})
        self.add_macro(quick_email)

    # Action handler implementations (placeholders)
    def _check_email_handler(self, params, context):
        """Check email handler"""
        # TODO: Connect to email_handler
        return "Checking emails..."

    def _read_email_handler(self, params, context):
        """Read email handler"""
        return "Reading email..."

    def _send_email_handler(self, params, context):
        """Send email handler"""
        return "Sending email..."

    def _check_calendar_handler(self, params, context):
        """Check calendar handler"""
        return "Checking calendar..."

    def _create_event_handler(self, params, context):
        """Create event handler"""
        return "Creating event..."

    def _list_tasks_handler(self, params, context):
        """List tasks handler"""
        return "Listing tasks..."

    def _create_task_handler(self, params, context):
        """Create task handler"""
        return "Creating task..."

    def _enable_dnd_handler(self, params, context):
        """Enable DND handler"""
        duration = params.get("duration_hours", 1)
        return f"DND enabled for {duration} hours"

    def _disable_dnd_handler(self, params, context):
        """Disable DND handler"""
        return "DND disabled"

    def _speak_handler(self, params, context):
        """Speak handler"""
        text = params.get("text", "")
        # TODO: Connect to TTS
        return f"Speaking: {text}"

    def _wait_handler(self, params, context):
        """Wait handler"""
        seconds = params.get("seconds", 1)
        time.sleep(seconds)
        return f"Waited {seconds} seconds"

    def _ai_query_handler(self, params, context):
        """AI query handler"""
        query = params.get("query", "")
        # TODO: Connect to AI chat
        return f"AI query: {query}"


# Global instance
_macro_manager: Optional[MacroManager] = None


def get_macro_manager() -> MacroManager:
    """Get global macro manager"""
    global _macro_manager
    if _macro_manager is None:
        _macro_manager = MacroManager()
    return _macro_manager
