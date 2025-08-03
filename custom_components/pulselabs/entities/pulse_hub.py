
from custom_components.pulselabs.sensors import PulseHubConnectedSensor
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass

from ..sensors.PulseHubSensor import PulseHubSensor
from ..sensors.PulseHubBinarySensor import PulseHubBinarySensor
from ..sensors.PulseHubConnectedSensor import PulseHubConnectedSensor

from ..const import (
       HUB_SENSOR_MAP as SENSOR_MAP,
       HUB_BINARY_SENSOR_MAP as BINARY_SENSOR_MAP,
       HUB_CONNECTED_SENSOR_MAP,
       SENSOR_VALUE_MAP,
       MEASURING_UNIT_MAP,
       slugify,
       DeviceType
)

async def build_sensors(hass, entry, coordinator):
    sensors = []

    supported_hubs = (
        (hub_id, hub)
        for hub_id, hub in coordinator.data.get("hubs", {}).items()
        if DeviceType.parse(hub.get("deviceType")) in (DeviceType.Hub,)
    )

    for hub_id, hub in supported_hubs:
        for key, description in SENSOR_MAP.items():
            if key in hub:
                sensors.append(
                    PulseHubSensor(coordinator, entry, hub, description)
                )

    return sensors

async def build_binary_sensors(hass, entry, coordinator):
    sensors = []

    supported_hubs = (
        (hub_id, hub)
        for hub_id, hub in coordinator.data.get("hubs", {}).items()
        if DeviceType.parse(hub.get("deviceType")) in (DeviceType.Hub,)
    )

    for hub_id, hub in supported_hubs:
        for key, description in BINARY_SENSOR_MAP.items():
            if key in hub:
                sensors.append(
                    PulseHubBinarySensor(coordinator, entry, hub, description)
                )

    return sensors

async def build_connected_sensors(hass, entry, coordinator):
    sensors = []

    supported_sensors = (
        (sensor_id, sensor)
        for sensor_id, sensor in coordinator.data.get("sensors", {}).items()
        if DeviceType.parse(sensor.get("deviceType")) in (DeviceType.Sensor,)
    )

    for sensor_id_key, sensor in supported_sensors:
        value_name = sensor.get("valueName")
        unit = sensor.get("measuringUnit", "")
        sensor_type = sensor.get("type")

        # Попробуем взять описание из универсальной MAP
        description = HUB_CONNECTED_SENSOR_MAP.get(sensor_type, {}).get(value_name)

        if not description:
            description = generate_sensor_entity_description(value_name, unit)

        # Принудительно задаём уникальный ключ
        description = SensorEntityDescription(
            key=sensor_id_key,
            translation_key=slugify(value_name),
            native_unit_of_measurement=description.native_unit_of_measurement,
            device_class=description.device_class,
            icon=description.icon,
            entity_category=description.entity_category,
            entity_registry_enabled_default=description.entity_registry_enabled_default,
            suggested_display_precision=description.suggested_display_precision,
            state_class=description.state_class,
        )

        sensors.append(
            PulseHubConnectedSensor(
                coordinator=coordinator,
                entry=entry,
                sensor=sensor,
                description=description,
            )
        )

    return sensors

def generate_sensor_entity_description(param_name: str, unit: str) -> SensorEntityDescription:
    unit = unit.strip() or None

    device_class, ha_unit = SENSOR_VALUE_MAP.get((param_name, unit), (None, None))

    if ha_unit is None and unit in MEASURING_UNIT_MAP:
        ha_unit = MEASURING_UNIT_MAP[unit]

    return SensorEntityDescription(
        translation_key=slugify(param_name),
        native_unit_of_measurement=ha_unit,
        device_class=device_class,
        icon=None,
        state_class=SensorStateClass.MEASUREMENT,
    )