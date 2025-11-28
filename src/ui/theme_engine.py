"""
Context-Aware Theme Engine
Dynamically adapts UI themes based on time, activity, emotion, and context
"""

import json
from datetime import datetime, time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class ThemeMode(Enum):
    """Theme modes"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # Time-based


class ActivityContext(Enum):
    """Activity contexts"""

    FOCUS = "focus"
    CREATIVE = "creative"
    MEETING = "meeting"
    RELAX = "relax"
    ADMIN = "admin"
    DEFAULT = "default"


class EmotionState(Enum):
    """Emotional states"""

    CALM = "calm"
    ENERGIZED = "energized"
    STRESSED = "stressed"
    NEUTRAL = "neutral"


class Theme:
    """Theme definition"""

    def __init__(
        self,
        name: str,
        colors: Dict[str, str],
        fonts: Dict[str, str] = None,
        animations: Dict[str, Any] = None,
        description: str = "",
    ):
        self.name = name
        self.colors = colors
        self.fonts = fonts or {}
        self.animations = animations or {}
        self.description = description

    def get_color(self, key: str, default: str = "#FFFFFF") -> str:
        """Get color by key"""
        return self.colors.get(key, default)

    def get_font(self, key: str, default: str = "Segoe UI") -> str:
        """Get font by key"""
        return self.fonts.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "colors": self.colors,
            "fonts": self.fonts,
            "animations": self.animations,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Theme":
        """Create from dictionary"""
        return Theme(
            name=data["name"],
            colors=data["colors"],
            fonts=data.get("fonts", {}),
            animations=data.get("animations", {}),
            description=data.get("description", ""),
        )

    def generate_qss(self) -> str:
        """Generate Qt StyleSheet (QSS) from theme"""

        qss = f"""
/* {self.name} Theme */

QWidget {{
    background-color: {self.get_color('background')};
    color: {self.get_color('text')};
    font-family: {self.get_font('primary')};
    font-size: 12px;
}}

QPushButton {{
    background-color: {self.get_color('primary')};
    color: {self.get_color('button_text', '#FFFFFF')};
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {self.get_color('primary_hover')};
}}

QPushButton:pressed {{
    background-color: {self.get_color('primary_pressed')};
}}

QPushButton:disabled {{
    background-color: {self.get_color('disabled', '#CCCCCC')};
    color: {self.get_color('disabled_text', '#888888')};
}}

QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {self.get_color('input_background')};
    color: {self.get_color('text')};
    border: 1px solid {self.get_color('border')};
    border-radius: 3px;
    padding: 5px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {self.get_color('primary')};
}}

QGroupBox {{
    border: 1px solid {self.get_color('border')};
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}}

QGroupBox::title {{
    color: {self.get_color('heading')};
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}}

QTabWidget::pane {{
    border: 1px solid {self.get_color('border')};
    background-color: {self.get_color('surface')};
}}

QTabBar::tab {{
    background-color: {self.get_color('tab_background')};
    color: {self.get_color('tab_text')};
    padding: 8px 16px;
    border: 1px solid {self.get_color('border')};
}}

QTabBar::tab:selected {{
    background-color: {self.get_color('primary')};
    color: {self.get_color('button_text', '#FFFFFF')};
}}

QScrollBar:vertical {{
    background-color: {self.get_color('surface')};
    width: 12px;
}}

QScrollBar::handle:vertical {{
    background-color: {self.get_color('scrollbar')};
    border-radius: 6px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {self.get_color('scrollbar_hover')};
}}

QLabel {{
    color: {self.get_color('text')};
}}

QLabel[heading="true"] {{
    color: {self.get_color('heading')};
    font-size: 16px;
    font-weight: bold;
}}

QComboBox {{
    background-color: {self.get_color('input_background')};
    color: {self.get_color('text')};
    border: 1px solid {self.get_color('border')};
    border-radius: 3px;
    padding: 5px;
}}

QComboBox:hover {{
    border: 1px solid {self.get_color('primary')};
}}

QListWidget, QTreeWidget {{
    background-color: {self.get_color('surface')};
    color: {self.get_color('text')};
    border: 1px solid {self.get_color('border')};
}}

QListWidget::item:selected, QTreeWidget::item:selected {{
    background-color: {self.get_color('primary')};
    color: {self.get_color('button_text', '#FFFFFF')};
}}

QMenuBar {{
    background-color: {self.get_color('menubar')};
    color: {self.get_color('text')};
}}

QMenuBar::item:selected {{
    background-color: {self.get_color('primary')};
    color: {self.get_color('button_text', '#FFFFFF')};
}}

QMenu {{
    background-color: {self.get_color('surface')};
    color: {self.get_color('text')};
    border: 1px solid {self.get_color('border')};
}}

QMenu::item:selected {{
    background-color: {self.get_color('primary')};
    color: {self.get_color('button_text', '#FFFFFF')};
}}

QStatusBar {{
    background-color: {self.get_color('statusbar')};
    color: {self.get_color('text')};
}}

QProgressBar {{
    background-color: {self.get_color('surface')};
    border: 1px solid {self.get_color('border')};
    border-radius: 3px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {self.get_color('primary')};
    border-radius: 2px;
}}
"""
        return qss


class ThemeEngine:
    """Main theme engine"""

    def __init__(self, themes_file: str = "data/themes.json"):
        self.logger = setup_logger("theme.engine")
        self.themes_file = Path(themes_file)
        self.themes: Dict[str, Theme] = {}

        # Current state
        self.current_theme: Optional[Theme] = None
        self.theme_mode = ThemeMode.AUTO
        self.current_context = ActivityContext.DEFAULT
        self.current_emotion = EmotionState.NEUTRAL

        # Callbacks
        self.theme_change_callbacks: List[Callable] = []

        # Transition settings
        self.transition_enabled = True
        self.transition_duration_ms = 300

        # Ensure data directory exists
        self.themes_file.parent.mkdir(parents=True, exist_ok=True)

        # Load themes
        self._load_themes()
        self._register_default_themes()

        # Apply initial theme
        self._apply_auto_theme()

    def add_theme(self, theme: Theme):
        """Add or update theme"""
        self.themes[theme.name] = theme
        self._save_themes()
        self.logger.info(f"Added theme: {theme.name}")

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(name)

    def list_themes(self) -> List[str]:
        """List all theme names"""
        return list(self.themes.keys())

    def set_theme(self, theme_name: str):
        """Manually set theme"""
        theme = self.get_theme(theme_name)

        if not theme:
            self.logger.error(f"Theme not found: {theme_name}")
            return

        self._apply_theme(theme)

    def set_theme_mode(self, mode: ThemeMode):
        """Set theme mode (light/dark/auto)"""
        self.theme_mode = mode
        self._apply_auto_theme()

    def set_context(self, context: ActivityContext):
        """Set activity context"""
        self.current_context = context
        self._apply_context_theme()

    def set_emotion(self, emotion: EmotionState):
        """Set emotion state"""
        self.current_emotion = emotion
        self._apply_emotion_theme()

    def get_current_theme(self) -> Optional[Theme]:
        """Get currently active theme"""
        return self.current_theme

    def add_theme_change_callback(self, callback: Callable):
        """Add callback for theme changes"""
        self.theme_change_callbacks.append(callback)

    def enable_transitions(self, enabled: bool = True):
        """Enable/disable theme transitions"""
        self.transition_enabled = enabled

    def _apply_theme(self, theme: Theme):
        """Apply theme"""
        if self.current_theme == theme:
            return

        self.logger.info(f"Applying theme: {theme.name}")

        self.current_theme = theme

        # Notify callbacks
        for callback in self.theme_change_callbacks:
            try:
                callback(theme)
            except Exception as e:
                self.logger.error(f"Theme callback error: {e}")

    def _apply_auto_theme(self):
        """Apply theme based on mode and time"""

        if self.theme_mode == ThemeMode.LIGHT:
            theme = self.get_theme("light_modern")
        elif self.theme_mode == ThemeMode.DARK:
            theme = self.get_theme("dark_modern")
        else:  # AUTO
            # Time-based
            current_hour = datetime.now().hour

            if 6 <= current_hour < 18:  # Daytime (6 AM - 6 PM)
                theme = self.get_theme("light_modern")
            else:  # Nighttime
                theme = self.get_theme("dark_modern")

        if theme:
            self._apply_theme(theme)

    def _apply_context_theme(self):
        """Apply theme based on activity context"""

        context_themes = {
            ActivityContext.FOCUS: "focus_minimal",
            ActivityContext.CREATIVE: "creative_vibrant",
            ActivityContext.MEETING: "meeting_professional",
            ActivityContext.RELAX: "relax_calm",
            ActivityContext.ADMIN: "light_modern",
        }

        theme_name = context_themes.get(
            self.current_context, "light_modern"
        )
        theme = self.get_theme(theme_name)

        if theme:
            self._apply_theme(theme)

    def _apply_emotion_theme(self):
        """Apply theme based on emotion"""

        emotion_themes = {
            EmotionState.CALM: "relax_calm",
            EmotionState.ENERGIZED: "energized_bright",
            EmotionState.STRESSED: "calm_soothing",
            EmotionState.NEUTRAL: "light_modern",
        }

        theme_name = emotion_themes.get(self.current_emotion, "light_modern")
        theme = self.get_theme(theme_name)

        if theme:
            self._apply_theme(theme)

    def _save_themes(self):
        """Save themes to file"""
        try:
            data = {name: theme.to_dict() for name, theme in self.themes.items()}

            with open(self.themes_file, "w") as f:
                json.dump(data, f, indent=2)

            self.logger.debug(f"Saved {len(self.themes)} themes")
        except Exception as e:
            self.logger.error(f"Error saving themes: {e}")

    def _load_themes(self):
        """Load themes from file"""
        if not self.themes_file.exists():
            return

        try:
            with open(self.themes_file, "r") as f:
                data = json.load(f)

            for name, theme_data in data.items():
                self.themes[name] = Theme.from_dict(theme_data)

            self.logger.info(f"Loaded {len(self.themes)} themes")
        except Exception as e:
            self.logger.error(f"Error loading themes: {e}")

    def _register_default_themes(self):
        """Register default built-in themes"""

        # Modern Light Theme
        light_modern = Theme(
            name="light_modern",
            description="Clean modern light theme",
            colors={
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "primary": "#007ACC",
                "primary_hover": "#005A9E",
                "primary_pressed": "#004578",
                "text": "#333333",
                "heading": "#1A1A1A",
                "border": "#DDDDDD",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#E0E0E0",
                "tab_text": "#333333",
                "scrollbar": "#CCCCCC",
                "scrollbar_hover": "#999999",
                "menubar": "#F5F5F5",
                "statusbar": "#F0F0F0",
                "disabled": "#E0E0E0",
                "disabled_text": "#999999",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Semibold"},
        )
        self.add_theme(light_modern)

        # Modern Dark Theme
        dark_modern = Theme(
            name="dark_modern",
            description="Sleek modern dark theme",
            colors={
                "background": "#1E1E1E",
                "surface": "#252526",
                "primary": "#0E639C",
                "primary_hover": "#1177BB",
                "primary_pressed": "#005A9E",
                "text": "#CCCCCC",
                "heading": "#FFFFFF",
                "border": "#3E3E42",
                "input_background": "#2D2D30",
                "button_text": "#FFFFFF",
                "tab_background": "#2D2D30",
                "tab_text": "#CCCCCC",
                "scrollbar": "#424242",
                "scrollbar_hover": "#555555",
                "menubar": "#2D2D30",
                "statusbar": "#007ACC",
                "disabled": "#3E3E42",
                "disabled_text": "#6E6E6E",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Semibold"},
        )
        self.add_theme(dark_modern)

        # Focus Minimal Theme (reduced distractions)
        focus_minimal = Theme(
            name="focus_minimal",
            description="Minimal distraction-free theme for deep work",
            colors={
                "background": "#FAFAFA",
                "surface": "#F0F0F0",
                "primary": "#6C757D",
                "primary_hover": "#5A6268",
                "primary_pressed": "#495057",
                "text": "#495057",
                "heading": "#212529",
                "border": "#E0E0E0",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#E8E8E8",
                "tab_text": "#495057",
                "scrollbar": "#D0D0D0",
                "scrollbar_hover": "#B0B0B0",
                "menubar": "#F0F0F0",
                "statusbar": "#E8E8E8",
            },
            fonts={"primary": "Calibri", "heading": "Calibri"},
        )
        self.add_theme(focus_minimal)

        # Creative Vibrant Theme
        creative_vibrant = Theme(
            name="creative_vibrant",
            description="Colorful vibrant theme for creative work",
            colors={
                "background": "#FFFFFF",
                "surface": "#FFF8F0",
                "primary": "#E83E8C",
                "primary_hover": "#D6277A",
                "primary_pressed": "#BD2167",
                "text": "#333333",
                "heading": "#6F42C1",
                "border": "#FFD6E8",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#FFE8F0",
                "tab_text": "#333333",
                "scrollbar": "#FFB3D9",
                "scrollbar_hover": "#FF8CC5",
                "menubar": "#FFF0F8",
                "statusbar": "#FFE0EE",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Bold"},
        )
        self.add_theme(creative_vibrant)

        # Meeting Professional Theme
        meeting_professional = Theme(
            name="meeting_professional",
            description="Professional theme for meetings",
            colors={
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "primary": "#0056B3",
                "primary_hover": "#004494",
                "primary_pressed": "#003D82",
                "text": "#212529",
                "heading": "#0056B3",
                "border": "#DEE2E6",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#E9ECEF",
                "tab_text": "#212529",
                "scrollbar": "#CED4DA",
                "scrollbar_hover": "#ADB5BD",
                "menubar": "#F8F9FA",
                "statusbar": "#E9ECEF",
            },
            fonts={"primary": "Arial", "heading": "Arial Bold"},
        )
        self.add_theme(meeting_professional)

        # Relax Calm Theme
        relax_calm = Theme(
            name="relax_calm",
            description="Calming theme for relaxation",
            colors={
                "background": "#F0F8FF",
                "surface": "#E6F2FF",
                "primary": "#17A2B8",
                "primary_hover": "#138496",
                "primary_pressed": "#117A8B",
                "text": "#2C3E50",
                "heading": "#17A2B8",
                "border": "#BEE5EB",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#D1ECF1",
                "tab_text": "#2C3E50",
                "scrollbar": "#A8DADC",
                "scrollbar_hover": "#81C4C8",
                "menubar": "#D1ECF1",
                "statusbar": "#BEE5EB",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Light"},
        )
        self.add_theme(relax_calm)

        # Energized Bright Theme
        energized_bright = Theme(
            name="energized_bright",
            description="Bright energizing theme",
            colors={
                "background": "#FFFFFF",
                "surface": "#FFF9E6",
                "primary": "#FFC107",
                "primary_hover": "#E0A800",
                "primary_pressed": "#C69500",
                "text": "#212529",
                "heading": "#FF6F00",
                "border": "#FFE082",
                "input_background": "#FFFFFF",
                "button_text": "#212529",
                "tab_background": "#FFF3CD",
                "tab_text": "#212529",
                "scrollbar": "#FFD54F",
                "scrollbar_hover": "#FFCA28",
                "menubar": "#FFF9E6",
                "statusbar": "#FFF3CD",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Bold"},
        )
        self.add_theme(energized_bright)

        # Calm Soothing Theme (for stress relief)
        calm_soothing = Theme(
            name="calm_soothing",
            description="Soothing theme to reduce stress",
            colors={
                "background": "#F5F9F5",
                "surface": "#E8F5E9",
                "primary": "#28A745",
                "primary_hover": "#218838",
                "primary_pressed": "#1E7E34",
                "text": "#2E4A2E",
                "heading": "#28A745",
                "border": "#C8E6C9",
                "input_background": "#FFFFFF",
                "button_text": "#FFFFFF",
                "tab_background": "#C8E6C9",
                "tab_text": "#2E4A2E",
                "scrollbar": "#A5D6A7",
                "scrollbar_hover": "#81C784",
                "menubar": "#E8F5E9",
                "statusbar": "#C8E6C9",
            },
            fonts={"primary": "Segoe UI", "heading": "Segoe UI Light"},
        )
        self.add_theme(calm_soothing)


# Global instance
_theme_engine: Optional[ThemeEngine] = None


def get_theme_engine() -> ThemeEngine:
    """Get global theme engine"""
    global _theme_engine
    if _theme_engine is None:
        _theme_engine = ThemeEngine()
    return _theme_engine
