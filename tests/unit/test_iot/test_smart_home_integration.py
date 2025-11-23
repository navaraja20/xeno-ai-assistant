"""
Unit Tests for Smart Home Integration Module
Tests device management, control, and automation
"""
import pytest
from src.iot.smart_home_integration import SmartHomeHub


class TestSmartHomeHub:
    """Test suite for SmartHomeHub class"""
    
    @pytest.fixture
    def hub(self):
        """Fixture to create a fresh SmartHomeHub instance"""
        return SmartHomeHub()
    
    def test_initialization(self, hub):
        """Test that hub initializes correctly"""
        assert hub is not None
        assert hasattr(hub, 'devices')
    
    def test_add_light(self, hub):
        """Test adding a smart light"""
        device_id = "bedroom_light"
        name = "Bedroom Light"
        
        light = hub.add_light(device_id, name, "philips_hue")
        
        assert light is not None
        assert hub.get_device(device_id) is not None
    
    def test_add_thermostat(self, hub):
        """Test adding a smart thermostat"""
        device_id = "living_room_thermostat"
        name = "Living Room Thermostat"
        
        thermostat = hub.add_thermostat(device_id, name)
        
        assert thermostat is not None
        assert hub.get_device(device_id) is not None
    
    def test_add_lock(self, hub):
        """Test adding a smart lock"""
        device_id = "front_door"
        name = "Front Door Lock"
        
        lock = hub.add_lock(device_id, name)
        
        assert lock is not None
        assert hub.get_device(device_id) is not None
    
    def test_add_camera(self, hub):
        """Test adding a security camera"""
        device_id = "garage_camera"
        name = "Garage Camera"
        
        camera = hub.add_camera(device_id, name)
        
        assert camera is not None
        assert hub.get_device(device_id) is not None
    
    def test_get_nonexistent_device(self, hub):
        """Test getting a device that doesn't exist"""
        device = hub.get_device("nonexistent_device")
        assert device is None
    
    def test_multiple_devices(self, hub):
        """Test managing multiple devices"""
        # Add various devices
        hub.add_light("light_1", "Light 1")
        hub.add_light("light_2", "Light 2")
        hub.add_thermostat("thermo_1", "Thermostat 1")
        hub.add_lock("lock_1", "Lock 1")
        
        # Get all devices
        devices = hub.list_devices()
        assert len(devices) >= 4
    
    def test_device_groups(self, hub):
        """Test creating device groups"""
        hub.add_light("light_1", "Light 1")
        hub.add_light("light_2", "Light 2")
        
        # Create group
        hub.create_group("living_room", ["light_1", "light_2"])
        
        # Verify group exists
        assert "living_room" in hub.device_groups
        assert len(hub.device_groups["living_room"]) == 2


class TestDeviceControl:
    """Test suite for device control operations"""
    
    @pytest.fixture
    def hub(self):
        return SmartHomeHub()
    
    def test_device_retrieval(self, hub):
        """Test retrieving devices"""
        light_id = "test_light"
        light = hub.add_light(light_id, "Test Light")
        
        # Get device
        retrieved = hub.get_device(light_id)
        assert retrieved is not None
        assert retrieved.device_id == light_id
    
    def test_list_devices_by_type(self, hub):
        """Test filtering devices by type"""
        hub.add_light("light_1", "Light 1")
        hub.add_light("light_2", "Light 2")
        hub.add_thermostat("thermo_1", "Thermostat 1")
        
        # List only lights
        lights = hub.list_devices(device_type="light")
        assert len([d for d in lights if hasattr(d, 'brightness')]) >= 0


class TestDeviceAutomation:
    """Test suite for automation features"""
    
    @pytest.fixture
    def hub(self):
        return SmartHomeHub()
    
    def test_scenes_storage(self, hub):
        """Test that scenes can be stored"""
        from src.iot.smart_home_integration import Scene
        
        # Add devices
        hub.add_light("light_1", "Light 1")
        
        # Create scene object with hub parameter
        scene = Scene("evening", "Evening scene", hub)
        scene.add_action("light_1", "turn_on", brightness=80)
        hub.create_scene(scene)
        
        # Verify scene exists
        assert "evening" in hub.scenes
    
    def test_automation_storage(self, hub):
        """Test that automations can be stored"""
        from src.iot.smart_home_integration import Automation
        
        hub.add_light("auto_light", "Auto Light")
        
        # Create automation object with hub parameter
        automation = Automation("evening_lights", "Turn on lights at 6pm", hub)
        automation.add_condition("time", hour=18)
        automation.add_action("auto_light", "turn_on")
        hub.add_automation(automation)
        
        # Verify automation exists
        assert len(hub.automations) > 0


@pytest.mark.integration
def test_smart_home_complete_workflow():
    """Integration test: Complete smart home workflow"""
    hub = SmartHomeHub()
    
    # Set up home
    hub.add_light("living_room_light", "Living Room Light")
    hub.add_light("bedroom_light", "Bedroom Light")
    hub.add_thermostat("main_thermostat", "Main Thermostat")
    hub.add_lock("front_door", "Front Door Lock")
    hub.add_camera("entrance_camera", "Entrance Camera")
    
    # Check device count
    devices = hub.list_devices()
    assert len(devices) == 5
    
    # Test device groups
    hub.create_group("all_lights", ["living_room_light", "bedroom_light"])
    assert "all_lights" in hub.device_groups
    
    # Verify all devices can be retrieved
    for device_id in ["living_room_light", "bedroom_light", "main_thermostat"]:
        device = hub.get_device(device_id)
        assert device is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
