"""
Sync Engine
Core synchronization engine for multi-device sync
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from src.core.logger import setup_logger


class SyncStatus(Enum):
    """Sync status"""

    IDLE = "idle"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    SUCCESS = "success"


class ChangeType(Enum):
    """Type of change"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class SyncChange:
    """Represents a sync change"""

    def __init__(
        self,
        change_id: str,
        change_type: ChangeType,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
        timestamp: datetime,
        device_id: str,
        version: int = 1,
    ):
        self.change_id = change_id
        self.change_type = change_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.data = data
        self.timestamp = timestamp
        self.device_id = device_id
        self.version = version

        # Checksum for data integrity
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for data"""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "change_id": self.change_id,
            "change_type": self.change_type.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "device_id": self.device_id,
            "version": self.version,
            "checksum": self.checksum,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncChange":
        """Create from dictionary"""
        return cls(
            change_id=data["change_id"],
            change_type=ChangeType(data["change_type"]),
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            device_id=data["device_id"],
            version=data.get("version", 1),
        )


class ConflictResolution(Enum):
    """Conflict resolution strategies"""

    LATEST_WINS = "latest_wins"  # Most recent change wins
    DEVICE_PRIORITY = "device_priority"  # Specific device takes priority
    MANUAL = "manual"  # Require manual resolution
    MERGE = "merge"  # Attempt to merge changes


class SyncConflict:
    """Represents a sync conflict"""

    def __init__(
        self,
        entity_type: str,
        entity_id: str,
        local_change: SyncChange,
        remote_change: SyncChange,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.local_change = local_change
        self.remote_change = remote_change
        self.resolved = False
        self.resolution = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "local_change": self.local_change.to_dict(),
            "remote_change": self.remote_change.to_dict(),
            "resolved": self.resolved,
            "resolution": self.resolution.to_dict() if self.resolution else None,
        }


class SyncEngine:
    """Core synchronization engine"""

    def __init__(self, device_id: str):
        self.logger = setup_logger("sync.engine")
        self.device_id = device_id

        # Change tracking
        self.pending_changes: List[SyncChange] = []
        self.applied_changes: Set[str] = set()  # Track applied change IDs

        # Conflict tracking
        self.conflicts: List[SyncConflict] = []

        # Sync state
        self.status = SyncStatus.IDLE
        self.last_sync_time: Optional[datetime] = None

        # Conflict resolution strategy
        self.conflict_strategy = ConflictResolution.LATEST_WINS

        # Version tracking (entity_id -> version)
        self.entity_versions: Dict[str, int] = {}

    def track_change(
        self,
        change_type: ChangeType,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
    ) -> SyncChange:
        """Track a local change"""
        # Generate change ID
        change_id = f"{self.device_id}_{entity_id}_{int(time.time() * 1000)}"

        # Get current version
        current_version = self.entity_versions.get(entity_id, 0)
        new_version = current_version + 1

        # Create change
        change = SyncChange(
            change_id=change_id,
            change_type=change_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            timestamp=datetime.now(),
            device_id=self.device_id,
            version=new_version,
        )

        # Add to pending changes
        self.pending_changes.append(change)

        # Update version
        self.entity_versions[entity_id] = new_version

        self.logger.debug(f"Tracked {change_type.value} for {entity_type}:{entity_id}")
        return change

    def get_pending_changes(self) -> List[SyncChange]:
        """Get pending changes to sync"""
        return self.pending_changes.copy()

    def apply_remote_changes(
        self, remote_changes: List[SyncChange]
    ) -> Dict[str, Any]:
        """Apply changes from remote device"""
        self.status = SyncStatus.SYNCING
        results = {
            "applied": [],
            "conflicts": [],
            "errors": [],
        }

        for remote_change in remote_changes:
            # Skip if already applied
            if remote_change.change_id in self.applied_changes:
                continue

            # Check for conflicts
            conflict = self._detect_conflict(remote_change)

            if conflict:
                # Handle conflict
                resolution = self._resolve_conflict(conflict)

                if resolution:
                    results["applied"].append(resolution.to_dict())
                    self.applied_changes.add(remote_change.change_id)
                else:
                    results["conflicts"].append(conflict.to_dict())
                    self.conflicts.append(conflict)
            else:
                # No conflict, apply change
                try:
                    self._apply_change(remote_change)
                    results["applied"].append(remote_change.to_dict())
                    self.applied_changes.add(remote_change.change_id)
                except Exception as e:
                    self.logger.error(f"Error applying change: {e}")
                    results["errors"].append(
                        {"change": remote_change.to_dict(), "error": str(e)}
                    )

        # Clear applied pending changes
        self.pending_changes = [
            c for c in self.pending_changes if c.change_id not in self.applied_changes
        ]

        self.status = SyncStatus.SUCCESS if not results["conflicts"] else SyncStatus.CONFLICT
        self.last_sync_time = datetime.now()

        self.logger.info(
            f"Applied {len(results['applied'])} changes, "
            f"{len(results['conflicts'])} conflicts, "
            f"{len(results['errors'])} errors"
        )

        return results

    def _detect_conflict(self, remote_change: SyncChange) -> Optional[SyncConflict]:
        """Detect if remote change conflicts with local changes"""
        # Find local changes for same entity
        local_changes = [
            c
            for c in self.pending_changes
            if c.entity_id == remote_change.entity_id
            and c.entity_type == remote_change.entity_type
        ]

        if not local_changes:
            return None

        # Get most recent local change
        local_change = max(local_changes, key=lambda c: c.timestamp)

        # Check if changes conflict
        if self._changes_conflict(local_change, remote_change):
            return SyncConflict(
                entity_type=remote_change.entity_type,
                entity_id=remote_change.entity_id,
                local_change=local_change,
                remote_change=remote_change,
            )

        return None

    def _changes_conflict(self, change1: SyncChange, change2: SyncChange) -> bool:
        """Check if two changes conflict"""
        # Both are deletes - no conflict
        if (
            change1.change_type == ChangeType.DELETE
            and change2.change_type == ChangeType.DELETE
        ):
            return False

        # Different checksums indicate conflict
        if change1.checksum != change2.checksum:
            return True

        return False

    def _resolve_conflict(self, conflict: SyncConflict) -> Optional[SyncChange]:
        """Resolve conflict based on strategy"""
        if self.conflict_strategy == ConflictResolution.LATEST_WINS:
            # Use change with latest timestamp
            if conflict.remote_change.timestamp > conflict.local_change.timestamp:
                winner = conflict.remote_change
            else:
                winner = conflict.local_change

            conflict.resolved = True
            conflict.resolution = winner
            return winner

        elif self.conflict_strategy == ConflictResolution.DEVICE_PRIORITY:
            # Prioritize changes from this device
            winner = conflict.local_change
            conflict.resolved = True
            conflict.resolution = winner
            return winner

        elif self.conflict_strategy == ConflictResolution.MERGE:
            # Attempt to merge changes
            merged = self._merge_changes(conflict.local_change, conflict.remote_change)
            if merged:
                conflict.resolved = True
                conflict.resolution = merged
                return merged

        # MANUAL or failed merge
        return None

    def _merge_changes(
        self, change1: SyncChange, change2: SyncChange
    ) -> Optional[SyncChange]:
        """Attempt to merge two changes"""
        # Simple field-level merge
        merged_data = change1.data.copy()

        for key, value in change2.data.items():
            # If field doesn't exist in local, add it
            if key not in merged_data:
                merged_data[key] = value
            # If values differ, use latest
            elif change2.timestamp > change1.timestamp:
                merged_data[key] = value

        # Create merged change
        merged = SyncChange(
            change_id=f"merged_{change1.change_id}_{change2.change_id}",
            change_type=ChangeType.UPDATE,
            entity_type=change1.entity_type,
            entity_id=change1.entity_id,
            data=merged_data,
            timestamp=max(change1.timestamp, change2.timestamp),
            device_id=self.device_id,
            version=max(change1.version, change2.version),
        )

        return merged

    def _apply_change(self, change: SyncChange):
        """Apply a change to local state"""
        # Update version
        self.entity_versions[change.entity_id] = change.version

        # Log application
        self.logger.debug(
            f"Applied {change.change_type.value} for {change.entity_type}:{change.entity_id}"
        )

        # Actual application would be handled by entity-specific handlers
        # This is just the sync engine coordination

    def get_conflicts(self) -> List[SyncConflict]:
        """Get unresolved conflicts"""
        return [c for c in self.conflicts if not c.resolved]

    def resolve_conflict_manually(
        self, entity_id: str, resolution_change: SyncChange
    ) -> bool:
        """Manually resolve a conflict"""
        for conflict in self.conflicts:
            if conflict.entity_id == entity_id and not conflict.resolved:
                conflict.resolved = True
                conflict.resolution = resolution_change
                self._apply_change(resolution_change)
                self.logger.info(f"Manually resolved conflict for {entity_id}")
                return True

        return False

    def clear_pending_changes(self):
        """Clear all pending changes"""
        self.pending_changes.clear()
        self.logger.debug("Cleared pending changes")

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        return {
            "status": self.status.value,
            "device_id": self.device_id,
            "pending_changes": len(self.pending_changes),
            "unresolved_conflicts": len(self.get_conflicts()),
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "entities_tracked": len(self.entity_versions),
        }


# Global instance
_sync_engine: Optional[SyncEngine] = None


def get_sync_engine(device_id: str = "default_device") -> SyncEngine:
    """Get global sync engine"""
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = SyncEngine(device_id)
    return _sync_engine
