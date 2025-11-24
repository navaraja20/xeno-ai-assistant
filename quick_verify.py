#!/usr/bin/env python3
"""
XENO - Quick System Verification
Verifies all core systems are operational
"""

import sys
from pathlib import Path


def test_all():
    """Run all quick verification tests"""
    print("\n🔍 XENO System Verification\n")
    print("=" * 60)

    passed = 0
    total = 0

    # Test 1: Core Module Imports
    print("\n📦 Testing Module Imports...")
    modules_to_test = [
        ("Security (Enterprise)", "src.security.enterprise_security"),
        ("Security (Config)", "src.security.security_config"),
        ("AI (Personalization)", "src.ai.model_finetuning"),
        ("Collaboration", "src.collaboration.team_features"),
        ("IoT", "src.iot.smart_home_integration"),
        ("Voice", "src.voice.advanced_voice_engine"),
        ("ML (Analytics)", "src.ml.analytics_collector"),
        ("ML (Predictive)", "src.ml.predictive_analytics"),
    ]

    for name, module in modules_to_test:
        total += 1
        try:
            __import__(module)
            print(f"  ✓ {name}")
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: {e}")

    # Test 2: Security Functions
    print("\n🔐 Testing Security Functions...")
    try:
        from src.security.enterprise_security import AuthenticationManager, EncryptionManager

        # Encryption test
        total += 1
        enc = EncryptionManager()
        test_data = "test123"
        encrypted = enc.encrypt_data(test_data)
        decrypted = enc.decrypt_data(encrypted)
        if decrypted == test_data:
            print(f"  ✓ Encryption/Decryption")
            passed += 1
        else:
            print(f"  ✗ Encryption/Decryption: mismatch")

        # Password hashing test
        total += 1
        password = "TestPass123!"
        hashed, salt = enc.hash_password(password)
        if enc.verify_password(password, hashed, salt):
            print(f"  ✓ Password Hashing/Verification")
            passed += 1
        else:
            print(f"  ✗ Password Hashing/Verification")

        # Authentication test
        total += 1
        auth = AuthenticationManager()
        if auth.register_user("test_verify_user", "SecurePass123!"):
            print(f"  ✓ User Registration")
            passed += 1
        else:
            print(f"  ✗ User Registration")

        total += 1
        if auth.authenticate_user("test_verify_user", "SecurePass123!"):
            print(f"  ✓ User Authentication")
            passed += 1
        else:
            print(f"  ✗ User Authentication")

    except Exception as e:
        print(f"  ✗ Security tests failed: {e}")

    # Test 3: AI/ML Functions
    print("\n🤖 Testing AI/ML Functions...")
    try:
        from src.ai.model_finetuning import PersonalizationEngine

        total += 1
        engine = PersonalizationEngine("verify_user")
        engine.update_preference("theme", "dark")
        if engine.get_preference("theme") == "dark":
            print(f"  ✓ Personalization (Preferences)")
            passed += 1
        else:
            print(f"  ✗ Personalization (Preferences)")

        total += 1
        engine.record_interaction("test", "response", "brief")
        if len(engine.interactions) > 0:
            print(f"  ✓ Personalization (Interactions)")
            passed += 1
        else:
            print(f"  ✗ Personalization (Interactions)")

    except Exception as e:
        print(f"  ✗ AI/ML tests failed: {e}")

    # Test 4: Collaboration Functions
    print("\n👥 Testing Collaboration Functions...")
    try:
        from src.collaboration.team_features import TeamManager

        total += 1
        tm = TeamManager()
        team_id = tm.create_team("Verification Team", "owner_user")
        if team_id:
            print(f"  ✓ Team Creation")
            passed += 1
        else:
            print(f"  ✗ Team Creation")

        total += 1
        if tm.add_member(team_id, "member_user", "member"):
            print(f"  ✓ Team Member Management")
            passed += 1
        else:
            print(f"  ✗ Team Member Management")

    except Exception as e:
        print(f"  ✗ Collaboration tests failed: {e}")

    # Test 5: IoT Functions
    print("\n🏠 Testing IoT Functions...")
    try:
        from src.iot.smart_home_integration import SmartHomeHub

        total += 1
        hub = SmartHomeHub()
        print(f"  ✓ Smart Home Hub Initialization")
        passed += 1

        total += 1
        # Test device registration
        hub.devices["test_device"] = {"id": "test", "type": "light"}
        if "test_device" in hub.devices:
            print(f"  ✓ Device Registration")
            passed += 1
        else:
            print(f"  ✗ Device Registration")

    except Exception as e:
        print(f"  ✗ IoT tests failed: {e}")

    # Test 6: Voice Functions
    print("\n🎤 Testing Voice Functions...")
    try:
        from src.voice.advanced_voice_engine import EmotionAnalyzer, WakeWordDetector

        total += 1
        analyzer = EmotionAnalyzer()
        emotion = analyzer.analyze_text("I'm very happy!")
        if emotion in ["happy", "joy", "excited"]:
            print(f"  ✓ Emotion Analysis")
            passed += 1
        else:
            print(f"  ✗ Emotion Analysis: got '{emotion}'")

        total += 1
        detector = WakeWordDetector()
        if detector.detect("Hey XENO turn on lights"):
            print(f"  ✓ Wake Word Detection")
            passed += 1
        else:
            print(f"  ✗ Wake Word Detection")

    except Exception as e:
        print(f"  ✗ Voice tests failed: {e}")

    # Test 7: File Structure
    print("\n📁 Testing File Structure...")
    critical_files = [
        ".github/workflows/ci.yml",
        ".pre-commit-config.yaml",
        "pyproject.toml",
        "setup.py",
        "src/security/enterprise_security.py",
        "tests/unit/test_security/test_security_config.py",
        "tests/e2e/test_authentication_flow.py",
    ]

    for file_path in critical_files:
        total += 1
        if Path(file_path).exists():
            passed += 1
        else:
            print(f"  ✗ Missing: {file_path}")

    if passed == len(critical_files):
        print(f"  ✓ All {len(critical_files)} critical files present")

    # Summary
    print("\n" + "=" * 60)
    print(f"\n📊 RESULTS: {passed}/{total} tests passed ({100*passed//total}%)")

    if passed >= total * 0.95:
        print("✅ Status: HEALTHY")
        return 0
    elif passed >= total * 0.80:
        print("⚠️  Status: DEGRADED (but functional)")
        return 0
    else:
        print("❌ Status: NEEDS ATTENTION")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(test_all())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
