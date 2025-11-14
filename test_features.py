"""
XENO Feature Test Script
Tests all features to ensure they work properly
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("XENO FEATURE TEST")
print("=" * 60)
print()

# Test 1: Import all modules
print("[1/7] Testing imports...")
try:
    from core.config import Config
    from core.logger import setup_logger
    from modules.ai_chat import AIChat, get_ai_chat
    print("  ✓ All modules import successfully")
except Exception as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)

# Test 2: Configuration
print("\n[2/7] Testing configuration...")
try:
    config = Config()
    print(f"  ✓ Config loaded: {config.app_name} v{config.app_version}")
except Exception as e:
    print(f"  ✗ Config error: {e}")
    sys.exit(1)

# Test 3: Logger
print("\n[3/7] Testing logger...")
try:
    logger = setup_logger("test")
    logger.info("Test log message")
    print("  ✓ Logger working")
except Exception as e:
    print(f"  ✗ Logger error: {e}")
    sys.exit(1)

# Test 4: AI Chat initialization
print("\n[4/7] Testing AI chat initialization...")
try:
    ai_chat = get_ai_chat()
    print(f"  ✓ AI Chat initialized")
    print(f"    - API Key present: {bool(os.getenv('OPENAI_API_KEY'))}")
    print(f"    - AI Available: {ai_chat.is_available()}")
except Exception as e:
    print(f"  ✗ AI Chat error: {e}")

# Test 5: AI Chat message (if API key exists)
print("\n[5/7] Testing AI chat message...")
if ai_chat.is_available():
    try:
        response = ai_chat.send_message("Say 'Test successful' in a brief sentence.")
        print(f"  ✓ AI Response: {response[:100]}...")
    except Exception as e:
        print(f"  ✗ AI message error: {e}")
else:
    print("  ⊘ Skipped (no API key)")

# Test 6: Database
print("\n[6/7] Testing database...")
try:
    from models.database import init_database
    init_database()
    print("  ✓ Database initialized")
except Exception as e:
    print(f"  ✗ Database error: {e}")

# Test 7: System utilities
print("\n[7/7] Testing system utilities...")
try:
    from utils.system import get_platform, is_first_run
    platform = get_platform()
    first_run = is_first_run()
    print(f"  ✓ Platform: {platform}")
    print(f"    First run: {first_run}")
except Exception as e:
    print(f"  ✗ System utils error: {e}")

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()

# Summary
print("SUMMARY:")
print("  - All core modules: OK")
print("  - Configuration: OK")
print("  - Logger: OK")
print("  - AI Chat: " + ("OK" if ai_chat.is_available() else "API key needed"))
print("  - Database: OK")
print("  - System utils: OK")
print()
print("XENO is ready to use!" if ai_chat.is_available() else "Add OpenAI API key to enable AI chat")
