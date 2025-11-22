"""
Wearable & IoT Integration for XENO
Support for smartwatches, fitness trackers, smart home devices, and IoT sensors
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json


class DeviceType(Enum):
    """Types of IoT devices"""
    # Wearables
    SMARTWATCH = "smartwatch"
    FITNESS_TRACKER = "fitness_tracker"
    SMART_RING = "smart_ring"
    SMART_GLASSES = "smart_glasses"
    
    # Smart Home
    SMART_LIGHT = "smart_light"
    SMART_PLUG = "smart_plug"
    SMART_THERMOSTAT = "thermostat"
    SMART_LOCK = "smart_lock"
    SMART_CAMERA = "security_camera"
    SMART_SPEAKER = "smart_speaker"
    
    # Sensors
    TEMPERATURE_SENSOR = "temperature"
    HUMIDITY_SENSOR = "humidity"
    MOTION_SENSOR = "motion"
    DOOR_SENSOR = "door"
    SMOKE_DETECTOR = "smoke"
    
    # Health Devices
    BLOOD_PRESSURE_MONITOR = "blood_pressure"
    GLUCOSE_MONITOR = "glucose"
    SCALE = "smart_scale"
    OXIMETER = "pulse_oximeter"


class DeviceState(Enum):
    """Device connection states"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PAIRING = "pairing"
    ERROR = "error"
    SLEEPING = "sleeping"


@dataclass
class HealthMetrics:
    """Health and fitness metrics"""
    timestamp: datetime
    user_id: str
    
    # Heart metrics
    heart_rate: Optional[int] = None  # BPM
    hrv: Optional[float] = None  # Heart rate variability (ms)
    resting_hr: Optional[int] = None
    max_hr: Optional[int] = None
    
    # Activity metrics
    steps: Optional[int] = None
    distance: Optional[float] = None  # kilometers
    calories_burned: Optional[int] = None
    active_minutes: Optional[int] = None
    floors_climbed: Optional[int] = None
    
    # Sleep metrics
    sleep_duration: Optional[float] = None  # hours
    deep_sleep: Optional[float] = None
    light_sleep: Optional[float] = None
    rem_sleep: Optional[float] = None
    sleep_score: Optional[int] = None
    
    # Vitals
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    blood_oxygen: Optional[int] = None  # SpO2 percentage
    blood_glucose: Optional[float] = None  # mg/dL
    temperature: Optional[float] = None  # Celsius
    weight: Optional[float] = None  # kg
    
    # Stress & recovery
    stress_level: Optional[int] = None  # 0-100
    recovery_score: Optional[int] = None  # 0-100
    energy_level: Optional[int] = None  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            **{k: v for k, v in self.__dict__.items() 
               if k not in ['timestamp', 'user_id'] and v is not None}
        }


@dataclass
class Device:
    """IoT device representation"""
    device_id: str
    name: str
    type: DeviceType
    manufacturer: str
    model: str
    
    state: DeviceState = DeviceState.DISCONNECTED
    battery_level: Optional[int] = None
    firmware_version: Optional[str] = None
    last_sync: Optional[datetime] = None
    
    capabilities: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.type.value,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'state': self.state.value,
            'battery_level': self.battery_level,
            'firmware_version': self.firmware_version,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'capabilities': self.capabilities,
            'properties': self.properties
        }


class WearableIntegration:
    """Base class for wearable device integrations"""
    
    def __init__(self, device: Device):
        self.device = device
        
    async def connect(self) -> bool:
        """Connect to wearable device"""
        raise NotImplementedError
    
    async def disconnect(self) -> bool:
        """Disconnect from device"""
        raise NotImplementedError
    
    async def sync_data(self) -> Dict[str, Any]:
        """Sync data from device"""
        raise NotImplementedError
    
    async def get_health_metrics(self) -> HealthMetrics:
        """Get current health metrics"""
        raise NotImplementedError
    
    async def send_notification(self, title: str, message: str) -> bool:
        """Send notification to wearable"""
        raise NotImplementedError


class AppleWatchIntegration(WearableIntegration):
    """Apple Watch integration"""
    
    async def connect(self) -> bool:
        """Connect to Apple Watch"""
        # Uses HealthKit API
        print(f"Connecting to Apple Watch: {self.device.name}")
        self.device.state = DeviceState.CONNECTED
        self.device.last_sync = datetime.now()
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def sync_data(self) -> Dict[str, Any]:
        """Sync HealthKit data"""
        # In production, use HealthKit API
        return {
            'steps': 8245,
            'heart_rate': 72,
            'calories': 2150,
            'distance': 6.5,
            'active_minutes': 45
        }
    
    async def get_health_metrics(self) -> HealthMetrics:
        """Get health metrics from HealthKit"""
        data = await self.sync_data()
        
        return HealthMetrics(
            timestamp=datetime.now(),
            user_id=self.device.properties.get('user_id', 'unknown'),
            heart_rate=data.get('heart_rate'),
            steps=data.get('steps'),
            calories_burned=data.get('calories'),
            distance=data.get('distance'),
            active_minutes=data.get('active_minutes')
        )
    
    async def send_notification(self, title: str, message: str) -> bool:
        """Send notification to Apple Watch"""
        print(f"Sending to Apple Watch: {title} - {message}")
        return True


class FitbitIntegration(WearableIntegration):
    """Fitbit integration"""
    
    def __init__(self, device: Device, api_token: str):
        super().__init__(device)
        self.api_token = api_token
        self.base_url = "https://api.fitbit.com/1"
    
    async def connect(self) -> bool:
        """Connect to Fitbit API"""
        print(f"Connecting to Fitbit: {self.device.name}")
        self.device.state = DeviceState.CONNECTED
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def sync_data(self) -> Dict[str, Any]:
        """Sync data from Fitbit API"""
        import aiohttp
        
        headers = {'Authorization': f'Bearer {self.api_token}'}
        
        async with aiohttp.ClientSession() as session:
            # Get today's activity
            async with session.get(
                f"{self.base_url}/user/-/activities/date/today.json",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
        
        return {}
    
    async def get_health_metrics(self) -> HealthMetrics:
        """Get Fitbit health metrics"""
        data = await self.sync_data()
        summary = data.get('summary', {})
        
        return HealthMetrics(
            timestamp=datetime.now(),
            user_id=self.device.properties.get('user_id', 'unknown'),
            steps=summary.get('steps'),
            distance=summary.get('distances', [{}])[0].get('distance'),
            calories_burned=summary.get('caloriesOut'),
            active_minutes=summary.get('veryActiveMinutes', 0) + summary.get('fairlyActiveMinutes', 0),
            floors_climbed=summary.get('floors'),
            resting_hr=summary.get('restingHeartRate')
        )
    
    async def send_notification(self, title: str, message: str) -> bool:
        """Fitbit doesn't support push notifications"""
        return False


class GarminIntegration(WearableIntegration):
    """Garmin Connect integration"""
    
    def __init__(self, device: Device, username: str, password: str):
        super().__init__(device)
        self.username = username
        self.password = password
    
    async def connect(self) -> bool:
        """Connect to Garmin Connect"""
        print(f"Connecting to Garmin: {self.device.name}")
        self.device.state = DeviceState.CONNECTED
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def sync_data(self) -> Dict[str, Any]:
        """Sync from Garmin Connect"""
        # Use garminconnect library
        return {
            'steps': 9500,
            'heart_rate': 68,
            'stress': 35,
            'body_battery': 75
        }
    
    async def get_health_metrics(self) -> HealthMetrics:
        """Get Garmin health metrics"""
        data = await self.sync_data()
        
        return HealthMetrics(
            timestamp=datetime.now(),
            user_id=self.device.properties.get('user_id', 'unknown'),
            steps=data.get('steps'),
            heart_rate=data.get('heart_rate'),
            stress_level=data.get('stress'),
            energy_level=data.get('body_battery')
        )
    
    async def send_notification(self, title: str, message: str) -> bool:
        """Send notification to Garmin device"""
        print(f"Sending to Garmin: {title} - {message}")
        return True


class SmartHomeDevice:
    """Base class for smart home devices"""
    
    def __init__(self, device: Device):
        self.device = device
    
    async def connect(self) -> bool:
        """Connect to device"""
        raise NotImplementedError
    
    async def disconnect(self) -> bool:
        """Disconnect from device"""
        raise NotImplementedError
    
    async def get_state(self) -> Dict[str, Any]:
        """Get device state"""
        raise NotImplementedError
    
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """Set device state"""
        raise NotImplementedError


class PhilipsHueLight(SmartHomeDevice):
    """Philips Hue smart light"""
    
    def __init__(self, device: Device, bridge_ip: str, api_key: str):
        super().__init__(device)
        self.bridge_ip = bridge_ip
        self.api_key = api_key
        self.light_id = device.properties.get('light_id')
    
    async def connect(self) -> bool:
        self.device.state = DeviceState.CONNECTED
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def get_state(self) -> Dict[str, Any]:
        """Get light state"""
        import aiohttp
        
        url = f"http://{self.bridge_ip}/api/{self.api_key}/lights/{self.light_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    state = data.get('state', {})
                    return {
                        'on': state.get('on', False),
                        'brightness': state.get('bri', 0),
                        'hue': state.get('hue', 0),
                        'saturation': state.get('sat', 0)
                    }
        return {}
    
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """Set light state"""
        import aiohttp
        
        url = f"http://{self.bridge_ip}/api/{self.api_key}/lights/{self.light_id}/state"
        
        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=state) as response:
                return response.status == 200
    
    async def turn_on(self, brightness: int = 254):
        """Turn light on"""
        return await self.set_state({'on': True, 'bri': brightness})
    
    async def turn_off(self):
        """Turn light off"""
        return await self.set_state({'on': False})
    
    async def set_color(self, hue: int, saturation: int = 254):
        """Set light color"""
        return await self.set_state({'hue': hue, 'sat': saturation})
    
    async def set_brightness(self, brightness: int):
        """Set brightness (0-254)"""
        return await self.set_state({'bri': brightness})


class NestThermostat(SmartHomeDevice):
    """Nest Smart Thermostat"""
    
    def __init__(self, device: Device, access_token: str):
        super().__init__(device)
        self.access_token = access_token
        self.device_id = device.device_id
    
    async def connect(self) -> bool:
        self.device.state = DeviceState.CONNECTED
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def get_state(self) -> Dict[str, Any]:
        """Get thermostat state"""
        # Use Nest API
        return {
            'mode': 'heat',
            'current_temperature': 21.5,
            'target_temperature': 22.0,
            'humidity': 45
        }
    
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """Set thermostat state"""
        print(f"Setting Nest thermostat: {state}")
        return True
    
    async def set_temperature(self, temperature: float):
        """Set target temperature"""
        return await self.set_state({'target_temperature': temperature})
    
    async def set_mode(self, mode: str):
        """Set mode (heat, cool, heat-cool, off)"""
        return await self.set_state({'mode': mode})


class SmartPlugIntegration(SmartHomeDevice):
    """TP-Link Kasa Smart Plug"""
    
    async def connect(self) -> bool:
        self.device.state = DeviceState.CONNECTED
        return True
    
    async def disconnect(self) -> bool:
        self.device.state = DeviceState.DISCONNECTED
        return True
    
    async def get_state(self) -> Dict[str, Any]:
        """Get plug state"""
        # Use python-kasa library
        return {
            'on': True,
            'power': 45.2,  # Watts
            'voltage': 120.0,
            'current': 0.38
        }
    
    async def set_state(self, state: Dict[str, Any]) -> bool:
        """Set plug state"""
        print(f"Setting smart plug: {state}")
        return True
    
    async def turn_on(self):
        """Turn plug on"""
        return await self.set_state({'on': True})
    
    async def turn_off(self):
        """Turn plug off"""
        return await self.set_state({'on': False})


class IoTHub:
    """Central hub for managing all IoT devices"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.integrations: Dict[str, Any] = {}
        self.health_data: List[HealthMetrics] = []
        
    def register_device(self, device: Device):
        """Register new IoT device"""
        self.devices[device.device_id] = device
        print(f"Registered device: {device.name} ({device.type.value})")
    
    def unregister_device(self, device_id: str):
        """Unregister device"""
        if device_id in self.devices:
            del self.devices[device_id]
            if device_id in self.integrations:
                del self.integrations[device_id]
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """Get all devices of specific type"""
        return [d for d in self.devices.values() if d.type == device_type]
    
    def add_integration(self, device_id: str, integration: Any):
        """Add device integration"""
        self.integrations[device_id] = integration
    
    async def connect_device(self, device_id: str) -> bool:
        """Connect to device"""
        integration = self.integrations.get(device_id)
        if integration:
            return await integration.connect()
        return False
    
    async def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from device"""
        integration = self.integrations.get(device_id)
        if integration:
            return await integration.disconnect()
        return False
    
    async def sync_wearable(self, device_id: str) -> Optional[HealthMetrics]:
        """Sync data from wearable device"""
        integration = self.integrations.get(device_id)
        if isinstance(integration, WearableIntegration):
            metrics = await integration.get_health_metrics()
            self.health_data.append(metrics)
            return metrics
        return None
    
    async def send_wearable_notification(
        self,
        device_id: str,
        title: str,
        message: str
    ) -> bool:
        """Send notification to wearable"""
        integration = self.integrations.get(device_id)
        if isinstance(integration, WearableIntegration):
            return await integration.send_notification(title, message)
        return False
    
    async def control_smart_home(
        self,
        device_id: str,
        action: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """Control smart home device"""
        integration = self.integrations.get(device_id)
        if isinstance(integration, SmartHomeDevice):
            if action == 'set_state':
                return await integration.set_state(parameters)
            elif hasattr(integration, action):
                method = getattr(integration, action)
                return await method(**parameters)
        return False
    
    def get_health_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get health summary for user"""
        cutoff = datetime.now() - timedelta(days=days)
        user_metrics = [
            m for m in self.health_data
            if m.user_id == user_id and m.timestamp >= cutoff
        ]
        
        if not user_metrics:
            return {}
        
        # Calculate averages
        avg_steps = sum(m.steps or 0 for m in user_metrics) // len(user_metrics)
        avg_hr = sum(m.heart_rate or 0 for m in user_metrics) // len(user_metrics)
        total_distance = sum(m.distance or 0 for m in user_metrics)
        
        return {
            'period_days': days,
            'data_points': len(user_metrics),
            'average_steps': avg_steps,
            'average_heart_rate': avg_hr,
            'total_distance': total_distance,
            'latest': user_metrics[-1].to_dict() if user_metrics else None
        }
    
    def get_connected_devices(self) -> List[Device]:
        """Get all connected devices"""
        return [d for d in self.devices.values() if d.state == DeviceState.CONNECTED]
    
    def export_health_data(self, user_id: str, filepath: str):
        """Export health data to JSON"""
        user_metrics = [m for m in self.health_data if m.user_id == user_id]
        
        data = {
            'user_id': user_id,
            'export_date': datetime.now().isoformat(),
            'total_records': len(user_metrics),
            'data': [m.to_dict() for m in user_metrics]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
