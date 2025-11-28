"""
Offline Support
Handles offline operation and queueing
"""

import json
import queue
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from src.core.logger import setup_logger
from src.sync.sync_engine import SyncChange, ChangeType


class OfflineQueue:
    """Queue for offline operations"""

    def __init__(self, storage_path: str = None):
        self.logger = setup_logger("sync.offline")

        if storage_path is None:
            storage_path = Path(__file__).parent.parent.parent / "data" / "offline"

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.queue_file = self.storage_path / "offline_queue.json"

        # In-memory queue
        self._queue: queue.Queue = queue.Queue()

        # Load persisted queue
        self._load_queue()

    def enqueue(self, change: SyncChange):
        """Add change to offline queue"""
        self._queue.put(change)
        self._persist_queue()
        self.logger.debug(f"Queued offline change: {change.change_id}")

    def dequeue(self) -> Optional[SyncChange]:
        """Get next change from queue"""
        try:
            change = self._queue.get_nowait()
            self._persist_queue()
            return change
        except queue.Empty:
            return None

    def peek(self) -> Optional[SyncChange]:
        """Peek at next change without removing"""
        try:
            items = list(self._queue.queue)
            return items[0] if items else None
        except:
            return None

    def size(self) -> int:
        """Get queue size"""
        return self._queue.qsize()

    def clear(self):
        """Clear queue"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        self._persist_queue()
        self.logger.info("Cleared offline queue")

    def get_all(self) -> List[SyncChange]:
        """Get all queued changes"""
        return list(self._queue.queue)

    def _persist_queue(self):
        """Save queue to disk"""
        try:
            changes = list(self._queue.queue)
            data = {
                "changes": [c.to_dict() for c in changes],
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.queue_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to persist queue: {e}")

    def _load_queue(self):
        """Load queue from disk"""
        if not self.queue_file.exists():
            return

        try:
            with open(self.queue_file, "r") as f:
                data = json.load(f)
                changes = [SyncChange.from_dict(c) for c in data.get("changes", [])]

            for change in changes:
                self._queue.put(change)

            self.logger.info(f"Loaded {len(changes)} offline changes")

        except Exception as e:
            self.logger.error(f"Failed to load queue: {e}")


class OfflineManager:
    """Manages offline operation"""

    def __init__(self):
        self.logger = setup_logger("sync.offline_manager")

        # Offline queue
        self.queue = OfflineQueue()

        # Online status
        self._is_online = True
        self._online_callbacks: List[Callable] = []
        self._offline_callbacks: List[Callable] = []

        # Background sync thread
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_sync = threading.Event()

        # Auto-sync settings
        self.auto_sync_enabled = True
        self.sync_interval = 60  # seconds

    def set_online(self, is_online: bool):
        """Set online status"""
        if is_online == self._is_online:
            return

        self._is_online = is_online

        if is_online:
            self.logger.info("Device is now online")
            for callback in self._online_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Online callback error: {e}")

            # Start sync if enabled
            if self.auto_sync_enabled:
                self.start_auto_sync()
        else:
            self.logger.info("Device is now offline")
            for callback in self._offline_callbacks:
                try:
                    callback()
                except Exception as e:
                    self.logger.error(f"Offline callback error: {e}")

            # Stop sync
            self.stop_auto_sync()

    def is_online(self) -> bool:
        """Check if device is online"""
        return self._is_online

    def on_online(self, callback: Callable):
        """Register callback for when device comes online"""
        self._online_callbacks.append(callback)

    def on_offline(self, callback: Callable):
        """Register callback for when device goes offline"""
        self._offline_callbacks.append(callback)

    def queue_change(self, change: SyncChange):
        """Queue a change (works both online and offline)"""
        if self._is_online:
            # If online, could sync immediately or queue for batch
            self.queue.enqueue(change)
        else:
            # If offline, queue for later
            self.queue.enqueue(change)
            self.logger.debug("Change queued for offline sync")

    def process_queue(self, sync_callback: Callable[[List[SyncChange]], bool]) -> int:
        """Process queued changes"""
        processed = 0
        failed_changes = []

        while self.queue.size() > 0:
            change = self.queue.dequeue()
            if change is None:
                break

            try:
                # Attempt to sync
                success = sync_callback([change])

                if success:
                    processed += 1
                else:
                    # Re-queue if failed
                    failed_changes.append(change)
            except Exception as e:
                self.logger.error(f"Failed to process change: {e}")
                failed_changes.append(change)

        # Re-queue failed changes
        for change in failed_changes:
            self.queue.enqueue(change)

        self.logger.info(
            f"Processed {processed} changes, {len(failed_changes)} failed"
        )
        return processed

    def start_auto_sync(self):
        """Start auto-sync background thread"""
        if self._sync_thread and self._sync_thread.is_alive():
            return

        self._stop_sync.clear()
        self._sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self._sync_thread.start()
        self.logger.info("Started auto-sync")

    def stop_auto_sync(self):
        """Stop auto-sync background thread"""
        if self._sync_thread and self._sync_thread.is_alive():
            self._stop_sync.set()
            self._sync_thread.join(timeout=5)
            self.logger.info("Stopped auto-sync")

    def _auto_sync_loop(self):
        """Auto-sync background loop"""
        while not self._stop_sync.is_set():
            if self._is_online and self.queue.size() > 0:
                self.logger.debug("Auto-sync triggered")
                # Trigger sync event (would be handled by sync coordinator)

            # Wait for interval
            self._stop_sync.wait(self.sync_interval)

    def get_status(self) -> Dict[str, Any]:
        """Get offline manager status"""
        return {
            "is_online": self._is_online,
            "queue_size": self.queue.size(),
            "auto_sync_enabled": self.auto_sync_enabled,
            "sync_interval": self.sync_interval,
            "auto_sync_running": self._sync_thread.is_alive()
            if self._sync_thread
            else False,
        }


# Global instance
_offline_manager: Optional[OfflineManager] = None


def get_offline_manager() -> OfflineManager:
    """Get global offline manager"""
    global _offline_manager
    if _offline_manager is None:
        _offline_manager = OfflineManager()
    return _offline_manager
