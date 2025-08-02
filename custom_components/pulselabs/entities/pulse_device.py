from custom_components.pulselabs.sensors import PulseDeviceSensor
from homeassistant.components.sensor import SensorEntityDescription

from ..sensors.PulseDeviceSensor import PulseDeviceSensor
from ..sensors.PulseDeviceBinarySensor import PulseDeviceBinarySensor

from ..const import (DeviceType, DEVICE_SENSOR_MAP as SENSOR_MAP, DEVICE_BINARY_SENSOR_MAP as BINARY_SENSOR_MAP)

SUPPORTED_TYPES = (DeviceType.PulseOne, DeviceType.PulsePro, DeviceType.PulseZero)

def get_sensor_descriptions(device: dict) -> list[SensorEntityDescription]:
    return [desc for key, desc in SENSOR_MAP.items() if key in device]

def get_binary_sensor_descriptions(device: dict) -> list[SensorEntityDescription]:
    return [desc for key, desc in BINARY_SENSOR_MAP.items() if key in device]

async def build_sensors(hass, entry, coordinator):
    sensors = []
    
    supported_devices = (
        (device_id, device)
        for device_id, device in coordinator.data.get("devices", {}).items()
        if DeviceType.parse(device.get("deviceType")) in SUPPORTED_TYPES
    )

    for device_id, device in supported_devices:
        device_type = device.get("deviceType") or DeviceType.Unknown
        
        if not any(k in device for k in SENSOR_MAP):
            continue

        for description in get_sensor_descriptions(device):
            sensors.append(PulseDeviceSensor(coordinator, entry, device, description))

    return sensors

async def build_binary_sensors(hass, entry, coordinator):
    sensors = []
    
    supported_devices = (
        (device_id, device)
        for device_id, device in coordinator.data.get("devices", {}).items()
        if DeviceType.parse(device.get("deviceType")) in SUPPORTED_TYPES
    )

    for device_id, device in supported_devices:
        if not any(k in device for k in BINARY_SENSOR_MAP):
            continue

        for description in get_binary_sensor_descriptions(device):
            sensors.append(PulseDeviceBinarySensor(coordinator, entry, device, description))

    return sensors
