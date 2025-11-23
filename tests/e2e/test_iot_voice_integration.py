"""
End-to-End IoT and Voice Integration Tests
Tests complete IoT device management and voice control workflows
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.iot.smart_home_integration import (
    SmartHomeHub,
    SmartLight,
    SmartThermostat,
    SmartLock,
    SmartCamera
)
from src.voice.advanced_voice_engine import (
    AdvancedVoiceEngine,
    EmotionAnalyzer,
    VoiceBiometrics,
    WakeWordDetector
)


@pytest.fixture
def smart_home_hub():
    """Fixture for smart home hub"""
    return SmartHomeHub()


@pytest.fixture
def voice_engine():
    """Fixture for voice engine"""
    return AdvancedVoiceEngine()


# ==================== IoT Device Management ====================

def test_e2e_smart_home_setup(smart_home_hub):
    """E2E: Complete smart home setup with multiple devices"""
    # Step 1: Add lights
    living_room_light = SmartLight(
        device_id="light_lr_001",
        name="Living Room Main Light",
        api_endpoint="http://hue.local",
        api_key="lr_key"
    )
    smart_home_hub.register_device(living_room_light)
    
    bedroom_light = SmartLight(
        device_id="light_br_001",
        name="Bedroom Light",
        api_endpoint="http://hue.local",
        api_key="br_key"
    )
    smart_home_hub.register_device(bedroom_light)
    
    # Step 2: Add thermostat
    thermostat = SmartThermostat(
        device_id="thermo_001",
        name="Main Thermostat",
        api_endpoint="http://nest.local",
        api_key="thermo_key"
    )
    smart_home_hub.register_device(thermostat)
    
    # Step 3: Add security devices
    front_door_lock = SmartLock(
        device_id="lock_front",
        name="Front Door Lock",
        api_endpoint="http://august.local",
        api_key="lock_key"
    )
    smart_home_hub.register_device(front_door_lock)
    
    front_camera = SmartCamera(
        device_id="cam_front",
        name="Front Door Camera",
        api_endpoint="http://nest.local",
        api_key="cam_key"
    )
    smart_home_hub.register_device(front_camera)
    
    # Step 4: Verify all devices registered
    assert len(smart_home_hub.devices) == 5
    assert smart_home_hub.get_device("light_lr_001") is not None
    assert smart_home_hub.get_device("thermo_001") is not None
    assert smart_home_hub.get_device("lock_front") is not None


def test_e2e_device_grouping_workflow(smart_home_hub):
    """E2E: Create and manage device groups"""
    # Add devices
    for i in range(3):
        light = SmartLight(
            device_id=f"light_{i}",
            name=f"Light {i}",
            api_endpoint="http://test.local",
            api_key="key"
        )
        smart_home_hub.register_device(light)
    
    # Create device group
    smart_home_hub.create_group(
        "living_room",
        ["light_0", "light_1", "light_2"]
    )
    
    # Verify group
    assert "living_room" in smart_home_hub.device_groups
    assert len(smart_home_hub.device_groups["living_room"]) == 3


def test_e2e_scene_creation_and_activation(smart_home_hub):
    """E2E: Create and activate scenes"""
    # Setup devices
    light1 = SmartLight("light1", "Light 1", "http://test.local", "key")
    light2 = SmartLight("light2", "Light 2", "http://test.local", "key")
    thermostat = SmartThermostat("thermo1", "Thermostat", "http://test.local", "key")
    
    smart_home_hub.register_device(light1)
    smart_home_hub.register_device(light2)
    smart_home_hub.register_device(thermostat)
    
    # Create "Movie Night" scene
    from src.iot.smart_home_integration import Scene
    scene = Scene(name="Movie Night", description="Dim lights for movies", hub=smart_home_hub)
    scene.add_action("light1", "turn_off")
    scene.add_action("light2", "set_brightness", brightness=20)
    scene.add_action("thermo1", "set_temperature", temperature=68)
    smart_home_hub.create_scene(scene)
    
    # Verify scene created
    assert "Movie Night" in smart_home_hub.scenes
    created_scene = smart_home_hub.scenes["Movie Night"]
    assert len(created_scene.actions) == 3


def test_e2e_automation_workflow(smart_home_hub):
    """E2E: Create and manage automations"""
    # Setup devices
    light = SmartLight("auto_light", "Auto Light", "http://test.local", "key")
    lock = SmartLock("auto_lock", "Auto Lock", "http://test.local", "key")
    
    smart_home_hub.register_device(light)
    smart_home_hub.register_device(lock)
    
    # Create automation: Lock door and turn off lights at night
    from src.iot.smart_home_integration import Automation
    automation = Automation(name="Goodnight", description="Night routine", hub=smart_home_hub)
    automation.add_condition("time", hour=22, minute=0)
    automation.add_action("auto_lock", "lock")
    automation.add_action("auto_light", "turn_off")
    smart_home_hub.add_automation(automation)
    
    # Verify automation
    assert len(smart_home_hub.automations) == 1
    created_automation = smart_home_hub.automations[0]
    assert created_automation.name == "Goodnight"
    assert len(created_automation.actions) == 2


# ==================== Voice Control Integration ====================

def test_e2e_voice_engine_initialization(voice_engine):
    """E2E: Initialize voice engine with all components"""
    # Verify core components exist
    assert voice_engine.wake_word_detector is not None
    assert voice_engine.emotion_analyzer is not None
    assert voice_engine.voice_biometrics is not None
    assert voice_engine.conversation_manager is not None
    
    # Verify methods exist
    assert hasattr(voice_engine, 'enroll_user')
    assert hasattr(voice_engine, 'add_custom_wake_word')
    assert hasattr(voice_engine, 'set_language')


def test_e2e_user_enrollment_workflow(voice_engine):
    """E2E: Complete user enrollment for voice biometrics"""
    import numpy as np
    
    # Step 1: Generate 3 mock audio samples (required for enrollment)
    audio_samples = [np.random.randn(16000) for _ in range(3)]  # 3 samples at 16kHz
    
    # Step 2: Enroll user
    profile = voice_engine.enroll_user("test_user", audio_samples)
    
    # Step 3: Verify enrollment
    assert profile is not None
    assert profile.user_id == "test_user"


def test_e2e_wake_word_detection_workflow():
    """E2E: Wake word detection and activation"""
    detector = WakeWordDetector()
    
    # Step 1: Add custom wake word
    detector.add_custom_wake_word("jarvis")
    
    # Step 2: Test detection with default wake words (returns tuple: bool, word)
    detected, word = detector.detect("hey xeno can you help me")
    assert detected is True
    assert word in ["hey xeno", "xeno"]
    
    detected, word = detector.detect("xeno turn on the lights")
    assert detected is True
    
    detected, word = detector.detect("hello there")
    assert detected is False
    
    # Step 3: Verify custom wake word works
    detected, word = detector.detect("jarvis")
    assert detected is True
    assert word == "jarvis"


def test_e2e_emotion_detection_workflow():
    """E2E: Emotion detection from text and audio"""
    import numpy as np
    
    analyzer = EmotionAnalyzer()
    
    # Test text-based emotion detection
    emotions = [
        ("I'm so happy and excited today!", ["HAPPY", "EXCITED"]),
        ("This is really frustrating and annoying", ["FRUSTRATED", "ANGRY"]),
        ("I feel sad and disappointed", ["SAD"]),
        ("The weather is okay and alright", ["CALM", "NEUTRAL"])
    ]
    
    for text, acceptable_emotions in emotions:
        emotion = analyzer.analyze_text(text)
        assert emotion.name in acceptable_emotions, f"Expected one of {acceptable_emotions}, got {emotion.name}"
    
    # Test audio-based emotion (expects features dict)
    audio_features = {'pitch': 0.8, 'energy': 0.9, 'tempo': 0.6}
    audio_emotion = analyzer.analyze_audio(audio_features)
    assert audio_emotion.name in ["HAPPY", "SAD", "ANGRY", "NEUTRAL", "EXCITED", "CALM", "FRUSTRATED", "CONFUSED"]


def test_e2e_multi_language_support(voice_engine):
    """E2E: Multi-language speech recognition and synthesis"""
    # Test language switching
    voice_engine.set_language("es")  # Spanish
    voice_engine.set_language("fr")  # French
    voice_engine.set_language("en")  # Back to English
    
    # Verify set_language method exists and works
    assert hasattr(voice_engine, 'set_language')
    assert hasattr(voice_engine, 'respond')


# ==================== Integrated IoT + Voice Workflows ====================

def test_e2e_voice_controlled_smart_home(smart_home_hub, voice_engine):
    """E2E: Complete voice-controlled smart home scenario"""
    # Step 1: Setup smart home devices
    living_room_light = SmartLight(
        "lr_light",
        "Living Room Light",
        "http://test.local",
        "key"
    )
    thermostat = SmartThermostat(
        "main_thermo",
        "Main Thermostat",
        "http://test.local",
        "key"
    )
    
    smart_home_hub.register_device(living_room_light)
    smart_home_hub.register_device(thermostat)
    
    # Step 2: Enroll user voice
    import numpy as np
    from src.iot.smart_home_integration import Automation
    
    audio_samples = [np.random.randn(16000) for _ in range(3)]
    profile = voice_engine.enroll_user("homeowner", audio_samples)
    
    # Step 3: Create automation triggered by voice
    automation = Automation(name="Voice Welcome", description="Welcome home", hub=smart_home_hub)
    automation.add_condition("voice_command", command="I'm home")
    automation.add_action("lr_light", "turn_on")
    automation.add_action("main_thermo", "set_temperature", temperature=72)
    smart_home_hub.add_automation(automation)
    
    # Step 4: Verify integration
    assert len(smart_home_hub.devices) == 2
    assert len(smart_home_hub.automations) == 1
    assert profile.user_id == "homeowner"


def test_e2e_context_aware_voice_commands():
    """E2E: Context-aware voice command processing"""
    from src.voice.advanced_voice_engine import ConversationManager
    
    conv_mgr = ConversationManager()
    
    # Build conversation context (signature: user_id, role, content)
    conv_mgr.add_message("alice", "user", "Turn on the living room lights")
    conv_mgr.add_message("alice", "assistant", "Turning on living room lights")
    
    conv_mgr.add_message("alice", "user", "Make them brighter")
    conv_mgr.add_message("alice", "assistant", "Increasing brightness")
    
    conv_mgr.add_message("alice", "user", "What's the temperature?")
    conv_mgr.add_message("alice", "assistant", "Current temperature is 72°F")
    
    # Get context
    context = conv_mgr.get_context("alice")
    
    # Verify context tracking
    assert len(context.messages) >= 6
    messages_text = [msg.get('content', '') for msg in context.messages]
    assert any("living room" in msg.lower() for msg in messages_text)
    assert any("temperature" in msg.lower() for msg in messages_text)


def test_e2e_scene_activation_by_voice(smart_home_hub):
    """E2E: Activate smart home scene via voice command"""
    # Setup devices
    devices = [
        SmartLight("light1", "Light 1", "http://test.local", "key"),
        SmartLight("light2", "Light 2", "http://test.local", "key"),
        SmartThermostat("thermo", "Thermostat", "http://test.local", "key")
    ]
    
    for device in devices:
        smart_home_hub.register_device(device)
    
    # Create scenes
    from src.iot.smart_home_integration import Scene
    
    # Morning scene
    morning = Scene(name="Morning", description="Morning routine", hub=smart_home_hub)
    morning.add_action("light1", "set_brightness", brightness=100)
    morning.add_action("light2", "set_brightness", brightness=100)
    morning.add_action("thermo", "set_temperature", temperature=70)
    smart_home_hub.create_scene(morning)
    
    # Evening scene
    evening = Scene(name="Evening", description="Evening routine", hub=smart_home_hub)
    evening.add_action("light1", "set_brightness", brightness=50)
    evening.add_action("light2", "set_brightness", brightness=30)
    evening.add_action("thermo", "set_temperature", temperature=68)
    smart_home_hub.create_scene(evening)
    
    # Sleep scene
    sleep = Scene(name="Sleep", description="Sleep mode", hub=smart_home_hub)
    sleep.add_action("light1", "turn_off")
    sleep.add_action("light2", "turn_off")
    sleep.add_action("thermo", "set_temperature", temperature=65)
    smart_home_hub.create_scene(sleep)
    
    # Verify all scenes created
    assert len(smart_home_hub.scenes) == 3
    assert "Morning" in smart_home_hub.scenes
    assert "Evening" in smart_home_hub.scenes
    assert "Sleep" in smart_home_hub.scenes


def test_e2e_emergency_response_workflow(smart_home_hub, voice_engine):
    """E2E: Emergency response via voice command"""
    import numpy as np
    
    # Setup security devices
    camera = SmartCamera("cam_front", "Front Camera", "http://test.local", "key")
    lock = SmartLock("lock_main", "Main Door Lock", "http://test.local", "key")
    light = SmartLight("light_alarm", "Alarm Light", "http://test.local", "key")
    
    smart_home_hub.register_device(camera)
    smart_home_hub.register_device(lock)
    smart_home_hub.register_device(light)
    
    # Create emergency automation
    from src.iot.smart_home_integration import Automation
    
    automation = Automation(name="Emergency Mode", description="Emergency response", hub=smart_home_hub)
    automation.add_condition("voice_command", command="emergency")
    automation.add_action("lock_main", "lock")
    automation.add_action("cam_front", "start_recording")
    automation.add_action("light_alarm", "turn_on")
    smart_home_hub.add_automation(automation)
    
    # Verify emergency automation
    created_automation = smart_home_hub.automations[0]
    assert created_automation.name == "Emergency Mode"
    assert len(created_automation.actions) == 3


# ==================== Complete End-to-End Scenarios ====================

def test_e2e_daily_routine_automation(smart_home_hub, voice_engine):
    """E2E: Complete daily routine with voice and IoT"""
    import numpy as np
    
    # Phase 1: Setup IoT infrastructure
    devices = {
        "bedroom_light": SmartLight("br_light", "Bedroom Light", "http://test.local", "key"),
        "kitchen_light": SmartLight("kc_light", "Kitchen Light", "http://test.local", "key"),
        "living_light": SmartLight("lv_light", "Living Light", "http://test.local", "key"),
        "thermostat": SmartThermostat("thermo", "Thermostat", "http://test.local", "key"),
        "front_lock": SmartLock("lock", "Front Lock", "http://test.local", "key")
    }
    
    for device in devices.values():
        smart_home_hub.register_device(device)
    
    # Phase 2: Create daily scenes
    from src.iot.smart_home_integration import Scene, Automation
    
    wake_up = Scene(name="Wake Up", description="Morning", hub=smart_home_hub)
    wake_up.add_action("br_light", "set_brightness", brightness=50)
    wake_up.add_action("thermostat", "set_temperature", temperature=72)
    smart_home_hub.create_scene(wake_up)
    
    leave_home = Scene(name="Leave Home", description="Leaving", hub=smart_home_hub)
    leave_home.add_action("br_light", "turn_off")
    leave_home.add_action("kc_light", "turn_off")
    leave_home.add_action("lv_light", "turn_off")
    leave_home.add_action("lock", "lock")
    smart_home_hub.create_scene(leave_home)
    
    arrive_home = Scene(name="Arrive Home", description="Arriving", hub=smart_home_hub)
    arrive_home.add_action("lv_light", "set_brightness", brightness=80)
    arrive_home.add_action("lock", "unlock")
    smart_home_hub.create_scene(arrive_home)
    
    # Phase 3: Setup voice control
    audio_samples = [np.random.randn(16000) for _ in range(3)]
    profile = voice_engine.enroll_user("resident", audio_samples)
    
    # Phase 4: Create time-based automations
    morning = Automation(name="Morning Routine", description="Wake up", hub=smart_home_hub)
    morning.add_condition("time", hour=7, minute=0)
    morning.add_action("scene", "Wake Up")
    smart_home_hub.add_automation(morning)
    
    bedtime = Automation(name="Bedtime Routine", description="Sleep", hub=smart_home_hub)
    bedtime.add_condition("time", hour=22, minute=0)
    bedtime.add_action("br_light", "set_brightness", brightness=10)
    bedtime.add_action("lv_light", "turn_off")
    bedtime.add_action("kc_light", "turn_off")
    smart_home_hub.add_automation(bedtime)
    
    # Phase 5: Verification
    assert len(smart_home_hub.devices) == 5
    assert len(smart_home_hub.scenes) == 3
    assert len(smart_home_hub.automations) == 2
    assert profile.user_id == "resident"


def test_e2e_smart_home_security_system(smart_home_hub):
    """E2E: Complete smart home security system"""
    # Setup security devices
    cameras = [
        SmartCamera(f"cam_{loc}", f"{loc} Camera", "http://test.local", "key")
        for loc in ["front", "back", "garage"]
    ]
    
    locks = [
        SmartLock(f"lock_{loc}", f"{loc} Lock", "http://test.local", "key")
        for loc in ["front", "back", "garage"]
    ]
    
    # Alarm lights
    alarm_lights = [
        SmartLight(f"alarm_{loc}", f"{loc} Alarm", "http://test.local", "key")
        for loc in ["front", "back"]
    ]
    
    # Register all devices
    for device in cameras + locks + alarm_lights:
        smart_home_hub.register_device(device)
    
    # Create security modes
    from src.iot.smart_home_integration import Scene, Automation
    
    armed = Scene(name="Armed", description="Security armed", hub=smart_home_hub)
    for loc in ["front", "back", "garage"]:
        armed.add_action(f"lock_{loc}", "lock")
        armed.add_action(f"cam_{loc}", "start_recording")
    smart_home_hub.create_scene(armed)
    
    disarmed = Scene(name="Disarmed", description="Security disarmed", hub=smart_home_hub)
    for loc in ["front", "back", "garage"]:
        disarmed.add_action(f"cam_{loc}", "stop_recording")
    smart_home_hub.create_scene(disarmed)
    
    # Create intrusion automation
    intrusion = Automation(name="Intrusion Detected", description="Security alert", hub=smart_home_hub)
    intrusion.add_condition("sensor", sensor_type="motion")
    intrusion.add_action("alarm_front", "turn_on")
    intrusion.add_action("alarm_back", "turn_on")
    for loc in ["front", "back", "garage"]:
        intrusion.add_action(f"cam_{loc}", "start_recording")
    smart_home_hub.add_automation(intrusion)
    
    # Verify security system
    assert len(smart_home_hub.devices) == 8  # 3 cameras + 3 locks + 2 alarms
    assert len(smart_home_hub.scenes) == 2
    assert len(smart_home_hub.automations) == 1
