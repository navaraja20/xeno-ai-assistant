"""
Cloud Storage Provider
Handles cloud storage operations for sync
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.logger import setup_logger
from src.sync.sync_engine import SyncChange


class CloudProvider(ABC):
    """Abstract cloud storage provider"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = setup_logger(f"sync.cloud.{provider_name}")
        self._connected = False

    @abstractmethod
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to cloud provider"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from cloud provider"""
        pass

    @abstractmethod
    def upload_changes(self, changes: List[SyncChange]) -> bool:
        """Upload changes to cloud"""
        pass

    @abstractmethod
    def download_changes(self, since: Optional[datetime] = None) -> List[SyncChange]:
        """Download changes from cloud"""
        pass

    @abstractmethod
    def get_latest_sync_time(self) -> Optional[datetime]:
        """Get timestamp of latest sync"""
        pass

    @property
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected


class LocalFileProvider(CloudProvider):
    """Local file system provider (for testing/offline)"""

    def __init__(self, storage_path: str = None):
        super().__init__("local_file")

        if storage_path is None:
            storage_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sync")

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.changes_file = self.storage_path / "changes.json"
        self.metadata_file = self.storage_path / "metadata.json"

    def connect(self, credentials: Dict[str, Any] = None) -> bool:
        """Connect to local storage"""
        self.logger.info(f"Connected to local storage: {self.storage_path}")
        self._connected = True
        return True

    def disconnect(self) -> bool:
        """Disconnect from local storage"""
        self.logger.info("Disconnected from local storage")
        self._connected = False
        return True

    def upload_changes(self, changes: List[SyncChange]) -> bool:
        """Upload changes to local file"""
        if not self._connected:
            self.logger.error("Not connected")
            return False

        try:
            # Load existing changes
            existing_changes = []
            if self.changes_file.exists():
                with open(self.changes_file, "r") as f:
                    data = json.load(f)
                    existing_changes = [SyncChange.from_dict(c) for c in data.get("changes", [])]

            # Add new changes
            all_changes = existing_changes + changes

            # Remove duplicates (by change_id)
            seen_ids = set()
            unique_changes = []
            for change in all_changes:
                if change.change_id not in seen_ids:
                    unique_changes.append(change)
                    seen_ids.add(change.change_id)

            # Save
            with open(self.changes_file, "w") as f:
                json.dump(
                    {
                        "changes": [c.to_dict() for c in unique_changes],
                        "updated_at": datetime.now().isoformat(),
                    },
                    f,
                    indent=2,
                )

            # Update metadata
            self._update_metadata()

            self.logger.info(f"Uploaded {len(changes)} changes")
            return True

        except Exception as e:
            self.logger.error(f"Failed to upload changes: {e}")
            return False

    def download_changes(self, since: Optional[datetime] = None) -> List[SyncChange]:
        """Download changes from local file"""
        if not self._connected:
            self.logger.error("Not connected")
            return []

        try:
            if not self.changes_file.exists():
                return []

            with open(self.changes_file, "r") as f:
                data = json.load(f)
                changes = [SyncChange.from_dict(c) for c in data.get("changes", [])]

            # Filter by timestamp if provided
            if since:
                changes = [c for c in changes if c.timestamp > since]

            self.logger.info(f"Downloaded {len(changes)} changes")
            return changes

        except Exception as e:
            self.logger.error(f"Failed to download changes: {e}")
            return []

    def get_latest_sync_time(self) -> Optional[datetime]:
        """Get latest sync timestamp"""
        if not self.metadata_file.exists():
            return None

        try:
            with open(self.metadata_file, "r") as f:
                metadata = json.load(f)
                last_sync = metadata.get("last_sync")
                return datetime.fromisoformat(last_sync) if last_sync else None
        except Exception as e:
            self.logger.error(f"Failed to get sync time: {e}")
            return None

    def _update_metadata(self):
        """Update metadata file"""
        metadata = {
            "last_sync": datetime.now().isoformat(),
            "provider": self.provider_name,
        }

        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)


class EncryptedCloudProvider(CloudProvider):
    """Encrypted cloud storage provider"""

    def __init__(self, base_provider: CloudProvider, encryption_key: str):
        super().__init__(f"encrypted_{base_provider.provider_name}")
        self.base_provider = base_provider
        self.encryption_key = encryption_key

    def connect(self, credentials: Dict[str, Any] = None) -> bool:
        """Connect to encrypted storage"""
        result = self.base_provider.connect(credentials)
        self._connected = result
        return result

    def disconnect(self) -> bool:
        """Disconnect from encrypted storage"""
        result = self.base_provider.disconnect()
        self._connected = False
        return result

    def upload_changes(self, changes: List[SyncChange]) -> bool:
        """Upload encrypted changes"""
        # Encrypt changes
        encrypted_changes = [self._encrypt_change(c) for c in changes]
        return self.base_provider.upload_changes(encrypted_changes)

    def download_changes(self, since: Optional[datetime] = None) -> List[SyncChange]:
        """Download and decrypt changes"""
        encrypted_changes = self.base_provider.download_changes(since)
        return [self._decrypt_change(c) for c in encrypted_changes]

    def get_latest_sync_time(self) -> Optional[datetime]:
        """Get latest sync time"""
        return self.base_provider.get_latest_sync_time()

    def _encrypt_change(self, change: SyncChange) -> SyncChange:
        """Encrypt change data"""
        # Simple XOR encryption for demo (use proper encryption in production)
        encrypted_data = {}
        for key, value in change.data.items():
            if isinstance(value, str):
                encrypted_data[key] = self._xor_encrypt(value)
            else:
                encrypted_data[key] = value

        # Create new change with encrypted data
        encrypted = SyncChange(
            change_id=change.change_id,
            change_type=change.change_type,
            entity_type=change.entity_type,
            entity_id=change.entity_id,
            data=encrypted_data,
            timestamp=change.timestamp,
            device_id=change.device_id,
            version=change.version,
        )

        return encrypted

    def _decrypt_change(self, change: SyncChange) -> SyncChange:
        """Decrypt change data"""
        decrypted_data = {}
        for key, value in change.data.items():
            if isinstance(value, str):
                decrypted_data[key] = self._xor_decrypt(value)
            else:
                decrypted_data[key] = value

        # Create new change with decrypted data
        decrypted = SyncChange(
            change_id=change.change_id,
            change_type=change.change_type,
            entity_type=change.entity_type,
            entity_id=change.entity_id,
            data=decrypted_data,
            timestamp=change.timestamp,
            device_id=change.device_id,
            version=change.version,
        )

        return decrypted

    def _xor_encrypt(self, text: str) -> str:
        """Simple XOR encryption"""
        key = self.encryption_key.encode()
        encrypted = []

        for i, char in enumerate(text):
            encrypted.append(chr(ord(char) ^ key[i % len(key)]))

        return "".join(encrypted).encode("utf-8").hex()

    def _xor_decrypt(self, encrypted_hex: str) -> str:
        """Simple XOR decryption"""
        try:
            encrypted = bytes.fromhex(encrypted_hex).decode("utf-8")
            key = self.encryption_key.encode()
            decrypted = []

            for i, char in enumerate(encrypted):
                decrypted.append(chr(ord(char) ^ key[i % len(key)]))

            return "".join(decrypted)
        except:
            # Return as-is if decryption fails
            return encrypted_hex


class CloudStorageManager:
    """Manages cloud storage providers"""

    def __init__(self):
        self.logger = setup_logger("sync.cloud_manager")
        self.providers: Dict[str, CloudProvider] = {}
        self.active_provider: Optional[CloudProvider] = None

    def register_provider(self, name: str, provider: CloudProvider):
        """Register a cloud provider"""
        self.providers[name] = provider
        self.logger.info(f"Registered provider: {name}")

    def set_active_provider(self, name: str) -> bool:
        """Set active cloud provider"""
        if name not in self.providers:
            self.logger.error(f"Provider not found: {name}")
            return False

        self.active_provider = self.providers[name]
        self.logger.info(f"Active provider set to: {name}")
        return True

    def get_provider(self, name: str) -> Optional[CloudProvider]:
        """Get provider by name"""
        return self.providers.get(name)

    def list_providers(self) -> List[str]:
        """List available providers"""
        return list(self.providers.keys())

    def upload_to_cloud(self, changes: List[SyncChange]) -> bool:
        """Upload changes to active provider"""
        if not self.active_provider:
            self.logger.error("No active provider")
            return False

        return self.active_provider.upload_changes(changes)

    def download_from_cloud(self, since: Optional[datetime] = None) -> List[SyncChange]:
        """Download changes from active provider"""
        if not self.active_provider:
            self.logger.error("No active provider")
            return []

        return self.active_provider.download_changes(since)

    def get_sync_time(self) -> Optional[datetime]:
        """Get latest sync time from active provider"""
        if not self.active_provider:
            return None

        return self.active_provider.get_latest_sync_time()


# Global instance
_cloud_manager: Optional[CloudStorageManager] = None


def get_cloud_manager() -> CloudStorageManager:
    """Get global cloud storage manager"""
    global _cloud_manager
    if _cloud_manager is None:
        _cloud_manager = CloudStorageManager()

        # Register default local provider
        local_provider = LocalFileProvider()
        _cloud_manager.register_provider("local", local_provider)
        _cloud_manager.set_active_provider("local")

    return _cloud_manager
