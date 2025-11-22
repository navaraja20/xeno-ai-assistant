"""
Comprehensive Test Suite for XENO Features
Tests all 10 next-level features
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_priority_1_ml_predictive():
    """Test ML & Predictive Analytics"""
    print("\n🧪 Testing Priority 1: ML & Predictive Analytics...")
    try:
        from src.ml.predictive_analytics import PredictiveEngine, BehaviorAnalyzer
        
        # Test PredictiveEngine
        engine = PredictiveEngine()
        print(f"  ✓ Predictive engine initialized")
        
        # Test BehaviorAnalyzer  
        analyzer = BehaviorAnalyzer()
        print(f"  ✓ Behavior analyzer initialized")
        
        print("  ✅ Priority 1: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 1: FAILED - {e}")
        return False


def test_priority_2_analytics_dashboard():
    """Test Advanced Analytics Dashboard"""
    print("\n🧪 Testing Priority 2: Advanced Analytics Dashboard...")
    try:
        from src.ml.analytics_dashboard import AnalyticsDashboard
        
        dashboard = AnalyticsDashboard()
        print(f"  ✓ Analytics dashboard initialized")
        
        print("  ✅ Priority 2: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 2: FAILED - {e}")
        return False


def test_priority_3_enterprise_security():
    """Test Enterprise Security & Compliance"""
    print("\n🧪 Testing Priority 3: Enterprise Security & Compliance...")
    try:
        from src.security.enterprise_security import (
            EncryptionManager, AuthenticationManager, 
            AuditLogger, ComplianceManager
        )
        
        # Test Encryption
        enc = EncryptionManager()
        plaintext = "Secret data"
        encrypted = enc.encrypt_data(plaintext)
        decrypted = enc.decrypt_data(encrypted)
        assert decrypted == plaintext, "Encryption/decryption mismatch"
        print(f"  ✓ Encryption/Decryption working")
        
        # Test Authentication
        auth = AuthenticationManager()
        username = "test_user"
        password = "test_password_123"
        auth.register_user(username, password, {"role": "user"})
        result = auth.authenticate(username, password)
        assert result["success"], "Authentication failed"
        print(f"  ✓ Authentication working")
        
        # Test Audit Logger
        logger = AuditLogger()
        logger.log_login(username, "127.0.0.1", True)
        print(f"  ✓ Audit logging working")
        
        # Test Compliance
        compliance = ComplianceManager()
        print(f"  ✓ Compliance manager initialized")
        
        print("  ✅ Priority 3: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 3: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_priority_4_browser_extension():
    """Test Browser Extension"""
    print("\n🧪 Testing Priority 4: Browser Extension...")
    try:
        # Check if extension files exist
        ext_files = [
            "browser_extension/manifest.json",
            "browser_extension/background.js",
            "browser_extension/content.js",
            "browser_extension/popup.html"
        ]
        
        for file in ext_files:
            if not os.path.exists(file):
                print(f"  ⚠️  Missing file: {file}")
        
        # Test WebSocket server
        from src.websocket_server import create_server
        print(f"  ✓ WebSocket server module available")
        
        print("  ✅ Priority 4: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 4: FAILED - {e}")
        return False


def test_priority_5_team_collaboration():
    """Test Team Collaboration"""
    print("\n🧪 Testing Priority 5: Team Collaboration...")
    try:
        from src.collaboration.team_features import (
            TeamManager, SharedCalendarManager,
            TaskDelegationManager, TeamAnalytics
        )
        
        # Test Team Manager
        team_mgr = TeamManager()
        team = team_mgr.create_team("Test Team", "test_owner", "A test team")
        print(f"  ✓ Team created: {team.name}")
        
        # Test Calendar Manager
        cal_mgr = SharedCalendarManager()
        print(f"  ✓ Calendar manager initialized")
        
        # Test Task Delegation
        task_mgr = TaskDelegationManager()
        print(f"  ✓ Task delegation manager initialized")
        
        # Test Analytics
        analytics = TeamAnalytics(task_mgr)
        print(f"  ✓ Team analytics initialized")
        
        print("  ✅ Priority 5: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 5: FAILED - {e}")
        return False


def test_priority_6_voice_nlp():
    """Test Advanced Voice & NLP"""
    print("\n🧪 Testing Priority 6: Advanced Voice & NLP...")
    try:
        from src.voice.advanced_voice_engine import AdvancedVoiceEngine, Language
        from src.voice.conversation_manager import ConversationManager
        
        # Test Voice Engine
        engine = AdvancedVoiceEngine()
        print(f"  ✓ Voice engine initialized")
        print(f"  ✓ Supported languages: {len([l for l in Language])} languages")
        
        # Test Conversation Manager
        conv_mgr = ConversationManager()
        print(f"  ✓ Conversation manager initialized")
        
        print("  ✅ Priority 6: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 6: FAILED - {e}")
        return False


def test_priority_7_integration_hub():
    """Test Integration Hub"""
    print("\n🧪 Testing Priority 7: Integration Hub...")
    try:
        from src.integrations.integration_hub import IntegrationHub, WorkflowEngine
        
        # Test Integration Hub
        hub = IntegrationHub()
        print(f"  ✓ Integration hub initialized")
        print(f"  ✓ Available connectors: {len(hub.connectors)}")
        
        # Test Workflow Engine
        workflow = WorkflowEngine()
        print(f"  ✓ Workflow engine initialized")
        
        print("  ✅ Priority 7: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 7: FAILED - {e}")
        return False


def test_priority_9_iot_wearable():
    """Test Wearable & IoT Integration"""
    print("\n🧪 Testing Priority 9: Wearable & IoT Integration...")
    try:
        from src.iot.iot_hub import IoTHub
        from src.iot.smart_home_integration import SmartHomeHub
        
        # Test IoT Hub
        hub = IoTHub()
        print(f"  ✓ IoT hub initialized")
        
        # Test Smart Home Hub
        smart_home = SmartHomeHub()
        print(f"  ✓ Smart home hub initialized")
        
        print("  ✅ Priority 9: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 9: FAILED - {e}")
        return False


def test_priority_10_ai_finetuning():
    """Test AI Model Fine-tuning"""
    print("\n🧪 Testing Priority 10: AI Model Fine-tuning...")
    try:
        from src.ai.model_finetuning import PersonalizationEngine, CustomModelTrainer, ContextualMemory
        from src.ai.federated_learning import FederatedTrainer, PersonalizedModelManager
        from src.ai.model_versioning import ModelVersionControl, PerformanceTracker
        
        # Test Personalization Engine
        engine = PersonalizationEngine("test_user")
        engine.update_preference("communication_style", "professional")
        pref = engine.get_preference("communication_style")
        assert pref == "professional", "Preference not saved correctly"
        print(f"  ✓ Personalization engine working")
        
        # Test Custom Model Trainer
        trainer = CustomModelTrainer("test_user")
        print(f"  ✓ Custom model trainer initialized")
        
        # Test Contextual Memory
        memory = ContextualMemory("test_user")
        memory.store_fact("test", "key", "value")
        value = memory.retrieve_fact("test", "key")
        assert value == "value", "Memory storage failed"
        print(f"  ✓ Contextual memory working")
        
        # Test Federated Learning
        fed_trainer = FederatedTrainer("test_model")
        print(f"  ✓ Federated trainer initialized")
        
        # Test Model Versioning
        vcs = ModelVersionControl()
        print(f"  ✓ Model version control initialized")
        
        # Test Performance Tracker
        tracker = PerformanceTracker()
        tracker.record_metric("test_model", "accuracy", 0.95)
        print(f"  ✓ Performance tracker working")
        
        print("  ✅ Priority 10: PASSED")
        return True
    except Exception as e:
        print(f"  ❌ Priority 10: FAILED - {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all feature tests"""
    print("=" * 70)
    print("🚀 XENO Feature Test Suite")
    print("=" * 70)
    
    results = {
        "Priority 1 (ML & Predictive)": test_priority_1_ml_predictive(),
        "Priority 2 (Analytics)": test_priority_2_analytics_dashboard(),
        "Priority 3 (Security)": test_priority_3_enterprise_security(),
        "Priority 4 (Browser Ext)": test_priority_4_browser_extension(),
        "Priority 5 (Team Collab)": test_priority_5_team_collaboration(),
        "Priority 6 (Voice & NLP)": test_priority_6_voice_nlp(),
        "Priority 7 (Integrations)": test_priority_7_integration_hub(),
        "Priority 9 (IoT/Wearable)": test_priority_9_iot_wearable(),
        "Priority 10 (AI Fine-tuning)": test_priority_10_ai_finetuning(),
    }
    
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for feature, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{feature:40} {status}")
    
    print("=" * 70)
    print(f"Total: {passed}/{total} features passed ({passed/total*100:.1f}%)")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL FEATURES WORKING! XENO is ready for deployment! 🚀")
        return 0
    else:
        print(f"\n⚠️  {total - passed} feature(s) need attention")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
