from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    UnitOfElectricPotential,
    PERCENTAGE,
    LIGHT_LUX,
    CONCENTRATION_PARTS_PER_MILLION,
)
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from homeassistant.helpers.entity import EntityCategory

from ..sensors.PulseSensor import PulseSensor
from ..sensors.PulseDataSensor import PulseDataSensor
from ..sensors.PulseBinarySensor import PulseBinarySensor


SENSOR_MAP: dict[str, SensorEntityDescription] = {
    "temperatureF": SensorEntityDescription(
        key="temperatureF",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "humidityRh": SensorEntityDescription(
        key="humidityRh",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "airPressure": SensorEntityDescription(
        key="airPressure",
        translation_key="air_pressure",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.PA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "vpd": SensorEntityDescription(
        key="vpd",
        translation_key="vpd",
        device_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        icon="mdi:leaf-circle",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lvpd_calculated": SensorEntityDescription(
        key="lvpd_calculated",
        translation_key="lvpd_calculated",
        device_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        icon="mdi:leaf-circle-outline",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "avpd_calculated": SensorEntityDescription(
        key="avpd_calculated",
        translation_key="avpd_calculated",
        device_class=None,
        native_unit_of_measurement=UnitOfPressure.KPA,
        icon="mdi:water-opacity",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dpF_calculated": SensorEntityDescription(
        key="dpF_calculated",
        translation_key="dew_point",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        icon="mdi:thermometer-water",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "co2": SensorEntityDescription(
        key="co2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "co2Temperature": SensorEntityDescription(
        key="co2Temperature",
        translation_key="co2_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer-alert",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "co2Rh": SensorEntityDescription(
        key="co2Rh",
        translation_key="co2_humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-alert",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    "ppfd": SensorEntityDescription(
        key="ppfd",
        translation_key="ppfd",
        device_class=None,
        native_unit_of_measurement="µmol/m²/s",
        icon="mdi:white-balance-sunny",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dli": SensorEntityDescription(
        key="dli",
        translation_key="dli",
        device_class=None,
        native_unit_of_measurement="mol/m²/d",
        icon="mdi:solar-power-variant",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "lightLux": SensorEntityDescription(
        key="lightLux",
        translation_key="light",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:brightness-6",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "signalStrength": SensorEntityDescription(
        key="signalStrength",
        translation_key="signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "batteryV": SensorEntityDescription(
        key="batteryV",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}

BINARY_SENSOR_MAP: dict[str, SensorEntityDescription] = {
    "pluggedIn": SensorEntityDescription(
        key="pluggedIn",
        translation_key="plugged_in",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}


# old sensor maps for double check

# SENSOR_MAP: Final[dict[str, dict[str, Any]]] = {
#     "temperatureF": {
#         "translation_key": "temperature",
#         "device_class": SensorDeviceClass.TEMPERATURE,
#         "unit": UnitOfTemperature.FAHRENHEIT,
#     },
#     "humidityRh": {
#         "translation_key": "humidity",
#         "device_class": SensorDeviceClass.HUMIDITY,
#         "unit": PERCENTAGE,
#     },
#     "airPressure": {
#         "translation_key": "air_pressure",
#         "device_class": SensorDeviceClass.PRESSURE,
#         "unit": UnitOfPressure.PA,
#     },
#     "vpd": {
#         "translation_key": "vpd",
#         "device_class": None,
#         "unit": UnitOfPressure.KPA,
#         "icon": "mdi:leaf-circle"
#     },
#     "lvpd_calculated": {
#         "translation_key": "lvpd_calculated",
#         "device_class": None,
#         "unit": UnitOfPressure.KPA,
#         "icon": "mdi:leaf-circle-outline"
#     },
#     "avpd_calculated": {
#         "translation_key": "avpd_calculated",
#         "device_class": None,
#         "unit": UnitOfPressure.KPA,
#         "icon": "mdi:water-opacity"
#     },
#     "dpF_calculated": {
#         "translation_key": "dew_point",
#         "device_class": SensorDeviceClass.TEMPERATURE,
#         "unit": UnitOfTemperature.FAHRENHEIT,
#         "icon": "mdi:thermometer-water"
#     },
#     "co2": {
#         "translation_key": "co2",
#         "device_class": SensorDeviceClass.CO2,
#         "unit": CONCENTRATION_PARTS_PER_MILLION,
#     },
#     "co2Temperature": {
#         "translation_key": "co2_temperature",
#         "device_class": SensorDeviceClass.TEMPERATURE,
#         "unit": UnitOfTemperature.CELSIUS,
#         "disabled_by_default": True,
#         "icon": "mdi:thermometer-alert"
#     },
#     "co2Rh": {
#         "translation_key": "co2_humidity",
#         "device_class": SensorDeviceClass.HUMIDITY,
#         "unit": PERCENTAGE,
#         "disabled_by_default": True,
#         "icon":"mdi:water-alert"
#     },
#     "ppfd": {
#         "translation_key": "ppfd",
#         "device_class": None,
#         "unit": "µmol/m²/s",
#         "icon": "mdi:white-balance-sunny"
#     },
#     "dli": {
#         "translation_key": "dli",
#         "device_class": None,
#         "unit": "mol/m²/d",
#         "icon": "mdi:solar-power-variant"
#     },
#     "lightLux": {
#         "translation_key": "light",
#         "device_class": None,
#         "unit": PERCENTAGE,
#         "icon": "mdi:brightness-6"
#     },
#     "signalStrength": {
#         "translation_key": "signal",
#         "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
#         "unit": "dBm",
#         "entity_category": EntityCategory.DIAGNOSTIC
#     },
#     "batteryV": {
#         "translation_key": "battery_voltage",
#         "device_class": SensorDeviceClass.VOLTAGE,
#         "unit": UnitOfElectricPotential.VOLT,
#         "suggested_display_precision":2,
#         "entity_category": EntityCategory.DIAGNOSTIC
#     }
# }

# BINARY_SENSOR_MAP: Final[dict[str, dict[str, Any]]] = {
#     "pluggedIn": {
#         "translation_key": "plugged_in",
#         "device_class": BinarySensorDeviceClass.PLUG,
#         "entity_category": EntityCategory.DIAGNOSTIC
#     }
# }

def get_sensor_descriptions(device: dict) -> list[SensorEntityDescription]:
    return [desc for key, desc in SENSOR_MAP.items() if key in device]


def get_binary_sensor_descriptions(device: dict) -> list[SensorEntityDescription]:
    return [desc for key, desc in BINARY_SENSOR_MAP.items() if key in device]


async def build_sensors(hass, entry, coordinator):
    sensors = []
    device_map = coordinator.data.get("devices", {})

    for device_id, device in device_map.items():
        if device.get("deviceType") == 2:
            continue

        if not any(k in device for k in SENSOR_MAP):
            continue

        for description in get_sensor_descriptions(device):
            sensors.append(PulseDataSensor(coordinator, entry, device_id, description))

    return sensors


async def build_binary_sensors(hass, entry, coordinator):
    sensors = []
    device_map = coordinator.data.get("devices", {})

    for device_id, device in device_map.items():
        if device.get("deviceType") == 2:
            continue

        if not any(k in device for k in BINARY_SENSOR_MAP):
            continue

        for description in get_binary_sensor_descriptions(device):
            sensors.append(PulseBinarySensor(coordinator, entry, device_id, description))

    return sensors
