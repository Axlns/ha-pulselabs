"""Pulse Labs sensors."""
from __future__ import annotations

from typing import Any
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfPressure, PERCENTAGE

from .const import DOMAIN, CONF_DEVICES, MANUFACTURER
from .coordinator import PulseDataUpdateCoordinator

import logging

_LOGGER = logging.getLogger(__name__)

SENSOR_MAP: dict[str, tuple[str | None, SensorDeviceClass | None, str | None]] = {
    "temperatureF":    ("temperature",      SensorDeviceClass.TEMPERATURE,    UnitOfTemperature.FAHRENHEIT),
    "humidityRh":      ("humidity",         SensorDeviceClass.HUMIDITY,       PERCENTAGE),
    "airPressure":     ("pressure",         SensorDeviceClass.PRESSURE,       UnitOfPressure.PA),
    "vpd":             ("vpd",              None,                             "kPa"),
    "avpd_calculated": ("avpd_calculated",  None,                             "kPa"),
    "lvpd_calculated": ("lvpd_calculated",  None,                             "kPa"),
    "co2":             ("co2",              SensorDeviceClass.CO2,            "ppm"),
    "lightLux":        ("light",            None,                             PERCENTAGE),
    "ppfd":            ("ppfd",             None,                             "μmol/m²/s"),
    "dli":             ("dli",              None,                             "mol/m²/d"),
    "signalStrength":  ("signal_strength",  SensorDeviceClass.SIGNAL_STRENGTH,"dBm"),
    "batteryV":        ("battery_voltage",  SensorDeviceClass.VOLTAGE,        "V"),
    "api_calls":       ("api_calls",        None,                             "calls"),
    "api_forecast":    ("api_forecast",     None,                             "calls"),
}

def build_entities(entry, coordinator):
    """Вернуть список ENTITIES для всех устройств."""
    entities = []

    for dev in entry.data[CONF_DEVICES]:
        dev_id = str(dev["id"])
        dev_name = dev.get("name") or f"{dev['deviceType']} {dev_id}"
        keys = coordinator.data.get(dev_id, {}).keys()

        # обычные sensors
        entities.extend(
            PulseSensor(coordinator, dev_id, key, dev_name)
            for key in SENSOR_MAP
            if key in keys
        )
       
        # usage‑счётчики (один на прибор, чтобы не ломать дашборды)
        entities.append(APICallSensor(coordinator, dev_id, dev_name))
        entities.append(APIForecastSensor(coordinator, dev_id, dev_name))

    return entities

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities = build_entities(entry, coordinator)
    async_add_entities(entities)


class PulseSensor(CoordinatorEntity, SensorEntity):
    """Sensor for one metric of one device."""

    def __init__(self, coordinator, device_id: str, api_key: str, dev_name: str):
        super().__init__(coordinator)

        self._device_id = device_id 
        self._api_key = api_key

        t_key, d_class, unit = SENSOR_MAP[api_key]
        if t_key is not None:
            self._attr_translation_key = t_key
        self._attr_has_entity_name = True
        self._attr_device_class = d_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_unique_id = f"{device_id}_{api_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "manufacturer": MANUFACTURER,
            "name": dev_name,
        }

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._device_id, {}).get(self._api_key)
        return round(val, 2) if isinstance(val, float) else val



class APICallSensor(CoordinatorEntity, SensorEntity):
    """Сенсор: сколько запросов сделано сегодня."""

    _attr_translation_key = "api_calls"
    _attr_icon = "mdi:counter"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "calls"
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, dev_name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{device_id}_api_calls"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "manufacturer": MANUFACTURER,
            "name": dev_name,
        }

    @property
    def native_value(self) -> int | None:
        return self.coordinator.calls_today


# ------------------------------------------------------------------
# 3.  Прогноз использования API к концу суток
# ------------------------------------------------------------------
class APIForecastSensor(CoordinatorEntity, SensorEntity):
    """Прогноз количества вызовов API к концу текущих суток."""

    _attr_translation_key = "api_forecast"
    _attr_icon = "mdi:chart-line"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "calls"
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, dev_name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{device_id}_api_forecast"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "manufacturer": MANUFACTURER,
            "name": dev_name,
        }

    @property
    def native_value(self) -> int | None:
        return self.coordinator.expected_at_end_of_day
