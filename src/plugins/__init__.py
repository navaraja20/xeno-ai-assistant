"""
Plugins Module
Exports all plugin components
"""

from src.plugins.plugin_base import (
    AIPlugin,
    AnalyticsPlugin,
    AutomationPlugin,
    IntegrationPlugin,
    Plugin,
    PluginAPI,
    PluginContext,
    PluginManifest,
    PluginStatus,
    PluginType,
    UIPlugin,
    UtilityPlugin,
)
from src.plugins.plugin_manager import PluginManager, PluginSandbox, get_plugin_manager
from src.plugins.plugin_sdk import PluginSDK, get_plugin_sdk

__all__ = [
    # Base Classes
    "Plugin",
    "PluginContext",
    "PluginManifest",
    "PluginStatus",
    "PluginType",
    "PluginAPI",
    # Specialized Plugins
    "AutomationPlugin",
    "IntegrationPlugin",
    "UIPlugin",
    "AnalyticsPlugin",
    "AIPlugin",
    "UtilityPlugin",
    # Plugin Manager
    "PluginManager",
    "PluginSandbox",
    "get_plugin_manager",
    # SDK
    "PluginSDK",
    "get_plugin_sdk",
]
