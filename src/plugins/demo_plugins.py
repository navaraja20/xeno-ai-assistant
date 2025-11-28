"""
Plugin System - Comprehensive Demo
Demonstrates plugin development, installation, and management
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.plugins import PluginType, get_plugin_manager, get_plugin_sdk


def generate_sample_tasks():
    """Generate sample task data"""
    base_date = datetime.now() - timedelta(days=30)
    tasks = []

    for i in range(50):
        created = base_date + timedelta(days=i * 0.6)
        completed = created + timedelta(hours=18) if i % 3 != 0 else None

        tasks.append(
            {
                "id": f"task_{i}",
                "title": f"Task {i}",
                "status": "completed" if completed else "pending",
                "priority": ["high", "medium", "low"][i % 3],
                "tags": [["work", "urgent"], ["personal"], ["review", "low-priority"]][i % 3],
                "created_at": created.isoformat(),
                "completed_at": completed.isoformat() if completed else None,
            }
        )

    return tasks


def demo_plugin_sdk():
    """Demo 1: Plugin SDK - Create Plugin Template"""
    print("\n" + "=" * 60)
    print("DEMO 1: Plugin SDK - Create Plugin Template")
    print("=" * 60)

    sdk = get_plugin_sdk()

    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n📦 Creating plugin template...")

        # Create automation plugin template
        success = sdk.create_plugin_template(
            plugin_id="my_automation",
            name="My Automation Plugin",
            plugin_type=PluginType.AUTOMATION,
            output_dir=temp_dir,
            author="Demo Developer",
            description="An automation plugin example",
        )

        if success:
            plugin_dir = Path(temp_dir) / "my_automation"
            print(f"✅ Plugin template created at: {plugin_dir}")

            # Show generated files
            print(f"\n📁 Generated files:")
            for file in plugin_dir.rglob("*"):
                if file.is_file():
                    rel_path = file.relative_to(plugin_dir)
                    print(f"  • {rel_path}")

            # Validate plugin
            print(f"\n🔍 Validating plugin...")
            validation = sdk.validate_plugin(str(plugin_dir))

            if validation["valid"]:
                print("✅ Plugin is valid")
            else:
                print("❌ Plugin has errors:")
                for error in validation["errors"]:
                    print(f"  • {error}")

            if validation["warnings"]:
                print("⚠️  Warnings:")
                for warning in validation["warnings"]:
                    print(f"  • {warning}")


def demo_plugin_manager():
    """Demo 2: Plugin Manager - Discovery and Loading"""
    print("\n" + "=" * 60)
    print("DEMO 2: Plugin Manager - Discovery and Loading")
    print("=" * 60)

    manager = get_plugin_manager()

    print(f"\n🔍 Discovering plugins...")
    discovered = manager.discover_plugins()
    print(f"✅ Discovered {len(discovered)} plugins")

    # List all plugins
    print(f"\n📋 Available Plugins:")
    all_plugins = manager.list_plugins()
    for manifest in all_plugins:
        print(f"  • {manifest.name} (v{manifest.version})")
        print(f"    ID: {manifest.id}")
        print(f"    Type: {manifest.plugin_type.value}")
        print(f"    Status: {manifest.status.value}")


def demo_sample_plugins():
    """Demo 3: Sample Plugins - Task Stats"""
    print("\n" + "=" * 60)
    print("DEMO 3: Sample Plugins - Task Stats Analytics")
    print("=" * 60)

    manager = get_plugin_manager()

    # Check if task_stats plugin exists
    plugin_id = "task_stats"

    # Try to activate
    print(f"\n🔌 Activating {plugin_id} plugin...")
    success = manager.activate_plugin(plugin_id)

    if success:
        print(f"✅ Plugin activated")

        # Get plugin instance
        plugin = manager.get_plugin(plugin_id)

        # Generate sample tasks
        tasks = generate_sample_tasks()
        print(f"\n📊 Analyzing {len(tasks)} tasks...")

        # Analyze tasks
        results = plugin.analyze(tasks)

        print(f"\n📈 Analysis Results:")
        print(f"  Total Tasks: {results['total_tasks']}")
        print(f"  Completed: {results['completed_tasks']}")
        print(f"  Completion Rate: {results['completion_rate']:.1%}")
        print(f"  Avg Completion Time: {results['average_completion_hours']:.1f} hours")
        print(f"  Most Productive Day: {results['most_productive_day']}")

        print(f"\n📊 Priority Distribution:")
        for priority, count in results["priority_distribution"].items():
            print(f"  • {priority}: {count}")

        print(f"\n💡 Insights:")
        for insight in results["insights"]:
            print(f"  • {insight}")

        # Deactivate
        manager.deactivate_plugin(plugin_id)
        print(f"\n✅ Plugin deactivated")
    else:
        print(f"⚠️  Plugin not available (this is a demo)")


def demo_github_integration():
    """Demo 4: Sample Plugins - GitHub Integration"""
    print("\n" + "=" * 60)
    print("DEMO 4: Sample Plugins - GitHub Integration")
    print("=" * 60)

    manager = get_plugin_manager()
    plugin_id = "github_integration"

    print(f"\n🔌 Activating {plugin_id} plugin...")

    # Mock configuration
    config = {
        "api_key": "demo_token_12345",
        "repository": "demo/repo",
        "auto_sync": True,
        "sync_interval": 300,
    }

    # Try to activate (will work if plugin is installed)
    success = manager.activate_plugin(plugin_id)

    if success:
        print(f"✅ Plugin activated")

        plugin = manager.get_plugin(plugin_id)

        # Get issues
        print(f"\n📋 Fetching GitHub issues...")
        issues = plugin.get_issues()

        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  • #{issue['id']}: {issue['title']}")
            print(f"    State: {issue['state']}, Labels: {', '.join(issue['labels'])}")

        # Create issue (demo)
        print(f"\n➕ Creating new issue...")
        issue_id = plugin.create_issue(
            title="Implement new feature",
            body="Feature requested by user",
            labels=["enhancement", "priority:high"],
        )
        print(f"✅ Created issue: {issue_id}")

        # Sync
        print(f"\n🔄 Syncing with GitHub...")
        sync_success = plugin.sync()
        if sync_success:
            print("✅ Sync completed")

        manager.deactivate_plugin(plugin_id)
        print(f"\n✅ Plugin deactivated")
    else:
        print(f"⚠️  Plugin not available (this is a demo)")


def demo_plugin_lifecycle():
    """Demo 5: Plugin Lifecycle Management"""
    print("\n" + "=" * 60)
    print("DEMO 5: Plugin Lifecycle Management")
    print("=" * 60)

    manager = get_plugin_manager()

    print(f"\n📋 Plugin Lifecycle Operations:\n")

    # List all plugins
    all_plugins = manager.list_plugins()
    print(f"1. Total Plugins: {len(all_plugins)}")

    # Filter by status
    from src.plugins.plugin_base import PluginStatus

    active = manager.list_plugins(status_filter=PluginStatus.ACTIVE)
    inactive = manager.list_plugins(status_filter=PluginStatus.INACTIVE)

    print(f"2. Active Plugins: {len(active)}")
    for plugin in active:
        print(f"   • {plugin.name}")

    print(f"3. Inactive Plugins: {len(inactive)}")
    for plugin in inactive:
        print(f"   • {plugin.name}")

    # Get plugin info
    if all_plugins:
        plugin = all_plugins[0]
        print(f"\n4. Plugin Details: {plugin.name}")
        info = manager.get_plugin_info(plugin.id)
        print(f"   ID: {info['id']}")
        print(f"   Version: {info['version']}")
        print(f"   Author: {info['author']}")
        print(f"   Type: {info['plugin_type']}")
        print(f"   Permissions: {', '.join(info['permissions'])}")


def demo_custom_plugin_creation():
    """Demo 6: Create Custom Plugin with SDK"""
    print("\n" + "=" * 60)
    print("DEMO 6: Create Custom Plugin with SDK")
    print("=" * 60)

    sdk = get_plugin_sdk()

    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\n🎨 Creating custom plugins...\n")

        # Create different types of plugins
        plugin_types = [
            (PluginType.AUTOMATION, "Task Auto-Scheduler"),
            (PluginType.INTEGRATION, "Slack Integration"),
            (PluginType.ANALYTICS, "Productivity Tracker"),
            (PluginType.AI, "Smart Suggestions"),
            (PluginType.UI, "Custom Dashboard"),
            (PluginType.UTILITY, "Export Tool"),
        ]

        for i, (ptype, name) in enumerate(plugin_types, 1):
            plugin_id = name.lower().replace(" ", "_")

            success = sdk.create_plugin_template(
                plugin_id=plugin_id,
                name=name,
                plugin_type=ptype,
                output_dir=temp_dir,
                author="Custom Developer",
                description=f"A {ptype.value} plugin",
            )

            if success:
                print(f"{i}. ✅ Created {name} ({ptype.value})")

                # Validate
                plugin_dir = Path(temp_dir) / plugin_id
                validation = sdk.validate_plugin(str(plugin_dir))

                if validation["valid"]:
                    print(f"   ✓ Validation passed")
                else:
                    print(f"   ✗ Validation failed:")
                    for error in validation["errors"]:
                        print(f"     - {error}")


def demo_plugin_permissions():
    """Demo 7: Plugin Permissions and Sandbox"""
    print("\n" + "=" * 60)
    print("DEMO 7: Plugin Permissions and Sandbox")
    print("=" * 60)

    from src.plugins.plugin_manager import PluginSandbox

    sandbox = PluginSandbox("demo_plugin")

    print(f"\n🔒 Testing permission validation:\n")

    # Test valid permissions
    valid_perms = ["tasks.read", "tasks.write", "notifications.send"]
    result = sandbox.validate_permissions(valid_perms)
    print(f"1. Valid permissions: {valid_perms}")
    print(f"   Result: {'✅ Approved' if result else '❌ Denied'}")

    # Test invalid permissions
    invalid_perms = ["tasks.delete_all", "system.shutdown"]
    result = sandbox.validate_permissions(invalid_perms)
    print(f"\n2. Invalid permissions: {invalid_perms}")
    print(f"   Result: {'✅ Approved' if result else '❌ Denied'}")

    # Test module imports
    print(f"\n🔒 Testing module import validation:\n")

    allowed_modules = ["json", "datetime", "math"]
    for module in allowed_modules:
        result = sandbox.validate_imports(module)
        status = "✅ Allowed" if result else "❌ Blocked"
        print(f"  • {module}: {status}")

    blocked_modules = ["os", "subprocess", "socket"]
    print()
    for module in blocked_modules:
        result = sandbox.validate_imports(module)
        status = "✅ Allowed" if result else "❌ Blocked"
        print(f"  • {module}: {status}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🔌 PLUGIN SYSTEM - COMPREHENSIVE DEMO")
    print("=" * 60)
    print("\nDemonstrating:")
    print("  • Plugin SDK & Template Generation")
    print("  • Plugin Manager & Discovery")
    print("  • Sample Plugins (Analytics, Integration)")
    print("  • Plugin Lifecycle Management")
    print("  • Custom Plugin Creation")
    print("  • Permissions & Sandbox Security")

    # Run demos
    demo_plugin_sdk()
    demo_plugin_manager()
    demo_sample_plugins()
    demo_github_integration()
    demo_plugin_lifecycle()
    demo_custom_plugin_creation()
    demo_plugin_permissions()

    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
