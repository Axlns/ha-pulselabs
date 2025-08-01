from __future__ import annotations
from typing import Final, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    PERCENTAGE,
    UnitOfElectricPotential,
    CONCENTRATION_PARTS_PER_MILLION
)
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN, PLAN_LIMITS

from .sensors.PulseDataSensor import PulseDataSensor
from .sensors.ApiUsedSensor import ApiUsedSensor
from .sensors.ApiRemainingSensor import ApiRemainingSensor

import logging
_LOGGER = logging.getLogger(__name__)

SENSOR_MAP: Final[dict[str, dict[str, Any]]] = {
    "temperatureF": {
        "translation_key": "temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.FAHRENHEIT,
    },
    "humidityRh": {
        "translation_key": "humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
    },
    "airPressure": {
        "translation_key": "air_pressure",
        "device_class": SensorDeviceClass.PRESSURE,
        "unit": UnitOfPressure.PA,
    },
    "vpd": {
        "translation_key": "vpd",
        "device_class": None,
        "unit": UnitOfPressure.KPA,
        "icon": "mdi:leaf-circle"
    },
    "lvpd_calculated": {
        "translation_key": "lvpd_calculated",
        "device_class": None,
        "unit": UnitOfPressure.KPA,
        "icon": "mdi:leaf-circle-outline"
    },
    "avpd_calculated": {
        "translation_key": "avpd_calculated",
        "device_class": None,
        "unit": UnitOfPressure.KPA,
        "icon": "mdi:water-opacity"
    },
    "dpF_calculated": {
        "translation_key": "dew_point",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.FAHRENHEIT,
        "icon": "mdi:thermometer-water"
    },
    "co2": {
        "translation_key": "co2",
        "device_class": SensorDeviceClass.CO2,
        "unit": CONCENTRATION_PARTS_PER_MILLION,
    },
    "co2Temperature": {
        "translation_key": "co2_temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit": UnitOfTemperature.CELSIUS,
        "disabled_by_default": True,
        "icon": "mdi:thermometer-alert"
    },
    "co2Rh": {
        "translation_key": "co2_humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit": PERCENTAGE,
        "disabled_by_default": True,
        "icon":"mdi:water-alert"
    },
    "ppfd": {
        "translation_key": "ppfd",
        "device_class": None,
        "unit": "µmol/m²/s",
        "icon": "mdi:white-balance-sunny"
    },
    "dli": {
        "translation_key": "dli",
        "device_class": None,
        "unit": "mol/m²/d",
        "icon": "mdi:solar-power-variant"
    },
    "lightLux": {
        "translation_key": "light",
        "device_class": None,
        "unit": PERCENTAGE,
        "icon": "mdi:brightness-6"
    },
    "signalStrength": {
        "translation_key": "signal",
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "unit": "dBm",
        "entity_category": EntityCategory.DIAGNOSTIC
    },
    "batteryV": {
        "translation_key": "battery_voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": UnitOfElectricPotential.VOLT,
        "suggested_display_precision":2,
        "entity_category": EntityCategory.DIAGNOSTIC
    }
}

def build_entities(coordinator, config_entry):
    entities = []

    for device_id, data in coordinator.data.items():
        for key in SENSOR_MAP:
            if key not in data or data[key] is None:
                continue

            spec = SENSOR_MAP[key]
            entity = PulseDataSensor(
                coordinator=coordinator,
                device_id=device_id,
                data_key=key,
                translation_key=spec.get("translation_key"),
                device_class=spec.get("device_class"),
                disabled_by_default = spec.get("disabled_by_default"),
                icon = spec.get("icon"),
                unit=spec.get("unit"),
                entity_category=spec.get("entity_category"),
                suggested_display_precision=spec.get("suggested_display_precision")
            )
            
            entities.append(entity)

    plan = config_entry.options.get("plan", "hobbyist").lower()
    limit = PLAN_LIMITS.get(plan, 4800)

    #добавляем диагностические сенсоры (в рамках отдельного устройства-службы)
    entities.append(ApiUsedSensor(coordinator, config_entry.entry_id))
    entities.append(ApiRemainingSensor(coordinator, config_entry.entry_id, limit, plan))
       
    return entities

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = build_entities(coordinator, entry)
    async_add_entities(entities)