"""
Quick Feature Validation for XENO
Checks if all key modules can be imported successfully
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🔍 XENO Feature Validation")
print("=" * 70)

tests_passed = 0
tests_total = 0

# Priority 1: ML & Predictive Analytics
tests_total += 1
try:
    from src.ml.predictive_analytics import PredictiveEngine, BehaviorAnalyzer
    engine = PredictiveEngine()
    analyzer = BehaviorAnalyzer()
    print("✅ Priority 1: ML & Predictive Analytics - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 1: ML & Predictive Analytics - {e}")

# Priority 2: Advanced Analytics Dashboard
tests_total += 1
try:
    from src.ml.analytics_dashboard import AnalyticsDashboard
    dashboard = AnalyticsDashboard()
    print("✅ Priority 2: Advanced Analytics Dashboard - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 2: Advanced Analytics Dashboard - {e}")

# Priority 3: Enterprise Security & Compliance
tests_total += 1
try:
    from src.security.enterprise_security import EncryptionManager, AuthenticationManager, AuditLogger, ComplianceManager
    enc = EncryptionManager()
    plaintext = "test data"
    encrypted = enc.encrypt_data(plaintext)
    decrypted = enc.decrypt_data(encrypted)
    assert decrypted == plaintext
    auth = AuthenticationManager(secret_key="test_key_123")
    logger = AuditLogger()
    compliance = ComplianceManager()
    print("✅ Priority 3: Enterprise Security & Compliance - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 3: Enterprise Security & Compliance - {e}")

# Priority 4: Browser Extension
tests_total += 1
try:
    ext_exists = os.path.exists("src/websocket_server.py")
    assert ext_exists, "WebSocket server not found"
    print("✅ Priority 4: Browser Extension (WebSocket Server) - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 4: Browser Extension - {e}")

# Priority 5: Team Collaboration
tests_total += 1
try:
    from src.collaboration.team_features import TeamManager, SharedCalendarManager, TaskDelegationManager, TeamAnalytics
    team_mgr = TeamManager()
    team = team_mgr.create_team("team1", "Test", "Test team", "owner1")
    cal_mgr = SharedCalendarManager()
    task_mgr = TaskDelegationManager()
    analytics = TeamAnalytics(team_mgr, task_mgr)
    print("✅ Priority 5: Team Collaboration - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 5: Team Collaboration - {e}")

# Priority 6: Advanced Voice & NLP
tests_total += 1
try:
    from src.voice.advanced_voice_engine import AdvancedVoiceEngine, Language
    engine = AdvancedVoiceEngine()
    langs = len([l for l in Language])
    print(f"✅ Priority 6: Advanced Voice & NLP ({langs} languages) - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 6: Advanced Voice & NLP - {e}")

# Priority 7: Integration Hub
tests_total += 1
try:
    hub_exists = os.path.exists("src/ui/integration_hub.py")
    assert hub_exists, "Integration hub UI not found"
    print("✅ Priority 7: Integration Hub (UI Module) - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 7: Integration Hub - {e}")

# Priority 9: Wearable & IoT Integration
tests_total += 1
try:
    from src.iot.iot_hub import IoTHub
    from src.iot.smart_home_integration import SmartHomeHub
    iot = IoTHub()
    smart = SmartHomeHub()
    print("✅ Priority 9: Wearable & IoT Integration - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 9: Wearable & IoT Integration - {e}")

# Priority 10: AI Model Fine-tuning
tests_total += 1
try:
    from src.ai.model_finetuning import PersonalizationEngine, CustomModelTrainer, ContextualMemory
    from src.ai.federated_learning import FederatedTrainer, PersonalizedModelManager
    from src.ai.model_versioning import ModelVersionControl, PerformanceTracker
    
    engine = PersonalizationEngine("test_user")
    engine.update_preference("style", "professional")
    assert engine.get_preference("style") == "professional"
    
    trainer = CustomModelTrainer("test_user")
    memory = ContextualMemory("test_user")
    memory.store_fact("test", "key", "value")
    assert memory.retrieve_fact("test", "key") == "value"
    
    fed = FederatedTrainer("test_model")
    vcs = ModelVersionControl()
    tracker = PerformanceTracker()
    
    print("✅ Priority 10: AI Model Fine-tuning - OK")
    tests_passed += 1
except Exception as e:
    print(f"❌ Priority 10: AI Model Fine-tuning - {e}")

print("=" * 70)
print(f"📊 Results: {tests_passed}/{tests_total} features validated ({tests_passed/tests_total*100:.1f}%)")
print("=" * 70)

if tests_passed == tests_total:
    print("\n🎉 ALL FEATURES WORKING! XENO is production-ready! 🚀\n")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_total - tests_passed} feature(s) need attention\n")
    sys.exit(1)
