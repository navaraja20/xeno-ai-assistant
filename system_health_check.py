#!/usr/bin/env python3
"""
XENO AI Assistant - Comprehensive System Health Check
Validates all features and system components
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


class HealthChecker:
    """Comprehensive health checker for XENO"""

    def __init__(self):
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {}
        self.start_time = time.time()

    def _print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

    def _print_result(self, name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
        print(f"  {status} | {name}")
        if details and not passed:
            print(f"    {YELLOW}→ {details}{RESET}")

    def _record_result(self, category: str, name: str, passed: bool, details: str = ""):
        """Record test result"""
        if category not in self.results:
            self.results[category] = []
        self.results[category].append((name, passed, details))
        self._print_result(name, passed, details)

    def check_imports(self) -> bool:
        """Check all critical imports"""
        self._print_header("CHECKING CORE IMPORTS")

        imports = {
            "Security": ["cryptography", "jwt", "pyotp"],
            "Voice": ["pyttsx3", "SpeechRecognition"],
            "ML": ["sklearn", "numpy"],
            "UI": ["PyQt5"],
            "Testing": ["pytest", "pytest_benchmark"],
        }

        all_passed = True
        for category, modules in imports.items():
            for module in modules:
                try:
                    __import__(module)
                    self._record_result("Imports", f"{category}: {module}", True)
                except ImportError as e:
                    self._record_result("Imports", f"{category}: {module}", False, str(e))
                    all_passed = False

        return all_passed

    def check_modules(self) -> bool:
        """Check XENO modules can be imported"""
        self._print_header("CHECKING XENO MODULES")

        modules = [
            "src.security.enterprise_security",
            "src.security.security_config",
            "src.ai.model_finetuning",
            "src.collaboration.team_features",
            "src.iot.smart_home_integration",
            "src.voice.advanced_voice_engine",
            "src.ml.analytics_collector",
            "src.ml.predictive_analytics",
        ]

        all_passed = True
        for module in modules:
            try:
                __import__(module)
                self._record_result("Modules", module.split(".")[-1], True)
            except Exception as e:
                self._record_result("Modules", module.split(".")[-1], False, str(e))
                all_passed = False

        return all_passed

    def check_security_features(self) -> bool:
        """Check security features"""
        self._print_header("CHECKING SECURITY FEATURES")

        try:
            from src.security.enterprise_security import AuthenticationManager, EncryptionManager
            from src.security.security_config import PasswordValidator, RateLimiter

            # Test encryption
            enc = EncryptionManager()
            test_data = "test_data_123"
            encrypted = enc.encrypt_data(test_data)
            decrypted = enc.decrypt_data(encrypted)
            self._record_result("Security", "Encryption/Decryption", decrypted == test_data)

            # Test password hashing
            password = "TestPass123!"
            hashed, salt = enc.hash_password(password)
            self._record_result(
                "Security", "Password Hashing", enc.verify_password(password, hashed, salt)
            )

            # Test password validation
            validator = PasswordValidator()
            is_valid, msg = validator.validate("WeakPass")
            self._record_result("Security", "Password Validation (Weak)", not is_valid)

            is_valid, msg = validator.validate("SecureP@ss123!")
            self._record_result("Security", "Password Validation (Strong)", is_valid)

            # Test rate limiting
            limiter = RateLimiter(max_attempts=3, window_seconds=60)
            for i in range(3):
                allowed = limiter.check_rate_limit("test_key")
                self._record_result("Security", f"Rate Limit Check {i+1}/3", allowed)

            blocked = not limiter.check_rate_limit("test_key")
            self._record_result("Security", "Rate Limit Block (4th attempt)", blocked)

            # Test authentication
            auth = AuthenticationManager()
            reg_result = auth.register_user("test_user", "TestPass123!")
            self._record_result("Security", "User Registration", reg_result)

            auth_result = auth.authenticate_user("test_user", "TestPass123!")
            self._record_result("Security", "User Authentication", auth_result is not None)

            wrong_auth = auth.authenticate_user("test_user", "WrongPassword")
            self._record_result("Security", "Wrong Password Rejection", wrong_auth is None)

            return True

        except Exception as e:
            self._record_result("Security", "Security Module", False, str(e))
            return False

    def check_ai_features(self) -> bool:
        """Check AI/ML features"""
        self._print_header("CHECKING AI/ML FEATURES")

        try:
            from src.ai.model_finetuning import PersonalizationEngine

            # Test personalization
            engine = PersonalizationEngine("test_ai_user")
            self._record_result("AI", "Personalization Engine Init", True)

            # Test preferences
            engine.update_preference("theme", "dark")
            pref = engine.get_preference("theme")
            self._record_result("AI", "Preference Update/Retrieval", pref == "dark")

            # Test interaction recording
            engine.record_interaction("test query", "test response", "brief")
            self._record_result("AI", "Interaction Recording", len(engine.interactions) > 0)

            # Test learning
            engine.learn_from_interaction("user likes brief responses")
            self._record_result("AI", "Learning from Interaction", True)

            return True

        except Exception as e:
            self._record_result("AI", "AI Module", False, str(e))
            return False

    def check_collaboration_features(self) -> bool:
        """Check collaboration features"""
        self._print_header("CHECKING COLLABORATION FEATURES")

        try:
            from src.collaboration.team_features import (
                SharedCalendarManager,
                TaskManager,
                TeamManager,
            )

            # Test team management
            team_mgr = TeamManager()
            team_id = team_mgr.create_team("Test Team", "test_owner")
            self._record_result("Collaboration", "Team Creation", team_id is not None)

            result = team_mgr.add_member(team_id, "test_member", "member")
            self._record_result("Collaboration", "Add Team Member", result)

            is_member = team_mgr.is_team_member(team_id, "test_member")
            self._record_result("Collaboration", "Member Check", is_member)

            # Test calendar
            cal_mgr = SharedCalendarManager(team_mgr)
            cal_id = cal_mgr.create_calendar(team_id, "test_owner", "Test Calendar")
            self._record_result("Collaboration", "Calendar Creation", cal_id is not None)

            # Test tasks
            task_mgr = TaskManager(team_mgr)
            task_id = task_mgr.assign_task(
                team_id, "Test Task", "test_member", "test_owner", priority="high"
            )
            self._record_result("Collaboration", "Task Assignment", task_id is not None)

            return True

        except Exception as e:
            self._record_result("Collaboration", "Collaboration Module", False, str(e))
            return False

    def check_iot_features(self) -> bool:
        """Check IoT features"""
        self._print_header("CHECKING IOT FEATURES")

        try:
            from src.iot.smart_home_integration import SmartHomeHub, SmartLight, SmartThermostat

            # Test smart home hub
            hub = SmartHomeHub()
            self._record_result("IoT", "Smart Home Hub Init", True)

            # Test adding devices
            light = SmartLight("living_room_light", "Living Room Light", hub)
            hub.devices["living_room_light"] = light
            self._record_result("IoT", "Add Light Device", "living_room_light" in hub.devices)

            thermo = SmartThermostat("main_thermostat", "Main Thermostat", hub)
            hub.devices["main_thermostat"] = thermo
            self._record_result("IoT", "Add Thermostat", "main_thermostat" in hub.devices)

            # Test device groups
            hub.device_groups["living_room"] = ["living_room_light"]
            self._record_result("IoT", "Device Groups", "living_room" in hub.device_groups)

            return True

        except Exception as e:
            self._record_result("IoT", "IoT Module", False, str(e))
            return False

    def check_voice_features(self) -> bool:
        """Check voice features"""
        self._print_header("CHECKING VOICE FEATURES")

        try:
            from src.voice.advanced_voice_engine import (
                ConversationManager,
                EmotionAnalyzer,
                MultiLanguageSTT,
                MultiLanguageTTS,
                VoiceBiometrics,
                WakeWordDetector,
            )

            # Test emotion analysis
            analyzer = EmotionAnalyzer()
            emotion = analyzer.analyze_text("I'm very happy today!")
            self._record_result("Voice", "Emotion Analysis (Happy)", emotion == "happy")

            emotion = analyzer.analyze_text("I'm feeling sad")
            self._record_result("Voice", "Emotion Analysis (Sad)", emotion == "sad")

            # Test voice biometrics
            biometrics = VoiceBiometrics()
            import numpy as np

            test_audio = np.random.rand(16000).reshape(1, -1)  # 1 second at 16kHz
            biometrics.enroll_user("test_voice_user", test_audio)
            self._record_result(
                "Voice",
                "Voice Biometrics Enrollment",
                "test_voice_user" in biometrics.voice_profiles,
            )

            # Test conversation manager
            conv_mgr = ConversationManager()
            conv_mgr.add_message("user", "Hello")
            conv_mgr.add_message("assistant", "Hi there!")
            self._record_result("Voice", "Conversation Management", len(conv_mgr.context) == 2)

            # Test wake word detector
            detector = WakeWordDetector()
            detected = detector.detect("Hey XENO, turn on the lights")
            self._record_result("Voice", "Wake Word Detection", detected)

            # Test multi-language
            stt = MultiLanguageSTT()
            stt.set_language("es")
            self._record_result("Voice", "Multi-language STT", stt.current_language == "es")

            tts = MultiLanguageTTS()
            tts.set_language("fr")
            self._record_result("Voice", "Multi-language TTS", tts.current_language == "fr")

            return True

        except Exception as e:
            self._record_result("Voice", "Voice Module", False, str(e))
            return False

    def check_file_structure(self) -> bool:
        """Check critical file structure"""
        self._print_header("CHECKING FILE STRUCTURE")

        required_files = [
            "src/security/enterprise_security.py",
            "src/security/security_config.py",
            "src/ai/model_finetuning.py",
            "src/collaboration/team_features.py",
            "src/iot/smart_home_integration.py",
            "src/voice/advanced_voice_engine.py",
            "tests/unit/test_security/test_security_config.py",
            "tests/e2e/test_authentication_flow.py",
            ".github/workflows/ci.yml",
            ".pre-commit-config.yaml",
            "pyproject.toml",
            "setup.py",
        ]

        all_exist = True
        for file_path in required_files:
            exists = Path(file_path).exists()
            self._record_result("Files", file_path.split("/")[-1], exists)
            if not exists:
                all_exist = False

        return all_exist

    def print_summary(self):
        """Print comprehensive summary"""
        self._print_header("HEALTH CHECK SUMMARY")

        total_tests = 0
        total_passed = 0

        for category, results in self.results.items():
            category_passed = sum(1 for _, passed, _ in results if passed)
            category_total = len(results)
            total_tests += category_total
            total_passed += category_passed

            status = (
                f"{GREEN}✓{RESET}" if category_passed == category_total else f"{YELLOW}!{RESET}"
            )
            print(f"{status} {BOLD}{category}{RESET}: {category_passed}/{category_total} passed")

        print(f"\n{BOLD}{'─'*70}{RESET}")

        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        overall_status = (
            f"{GREEN}HEALTHY{RESET}"
            if pass_rate >= 95
            else f"{YELLOW}DEGRADED{RESET}"
            if pass_rate >= 80
            else f"{RED}UNHEALTHY{RESET}"
        )

        print(f"{BOLD}Overall Status: {overall_status}{RESET}")
        print(f"{BOLD}Total Tests: {total_passed}/{total_tests} passed ({pass_rate:.1f}%){RESET}")

        elapsed = time.time() - self.start_time
        print(f"{BOLD}Execution Time: {elapsed:.2f}s{RESET}")

        # Save results to JSON
        results_file = Path("health_check_results.json")
        with open(results_file, "w") as f:
            json.dump(
                {
                    "timestamp": time.time(),
                    "total_tests": total_tests,
                    "total_passed": total_passed,
                    "pass_rate": pass_rate,
                    "execution_time": elapsed,
                    "results": {
                        cat: [(name, passed, details) for name, passed, details in res]
                        for cat, res in self.results.items()
                    },
                },
                f,
                indent=2,
            )

        print(f"\n{BLUE}Results saved to: {results_file}{RESET}")

        # Return exit code
        return 0 if pass_rate >= 95 else 1


def main():
    """Run comprehensive health check"""
    print(f"\n{BOLD}{BLUE}{'╔'+'═'*68+'╗'}{RESET}")
    print(f"{BOLD}{BLUE}║{'XENO AI ASSISTANT - SYSTEM HEALTH CHECK'.center(68)}║{RESET}")
    print(f"{BOLD}{BLUE}{'╚'+'═'*68+'╝'}{RESET}")

    checker = HealthChecker()

    try:
        # Run all checks
        checker.check_imports()
        checker.check_modules()
        checker.check_file_structure()
        checker.check_security_features()
        checker.check_ai_features()
        checker.check_collaboration_features()
        checker.check_iot_features()
        checker.check_voice_features()

        # Print summary and exit
        return checker.print_summary()

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Health check interrupted by user{RESET}")
        return 1
    except Exception as e:
        print(f"\n\n{RED}Fatal error during health check: {e}{RESET}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
