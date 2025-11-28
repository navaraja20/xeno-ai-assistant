"""
Plugin Manager
Manages plugin lifecycle, discovery, loading, and execution
"""

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger
from src.plugins.plugin_base import (
    Plugin,
    PluginAPI,
    PluginContext,
    PluginManifest,
    PluginStatus,
    PluginType,
)


class PluginSandbox:
    """Sandboxed environment for plugin execution"""

    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.logger = setup_logger(f"plugin.sandbox.{plugin_id}")

        # Resource limits
        self.max_memory_mb = 100
        self.max_cpu_time_seconds = 30
        self.allowed_modules = [
            "json",
            "datetime",
            "re",
            "math",
            "random",
            "collections",
            "itertools",
        ]

    def validate_permissions(self, permissions: List[str]) -> bool:
        """Validate requested permissions"""
        allowed_permissions = [
            "tasks.read",
            "tasks.write",
            "notifications.send",
            "memory.read",
            "memory.write",
            "workflows.execute",
            "analytics.track",
            "filesystem.read",
            "filesystem.write",
            "network.access",
        ]

        for permission in permissions:
            if permission not in allowed_permissions:
                self.logger.error(f"Invalid permission requested: {permission}")
                return False

        return True

    def validate_imports(self, module_name: str) -> bool:
        """Validate module imports"""
        # Check if module is in allowed list
        base_module = module_name.split(".")[0]

        if base_module in self.allowed_modules:
            return True

        # Allow imports from src.plugins
        if module_name.startswith("src.plugins"):
            return True

        self.logger.warning(f"Module import blocked: {module_name}")
        return False


class PluginManager:
    """Manages all plugins"""

    def __init__(self, plugins_dir: str = None):
        self.logger = setup_logger("plugin.manager")

        # Plugin directory
        if plugins_dir is None:
            plugins_dir = os.path.join(os.path.dirname(__file__), "installed")
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

        # Loaded plugins
        self.plugins: Dict[str, Plugin] = {}
        self.manifests: Dict[str, PluginManifest] = {}

        # Plugin API
        self.plugin_api = PluginAPI()

        # Registry file
        self.registry_file = self.plugins_dir / "registry.json"
        self._load_registry()

    def _load_registry(self):
        """Load plugin registry"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    registry = json.load(f)

                for plugin_data in registry.get("plugins", []):
                    manifest = PluginManifest.from_dict(plugin_data)
                    self.manifests[manifest.id] = manifest

                self.logger.info(f"Loaded {len(self.manifests)} plugins from registry")
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}")

    def _save_registry(self):
        """Save plugin registry"""
        try:
            registry = {
                "plugins": [m.to_dict() for m in self.manifests.values()],
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.registry_file, "w") as f:
                json.dump(registry, f, indent=2)

            self.logger.debug("Registry saved")
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")

    def discover_plugins(self) -> List[PluginManifest]:
        """Discover available plugins"""
        discovered = []

        # Scan plugins directory
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue

            # Look for manifest.json
            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)

                manifest = PluginManifest.from_dict(data)
                discovered.append(manifest)

                # Add to registry if not present
                if manifest.id not in self.manifests:
                    self.manifests[manifest.id] = manifest

                self.logger.info(f"Discovered plugin: {manifest.name}")
            except Exception as e:
                self.logger.error(f"Failed to load manifest from {plugin_dir}: {e}")

        self._save_registry()
        return discovered

    def install_plugin(self, plugin_path: str) -> Optional[str]:
        """
        Install plugin from path

        Args:
            plugin_path: Path to plugin directory or zip file

        Returns:
            Plugin ID if successful
        """
        plugin_path = Path(plugin_path)

        # Check if it's a directory
        if plugin_path.is_dir():
            manifest_file = plugin_path / "manifest.json"
            if not manifest_file.exists():
                self.logger.error("No manifest.json found")
                return None

            # Load manifest
            try:
                with open(manifest_file, "r") as f:
                    data = json.load(f)
                manifest = PluginManifest.from_dict(data)
            except Exception as e:
                self.logger.error(f"Failed to load manifest: {e}")
                return None

            # Copy plugin to plugins directory
            import shutil

            dest_dir = self.plugins_dir / manifest.id
            if dest_dir.exists():
                self.logger.warning(f"Plugin {manifest.id} already exists, updating...")
                shutil.rmtree(dest_dir)

            shutil.copytree(plugin_path, dest_dir)

            # Add to registry
            self.manifests[manifest.id] = manifest
            self._save_registry()

            self.logger.info(f"Installed plugin: {manifest.name}")
            return manifest.id

        else:
            self.logger.error("Plugin path must be a directory")
            return None

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall plugin"""
        if plugin_id not in self.manifests:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return False

        # Deactivate if active
        if plugin_id in self.plugins:
            self.deactivate_plugin(plugin_id)

        # Remove from filesystem
        plugin_dir = self.plugins_dir / plugin_id
        if plugin_dir.exists():
            import shutil

            shutil.rmtree(plugin_dir)

        # Remove from registry
        del self.manifests[plugin_id]
        self._save_registry()

        self.logger.info(f"Uninstalled plugin: {plugin_id}")
        return True

    def load_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Load plugin into memory"""
        if plugin_id not in self.manifests:
            self.logger.error(f"Plugin not found: {plugin_id}")
            return None

        manifest = self.manifests[plugin_id]

        # Check if already loaded
        if plugin_id in self.plugins:
            return self.plugins[plugin_id]

        # Validate permissions
        sandbox = PluginSandbox(plugin_id)
        if not sandbox.validate_permissions(manifest.permissions):
            self.logger.error(f"Invalid permissions for plugin: {plugin_id}")
            return None

        # Load plugin module
        plugin_dir = self.plugins_dir / plugin_id
        entry_file = plugin_dir / manifest.entry_point

        if not entry_file.exists():
            self.logger.error(f"Entry point not found: {manifest.entry_point}")
            return None

        try:
            # Import module
            spec = importlib.util.spec_from_file_location(f"plugins.{plugin_id}", entry_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"plugins.{plugin_id}"] = module
            spec.loader.exec_module(module)

            # Get plugin class
            if not hasattr(module, "Plugin"):
                self.logger.error("Plugin class not found in module")
                return None

            # Instantiate plugin
            plugin = module.Plugin()
            plugin.manifest = manifest

            # Create context
            context = PluginContext()
            context.logger = setup_logger(f"plugin.{plugin_id}")
            context.data_dir = plugin_dir / "data"
            context.data_dir.mkdir(exist_ok=True)
            context.api = self.plugin_api

            # Initialize plugin
            config = {}  # Load from config file if exists
            if plugin.initialize(context, config):
                plugin.context = context
                self.plugins[plugin_id] = plugin
                self.logger.info(f"Loaded plugin: {manifest.name}")
                return plugin
            else:
                self.logger.error(f"Failed to initialize plugin: {plugin_id}")
                return None

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return None

    def activate_plugin(self, plugin_id: str) -> bool:
        """Activate plugin"""
        # Load if not loaded
        plugin = self.plugins.get(plugin_id)
        if plugin is None:
            plugin = self.load_plugin(plugin_id)

        if plugin is None:
            return False

        try:
            if plugin.activate():
                plugin._is_active = True
                self.manifests[plugin_id].status = PluginStatus.ACTIVE
                self._save_registry()
                self.logger.info(f"Activated plugin: {plugin_id}")
                return True
            else:
                self.logger.error(f"Failed to activate plugin: {plugin_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error activating plugin {plugin_id}: {e}")
            self.manifests[plugin_id].status = PluginStatus.ERROR
            self._save_registry()
            return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """Deactivate plugin"""
        if plugin_id not in self.plugins:
            self.logger.warning(f"Plugin not loaded: {plugin_id}")
            return False

        plugin = self.plugins[plugin_id]

        try:
            if plugin.deactivate():
                plugin._is_active = False
                self.manifests[plugin_id].status = PluginStatus.INACTIVE
                self._save_registry()
                self.logger.info(f"Deactivated plugin: {plugin_id}")
                return True
            else:
                self.logger.error(f"Failed to deactivate plugin: {plugin_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error deactivating plugin {plugin_id}: {e}")
            return False

    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get loaded plugin"""
        return self.plugins.get(plugin_id)

    def list_plugins(self, status_filter: Optional[PluginStatus] = None) -> List[PluginManifest]:
        """List all plugins"""
        manifests = list(self.manifests.values())

        if status_filter:
            manifests = [m for m in manifests if m.status == status_filter]

        return manifests

    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get plugin information"""
        if plugin_id in self.manifests:
            return self.manifests[plugin_id].to_dict()
        return None

    def execute_plugin(self, plugin_id: str, method: str, *args, **kwargs) -> Optional[Any]:
        """Execute plugin method"""
        plugin = self.get_plugin(plugin_id)
        if plugin is None or not plugin.is_active:
            self.logger.error(f"Plugin not active: {plugin_id}")
            return None

        if not hasattr(plugin, method):
            self.logger.error(f"Method not found: {method}")
            return None

        try:
            method_func = getattr(plugin, method)
            result = method_func(*args, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f"Error executing {method} on {plugin_id}: {e}")
            return None


# Global instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
