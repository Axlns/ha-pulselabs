from __future__ import annotations
from typing import Final, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfPressure,
    PERCENTAGE,
    UnitOfElectricPotential,
    CONCENTRATION_PARTS_PER_MILLION
)
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import PulseCoordinatorEntity
from .const import DOMAIN, CONF_DEVICES, MANUFACTURER, PLAN_LIMITS

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
        "disabled_by_default": True,
        "icon": "mdi:white-balance-sunny"
    },
    "dli": {
        "translation_key": "dli",
        "device_class": None,
        "unit": "mol/m²/d",
        "disabled_by_default": True,
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
        "disabled_by_default": True,
    },
    "batteryV": {
        "translation_key": "battery_voltage",
        "device_class": SensorDeviceClass.VOLTAGE,
        "unit": UnitOfElectricPotential.VOLT,
        "disabled_by_default": True,
    },
    "api_calls": {
        "translation_key": "api_calls_today",
        "unit": "calls",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:counter"
    },
    "api_forecast": {
        "translation_key": "api_calls_forecast",
        "unit": "calls",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chart-line"
    },
}

def build_entities(coordinator, config_entry):
    entities = []

    for device_id, data in coordinator.data.items():
        for key in SENSOR_MAP:
            if key not in data or data[key] is None:
                continue

            spec = SENSOR_MAP[key]
            entity = PulseSensorEntity(
                coordinator=coordinator,
                device_id=device_id,
                data_key=key,
                translation_key=spec.get("translation_key"),
                device_class=spec.get("device_class"),
                unit=spec.get("unit"),
                entity_category=spec.get("entity_category"),
                disabled_by_default = spec.get("disabled_by_default"),
                icon = spec.get("icon")
            )
            
            entities.append(entity)

    plan = config_entry.options.get("plan", "hobbyist").lower()
    limit = PLAN_LIMITS.get(plan, 4800)

    entities.append(DatapointsUsedSensor(coordinator, config_entry.entry_id))
    entities.append(DatapointsRemainingSensor(coordinator, config_entry.entry_id, limit, plan))
       
    return entities

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = build_entities(coordinator, entry)
    async_add_entities(entities)

class PulseSensorEntity(PulseCoordinatorEntity, SensorEntity):
    
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        device_id,
        data_key,
        translation_key=None,
        device_class=None,
        unit=None,
        entity_category=None,
        disabled_by_default=False,
        icon = None
    ):
        super().__init__(coordinator, device_id)
        self._api_key = data_key
        self._attr_unique_id = f"{device_id}_{data_key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = entity_category
        
        if translation_key is not None:
            self._attr_translation_key = translation_key
        if disabled_by_default:
            self._attr_entity_registry_enabled_default = False
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> Any:
        val = self.coordinator.data.get(self._device_id, {}).get(self._api_key)
        return round(val, 2) if isinstance(val, float) else val

class DatapointsUsedSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "api_usage_today"
    _attr_icon = "mdi:counter"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "dps"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_datapoints_used"
        self._attr_device_info = {
            "identifiers":{(DOMAIN, f"api_usage_{entry_id}")},
            "name":"Pulse API",
            "manufacturer":MANUFACTURER,
            "entry_type":DeviceEntryType.SERVICE
        }

    @property
    def native_value(self):
        return self.coordinator.api.datapoints_today

class DatapointsRemainingSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "api_usage_remaining"
    _attr_icon = "mdi:chart-line"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "dps"

    def __init__(self, coordinator, entry_id, limit: int, plan: str):
        super().__init__(coordinator)
        self._limit = limit
        self._plan = plan
        self._attr_unique_id = f"{entry_id}_datapoints_remaining"
        self._attr_device_info = {
            "identifiers":{(DOMAIN, f"api_usage_{entry_id}")},
            "name":"Pulse API",
            "manufacturer":MANUFACTURER,
            "entry_type":DeviceEntryType.SERVICE
        }

    @property
    def native_value(self):
        used = self.coordinator.api.datapoints_today
        return max(0, self._limit - used)

    @property
    def extra_state_attributes(self):
        return {
            "limit": self._limit,
            "plan": self._plan,
        }