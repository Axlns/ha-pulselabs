"""Constants for the Pulse Labs integration."""
import re

from enum import IntEnum
from homeassistant.components.sensor import SensorEntityDescription, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from homeassistant.const import ( 
    UnitOfElectricPotential,
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfConductivity,
    CONCENTRATION_PARTS_PER_MILLION,
    UnitOfPressure,
    LIGHT_LUX,
)

from homeassistant.helpers.entity import EntityCategory


DOMAIN = "pulselabs"

BASE_URL = "https://api.pulsegrow.com"

MANUFACTURER = "Pulse Labs, Inc."


PLAN_LIMITS = {
    "hobbyist": 4800,
    "enthusiast": 24000,
    "professional": 120000,
}

class DeviceType(IntEnum):
    PulseOne=0
    PulsePro=1
    Hub=2
    Sensor=3
    Controller=4
    PulseZero=5
    Unknown = -1

    @classmethod
    def parse(cls, value) -> "DeviceType":
        return cls._value2member_map_.get(value, cls.Unknown)

DEVICE_TYPE_MAP: dict[DeviceType, str] = {
    DeviceType.PulseOne: "Pulse One",
    DeviceType.PulsePro: "Pulse Pro",
    DeviceType.Hub: "Pulse Hub",
    DeviceType.Sensor: "Pulse Sensor",
    DeviceType.Controller: "Pulse Controller",
    DeviceType.PulseZero: "Pulse Zero",
    DeviceType.Unknown: "Uknown"
}

DEVICE_SENSOR_MAP: dict[str, SensorEntityDescription] = {
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

DEVICE_BINARY_SENSOR_MAP: dict[str, SensorEntityDescription] = {
    "pluggedIn": SensorEntityDescription(
        key="pluggedIn",
        translation_key="plugged_in",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

HUB_SENSOR_MAP: dict[str, SensorEntityDescription] = {
    "batteryV": SensorEntityDescription(
        key="batteryV",
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
    ),
    "signalStrength": SensorEntityDescription(
        key="signalStrength",
        translation_key="signal_strength",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

HUB_BINARY_SENSOR_MAP: dict[str, SensorEntityDescription] = {
    "pluggedIn": SensorEntityDescription(
        key="pluggedIn",
        translation_key="plugged_in",
        device_class=BinarySensorDeviceClass.PLUG,
        entity_category=EntityCategory.DIAGNOSTIC,
    )
}

class SensorType(IntEnum):
    HUB = 0
    VWC1 = 1
    THV1 = 2
    PH10 = 3
    EC1 = 4
    VWC12 = 5
    PAR1 = 8
    VWC2 = 9
    ORP1 = 10
    THC1 = 11
    TDO1 = 12
    VWC3 = 13
    Unknown = -1

    @classmethod
    def parse(cls, value) -> "SensorType":
        return cls._value2member_map_.get(value, cls.Unknown)

SENSOR_TYPE_MAP: dict[SensorType, str] = {

    SensorType.HUB: "Hub",
    SensorType.VWC1: "VWC1",
    SensorType.THV1: "THV1",
    SensorType.PH10: "PH10",
    SensorType.EC1: "EC1",
    SensorType.VWC12: "VWC12",
    SensorType.PAR1: "PAR1",
    SensorType.VWC2: "VWC2",
    SensorType.ORP1: "ORP1",
    SensorType.THC1: "THC1",
    SensorType.TDO1: "TDO1",
    SensorType.VWC3: "VWC3",
    SensorType.Unknown: "Unknown",
}

UNIVERSAL_SENSOR_MAP = {
    SensorType.VWC1: {
        "Water Content": SensorEntityDescription(
            key=None,
            translation_key="water_content",
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:water-percent",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Pore Water EC": SensorEntityDescription(
            key=None,
            translation_key="pore_water_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Bulk EC": SensorEntityDescription(
            key=None,
            translation_key="bulk_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.THV1: {
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Humidity": SensorEntityDescription(
            key=None,
            translation_key="humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "VPD": SensorEntityDescription(
            key=None,
            translation_key="vpd",
            native_unit_of_measurement=UnitOfPressure.KPA,
            icon="mdi:leaf-circle",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Dew Point": SensorEntityDescription(
            key=None,
            translation_key="dew_point",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.PH10: {
        "pH": SensorEntityDescription(
            key=None,
            translation_key="ph",
            native_unit_of_measurement="",
            icon="mdi:water",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.EC1: {
        "EC": SensorEntityDescription(
            key=None,
            translation_key="ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.VWC12: {
        "Water Content": SensorEntityDescription(
            key=None,
            translation_key="water_content",
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:water-percent",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Pore Water EC": SensorEntityDescription(
            key=None,
            translation_key="pore_water_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Bulk EC": SensorEntityDescription(
            key=None,
            translation_key="bulk_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.PAR1: {
        "PPFD": SensorEntityDescription(
            key=None,
            translation_key="ppfd",
            native_unit_of_measurement="umol",
            icon="mdi:white-balance-sunny",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "DLI": SensorEntityDescription(
            key=None,
            translation_key="dli",
            native_unit_of_measurement="mol/m²",
            icon="mdi:solar-power-variant",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.VWC2: {
        "Water Content": SensorEntityDescription(
            key=None,
            translation_key="water_content",
            native_unit_of_measurement=PERCENTAGE,
            icon="mdi:water-percent",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Pore Water EC": SensorEntityDescription(
            key=None,
            translation_key="pore_water_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash-outline",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Bulk EC": SensorEntityDescription(
            key=None,
            translation_key="bulk_ec",
            native_unit_of_measurement="mS/cm",
            icon="mdi:flash",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.ORP1: {
        "Orp": SensorEntityDescription(
            key=None,
            translation_key="orp",
            native_unit_of_measurement="mv",
            icon="mdi:atom",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.THC1: {
        "Co2": SensorEntityDescription(
            key=None,
            translation_key="co2",
            native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
            device_class=SensorDeviceClass.CO2,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Humidity": SensorEntityDescription(
            key=None,
            translation_key="humidity",
            device_class=SensorDeviceClass.HUMIDITY,
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "VPD": SensorEntityDescription(
            key=None,
            translation_key="vpd",
            native_unit_of_measurement=UnitOfPressure.KPA,
            icon="mdi:leaf-circle",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Dew Point": SensorEntityDescription(
            key=None,
            translation_key="dew_point",
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            device_class=SensorDeviceClass.TEMPERATURE,
            icon="mdi:thermometer-water",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Light": SensorEntityDescription(
            key=None,
            translation_key="light",
            native_unit_of_measurement="Lux",
            icon="mdi:brightness-5",
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
    SensorType.TDO1: {
        "Dissolved Oxygen": SensorEntityDescription(
            key=None,
            translation_key="dissolved_oxygen",
            native_unit_of_measurement="mg/L",
            icon="mdi:fishbowl",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        "Temperature": SensorEntityDescription(
            key=None,
            translation_key="temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
            state_class=SensorStateClass.MEASUREMENT,
        ),
    },
}

def slugify(text: str) -> str:
    return re.sub(r"[^\w]+", "_", text.strip().lower()).strip("_")