from ..sensors.PulseSensor import PulseSensor
from ..sensors.PulseDataSensor import PulseDataSensor
from ..sensors.PulseBinarySensor import PulseBinarySensor


async def build_sensors(hass, entry, coordinator):
    """Создаёт сенсоры, связанные с hubViewDtos и universalSensorViews."""
    sensors = []

    # TODO: реализовать получение sensor_descriptions для каждого hub + universalSensorView

    return sensors


async def build_binary_sensors(hass, entry, coordinator):
    """Создаёт бинарные сенсоры, связанные с hubViewDtos."""
    sensors = []

    # TODO: реализовать получение binary_sensor_descriptions для каждого hub

    return sensors
