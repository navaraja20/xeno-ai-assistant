"""
Sync Coordinator
Coordinates synchronization across devices
"""

import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger
from src.sync.cloud_storage import CloudStorageManager, get_cloud_manager
from src.sync.offline_support import OfflineManager, get_offline_manager
from src.sync.sync_engine import ChangeType, SyncChange, SyncEngine, SyncStatus


class SyncCoordinator:
    """Coordinates synchronization"""

    def __init__(self, device_id: str):
        self.logger = setup_logger("sync.coordinator")
        self.device_id = device_id

        # Components
        self.sync_engine = SyncEngine(device_id)
        self.cloud_manager = get_cloud_manager()
        self.offline_manager = get_offline_manager()

        # Sync callbacks
        self._sync_callbacks: List[Callable[[Dict[str, Any]], None]] = []

        # Auto-sync configuration
        self.auto_sync_interval = 300  # 5 minutes

        # Register offline callbacks
        self.offline_manager.on_online(self._on_device_online)
        self.offline_manager.on_offline(self._on_device_offline)

    def track_change(
        self,
        change_type: ChangeType,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
    ) -> SyncChange:
        """Track a local change"""
        change = self.sync_engine.track_change(change_type, entity_type, entity_id, data)

        # Queue for sync
        if self.offline_manager.is_online():
            # Online - could sync immediately or batch
            self.logger.debug(f"Change tracked, will sync on next cycle")
        else:
            # Offline - queue for later
            self.offline_manager.queue_change(change)
            self.logger.debug(f"Change queued for offline sync")

        return change

    def sync_now(self) -> Dict[str, Any]:
        """Perform immediate sync"""
        self.logger.info("Starting sync...")

        results = {
            "status": "success",
            "uploaded": 0,
            "downloaded": 0,
            "conflicts": 0,
            "errors": [],
        }

        try:
            # Check if online
            if not self.offline_manager.is_online():
                results["status"] = "offline"
                results["errors"].append("Device is offline")
                return results

            # 1. Upload local changes
            pending_changes = self.sync_engine.get_pending_changes()

            if pending_changes:
                upload_success = self.cloud_manager.upload_to_cloud(pending_changes)

                if upload_success:
                    results["uploaded"] = len(pending_changes)
                    self.logger.info(f"Uploaded {len(pending_changes)} changes")
                else:
                    results["errors"].append("Failed to upload changes")

            # 2. Download remote changes
            last_sync = self.sync_engine.last_sync_time
            remote_changes = self.cloud_manager.download_from_cloud(since=last_sync)

            if remote_changes:
                # Filter out our own changes
                remote_changes = [c for c in remote_changes if c.device_id != self.device_id]

                # Apply remote changes
                apply_results = self.sync_engine.apply_remote_changes(remote_changes)

                results["downloaded"] = len(apply_results["applied"])
                results["conflicts"] = len(apply_results["conflicts"])

                if apply_results["errors"]:
                    results["errors"].extend(apply_results["errors"])

                self.logger.info(
                    f"Downloaded {len(remote_changes)} changes, "
                    f"applied {results['downloaded']}, "
                    f"{results['conflicts']} conflicts"
                )

            # 3. Clear successfully synced changes
            if results["uploaded"] > 0:
                self.sync_engine.clear_pending_changes()

            # 4. Process offline queue
            if self.offline_manager.queue.size() > 0:
                processed = self.offline_manager.process_queue(
                    lambda changes: self.cloud_manager.upload_to_cloud(changes)
                )
                results["uploaded"] += processed

            # Notify callbacks
            self._notify_sync_complete(results)

        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            results["status"] = "error"
            results["errors"].append(str(e))

        return results

    def on_sync_complete(self, callback: Callable[[Dict[str, Any]], None]):
        """Register callback for sync completion"""
        self._sync_callbacks.append(callback)

    def _notify_sync_complete(self, results: Dict[str, Any]):
        """Notify all sync callbacks"""
        for callback in self._sync_callbacks:
            try:
                callback(results)
            except Exception as e:
                self.logger.error(f"Sync callback error: {e}")

    def _on_device_online(self):
        """Handle device coming online"""
        self.logger.info("Device online - triggering sync")
        self.sync_now()

    def _on_device_offline(self):
        """Handle device going offline"""
        self.logger.info("Device offline - pausing sync")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive sync status"""
        return {
            "device_id": self.device_id,
            "sync_engine": self.sync_engine.get_sync_status(),
            "offline": self.offline_manager.get_status(),
            "cloud_provider": self.cloud_manager.active_provider.provider_name
            if self.cloud_manager.active_provider
            else None,
            "unresolved_conflicts": len(self.sync_engine.get_conflicts()),
        }

    def resolve_conflict(self, entity_id: str, resolution_change: SyncChange) -> bool:
        """Manually resolve a sync conflict"""
        return self.sync_engine.resolve_conflict_manually(entity_id, resolution_change)

    def get_conflicts(self):
        """Get all unresolved conflicts"""
        return self.sync_engine.get_conflicts()

    def enable_auto_sync(self, enabled: bool = True):
        """Enable or disable auto-sync"""
        self.offline_manager.auto_sync_enabled = enabled

        if enabled:
            self.offline_manager.start_auto_sync()
            self.logger.info("Auto-sync enabled")
        else:
            self.offline_manager.stop_auto_sync()
            self.logger.info("Auto-sync disabled")

    def set_sync_interval(self, seconds: int):
        """Set auto-sync interval"""
        self.offline_manager.sync_interval = seconds
        self.logger.info(f"Sync interval set to {seconds} seconds")


# Global instance
_sync_coordinator: Optional[SyncCoordinator] = None


def get_sync_coordinator(device_id: str = None) -> SyncCoordinator:
    """Get global sync coordinator"""
    global _sync_coordinator

    if _sync_coordinator is None:
        if device_id is None:
            # Generate device ID from machine info
            import hashlib
            import platform

            machine_info = f"{platform.node()}_{platform.machine()}"
            device_id = hashlib.md5(machine_info.encode()).hexdigest()[:12]

        _sync_coordinator = SyncCoordinator(device_id)

    return _sync_coordinator
