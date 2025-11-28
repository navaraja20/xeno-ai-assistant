"""
Multi-Device Sync - Comprehensive Demo
Demonstrates sync engine, cloud storage, offline support, and conflict resolution
"""

from datetime import datetime, timedelta
import time

from src.sync import (
    get_sync_coordinator,
    get_sync_engine,
    get_cloud_manager,
    get_offline_manager,
    ChangeType,
    ConflictResolution,
    LocalFileProvider,
    EncryptedCloudProvider,
)


def demo_basic_sync():
    """Demo 1: Basic Synchronization"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Synchronization")
    print("=" * 60)

    # Create two devices
    device1 = get_sync_coordinator("device_desktop")
    device2 = get_sync_coordinator("device_mobile")

    print(f"\n📱 Simulating two devices:")
    print(f"  • Device 1: {device1.device_id}")
    print(f"  • Device 2: {device2.device_id}")

    # Device 1: Create a task
    print(f"\n1️⃣  Device 1 creates a task...")
    task_data = {
        "title": "Complete project report",
        "priority": "high",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    change1 = device1.track_change(
        ChangeType.CREATE, "task", "task_001", task_data
    )
    print(f"   ✅ Task created: {task_data['title']}")

    # Device 1: Sync to cloud
    print(f"\n2️⃣  Device 1 syncs to cloud...")
    results1 = device1.sync_now()
    print(f"   ✅ Uploaded: {results1['uploaded']} changes")

    # Device 2: Sync from cloud
    print(f"\n3️⃣  Device 2 syncs from cloud...")
    results2 = device2.sync_now()
    print(f"   ✅ Downloaded: {results2['downloaded']} changes")
    print(f"   ℹ️  Task is now available on Device 2")

    # Device 2: Update task
    print(f"\n4️⃣  Device 2 updates task...")
    updated_data = task_data.copy()
    updated_data["status"] = "in_progress"
    updated_data["updated_at"] = datetime.now().isoformat()

    change2 = device2.track_change(
        ChangeType.UPDATE, "task", "task_001", updated_data
    )
    print(f"   ✅ Task status: pending → in_progress")

    # Device 2: Sync to cloud
    print(f"\n5️⃣  Device 2 syncs to cloud...")
    results2 = device2.sync_now()
    print(f"   ✅ Uploaded: {results2['uploaded']} changes")

    # Device 1: Sync from cloud
    print(f"\n6️⃣  Device 1 syncs from cloud...")
    results1 = device1.sync_now()
    print(f"   ✅ Downloaded: {results1['downloaded']} changes")
    print(f"   ℹ️  Task update is now on Device 1")


def demo_conflict_resolution():
    """Demo 2: Conflict Resolution"""
    print("\n" + "=" * 60)
    print("DEMO 2: Conflict Resolution")
    print("=" * 60)

    # Create two devices
    device1 = get_sync_engine("conflict_device_1")
    device2 = get_sync_engine("conflict_device_2")

    # Set conflict strategy
    device1.conflict_strategy = ConflictResolution.LATEST_WINS
    device2.conflict_strategy = ConflictResolution.LATEST_WINS

    print(f"\n⚙️  Conflict strategy: LATEST_WINS")

    # Both devices have same task
    task_data = {
        "title": "Write documentation",
        "priority": "medium",
        "status": "pending",
    }

    # Device 1 update
    print(f"\n1️⃣  Device 1 updates task...")
    time.sleep(0.1)  # Small delay
    device1_data = task_data.copy()
    device1_data["priority"] = "high"
    device1_data["notes"] = "Added by device 1"

    change1 = device1.track_change(
        ChangeType.UPDATE, "task", "task_conflict", device1_data
    )
    print(f"   Priority: medium → high")
    print(f"   Timestamp: {change1.timestamp}")

    # Device 2 update (slightly later)
    print(f"\n2️⃣  Device 2 updates task...")
    time.sleep(0.1)
    device2_data = task_data.copy()
    device2_data["priority"] = "low"
    device2_data["notes"] = "Added by device 2"

    change2 = device2.track_change(
        ChangeType.UPDATE, "task", "task_conflict", device2_data
    )
    print(f"   Priority: medium → low")
    print(f"   Timestamp: {change2.timestamp}")

    # Apply device 1's changes to device 2
    print(f"\n3️⃣  Applying Device 1's changes to Device 2...")
    results = device2.apply_remote_changes([change1])

    if results["conflicts"]:
        print(f"   ⚠️  Conflict detected!")
        conflict = results["conflicts"][0]
        print(f"   Local: priority={device2_data['priority']}")
        print(f"   Remote: priority={device1_data['priority']}")
        print(f"   Resolution: Latest wins → {change2.data['priority']} (Device 2 is newer)")
    else:
        print(f"   ✅ Applied {len(results['applied'])} changes")


def demo_offline_support():
    """Demo 3: Offline Support"""
    print("\n" + "=" * 60)
    print("DEMO 3: Offline Support & Queue")
    print("=" * 60)

    coordinator = get_sync_coordinator("offline_device")
    offline_mgr = get_offline_manager()

    # Start online
    print(f"\n📶 Device is online")
    offline_mgr.set_online(True)

    # Create some tasks
    print(f"\n1️⃣  Creating tasks while online...")
    for i in range(3):
        task_data = {
            "title": f"Online task {i+1}",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        coordinator.track_change(ChangeType.CREATE, "task", f"online_task_{i}", task_data)

    print(f"   ✅ Created 3 tasks")

    # Go offline
    print(f"\n2️⃣  Device goes offline...")
    offline_mgr.set_online(False)
    print(f"   📵 Now offline")

    # Create tasks while offline
    print(f"\n3️⃣  Creating tasks while offline...")
    for i in range(5):
        task_data = {
            "title": f"Offline task {i+1}",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        coordinator.track_change(ChangeType.CREATE, "task", f"offline_task_{i}", task_data)

    queued = offline_mgr.queue.size()
    print(f"   ✅ Created 5 tasks (queued: {queued})")

    # Check queue
    print(f"\n4️⃣  Offline queue status:")
    print(f"   Queue size: {offline_mgr.queue.size()}")
    print(f"   Auto-sync: {offline_mgr.auto_sync_enabled}")

    # Come back online
    print(f"\n5️⃣  Device comes back online...")
    offline_mgr.set_online(True)
    print(f"   📶 Now online")

    # Sync
    print(f"\n6️⃣  Syncing queued changes...")
    results = coordinator.sync_now()
    print(f"   ✅ Uploaded: {results['uploaded']} changes")
    print(f"   Queue remaining: {offline_mgr.queue.size()}")


def demo_encrypted_sync():
    """Demo 4: Encrypted Sync"""
    print("\n" + "=" * 60)
    print("DEMO 4: Encrypted Cloud Sync")
    print("=" * 60)

    cloud_mgr = get_cloud_manager()

    # Create encrypted provider
    print(f"\n🔒 Setting up encrypted storage...")
    base_provider = LocalFileProvider()
    encrypted_provider = EncryptedCloudProvider(
        base_provider, encryption_key="my_secret_key_12345"
    )

    # Register and activate
    cloud_mgr.register_provider("encrypted", encrypted_provider)
    cloud_mgr.set_active_provider("encrypted")

    # Connect
    encrypted_provider.connect()
    print(f"   ✅ Encrypted provider active")

    # Create coordinator with encryption
    coordinator = get_sync_coordinator("encrypted_device")

    # Create sensitive data
    print(f"\n1️⃣  Creating sensitive task...")
    sensitive_data = {
        "title": "Confidential meeting notes",
        "content": "Secret project information",
        "priority": "high",
    }

    coordinator.track_change(
        ChangeType.CREATE, "task", "sensitive_001", sensitive_data
    )

    # Sync (will be encrypted)
    print(f"\n2️⃣  Syncing with encryption...")
    results = coordinator.sync_now()
    print(f"   ✅ Uploaded: {results['uploaded']} encrypted changes")
    print(f"   🔒 Data is encrypted in cloud storage")

    # Simulate another device downloading
    print(f"\n3️⃣  Another device downloads encrypted data...")
    device2 = get_sync_coordinator("encrypted_device_2")
    results2 = device2.sync_now()
    print(f"   ✅ Downloaded: {results2['downloaded']} changes")
    print(f"   🔓 Data decrypted on device")


def demo_multi_device_workflow():
    """Demo 5: Complete Multi-Device Workflow"""
    print("\n" + "=" * 60)
    print("DEMO 5: Complete Multi-Device Workflow")
    print("=" * 60)

    print(f"\n📱 Scenario: Working across 3 devices\n")

    # Desktop device
    desktop = get_sync_coordinator("device_desktop")
    print(f"1️⃣  Desktop: Create project tasks")

    tasks = [
        {"title": "Design mockups", "priority": "high", "assigned": "designer"},
        {"title": "Implement backend", "priority": "high", "assigned": "developer"},
        {"title": "Write tests", "priority": "medium", "assigned": "qa"},
    ]

    for i, task in enumerate(tasks):
        desktop.track_change(ChangeType.CREATE, "task", f"project_task_{i}", task)

    print(f"   ✅ Created {len(tasks)} tasks")

    # Sync from desktop
    print(f"\n2️⃣  Desktop: Sync to cloud")
    results = desktop.sync_now()
    print(f"   ✅ Uploaded {results['uploaded']} tasks")

    # Mobile device
    print(f"\n3️⃣  Mobile: Sync from cloud")
    mobile = get_sync_coordinator("device_mobile")
    results = mobile.sync_now()
    print(f"   ✅ Downloaded {results['downloaded']} tasks")

    # Mobile updates a task
    print(f"\n4️⃣  Mobile: Update task status")
    updated_task = tasks[0].copy()
    updated_task["status"] = "in_progress"
    mobile.track_change(ChangeType.UPDATE, "task", "project_task_0", updated_task)
    print(f"   ✅ Updated: Design mockups → in_progress")

    # Mobile syncs
    print(f"\n5️⃣  Mobile: Sync to cloud")
    results = mobile.sync_now()
    print(f"   ✅ Uploaded {results['uploaded']} updates")

    # Laptop device
    print(f"\n6️⃣  Laptop: Sync from cloud")
    laptop = get_sync_coordinator("device_laptop")
    results = laptop.sync_now()
    print(f"   ✅ Downloaded {results['downloaded']} changes")
    print(f"   ℹ️  All devices now in sync!")

    # Show status
    print(f"\n📊 Sync Status:")
    status = laptop.get_status()
    print(f"   Device ID: {status['device_id']}")
    print(f"   Pending changes: {status['sync_engine']['pending_changes']}")
    print(f"   Conflicts: {status['unresolved_conflicts']}")


def demo_sync_statistics():
    """Demo 6: Sync Statistics & Monitoring"""
    print("\n" + "=" * 60)
    print("DEMO 6: Sync Statistics & Monitoring")
    print("=" * 60)

    coordinator = get_sync_coordinator("stats_device")

    # Register sync callback
    def on_sync_complete(results):
        print(f"\n   📊 Sync completed!")
        print(f"      Uploaded: {results['uploaded']}")
        print(f"      Downloaded: {results['downloaded']}")
        print(f"      Conflicts: {results['conflicts']}")
        if results['errors']:
            print(f"      Errors: {len(results['errors'])}")

    coordinator.on_sync_complete(on_sync_complete)

    # Create changes
    print(f"\n1️⃣  Creating test data...")
    for i in range(10):
        data = {"title": f"Task {i}", "index": i}
        coordinator.track_change(ChangeType.CREATE, "task", f"stat_task_{i}", data)

    # Sync
    print(f"\n2️⃣  Triggering sync...")
    results = coordinator.sync_now()

    # Show detailed status
    print(f"\n3️⃣  Detailed Status:")
    status = coordinator.get_status()

    print(f"\n   Sync Engine:")
    print(f"      Status: {status['sync_engine']['status']}")
    print(f"      Pending: {status['sync_engine']['pending_changes']}")
    print(f"      Entities: {status['sync_engine']['entities_tracked']}")
    print(f"      Last sync: {status['sync_engine']['last_sync']}")

    print(f"\n   Offline Manager:")
    print(f"      Online: {status['offline']['is_online']}")
    print(f"      Queue: {status['offline']['queue_size']}")
    print(f"      Auto-sync: {status['offline']['auto_sync_enabled']}")

    print(f"\n   Cloud Provider: {status['cloud_provider']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🔄 MULTI-DEVICE SYNC - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("\nDemonstrating:")
    print("  • Basic Synchronization")
    print("  • Conflict Resolution")
    print("  • Offline Support & Queue")
    print("  • Encrypted Cloud Sync")
    print("  • Multi-Device Workflow")
    print("  • Sync Statistics")

    # Run demos
    demo_basic_sync()
    demo_conflict_resolution()
    demo_offline_support()
    demo_encrypted_sync()
    demo_multi_device_workflow()
    demo_sync_statistics()

    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
