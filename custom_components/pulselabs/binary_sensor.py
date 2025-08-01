from __future__ import annotations
from typing import Final, Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.helpers.entity import EntityCategory

from .sensors.PulseBinarySensor import  PulseBinarySensor
from .sensors.ApiStatusSensor import  ApiStatusSensor
from .const import DOMAIN, CONF_DEVICES, MANUFACTURER

BINARY_SENSOR_MAP: Final[dict[str, dict[str, Any]]] = {
    "pluggedIn": {
        "translation_key": "plugged_in",
        "device_class": BinarySensorDeviceClass.PLUG,
        "entity_category": EntityCategory.DIAGNOSTIC
    }
}

def build_entities(coordinator, config_entry):
    entities = []

    entity = ApiStatusSensor(coordinator,config_entry.entry_id)
    entities.append(entity)

    for device_id, data in coordinator.data.items():
        for key in BINARY_SENSOR_MAP:
            if key not in data or data[key] is None:
                continue

            spec = BINARY_SENSOR_MAP[key]
            entity = PulseBinarySensor(
                coordinator=coordinator,
                device_id=device_id,
                data_key=key,
                translation_key=spec.get("translation_key"),
                device_class=spec.get("device_class"),
                disabled_by_default=spec.get("disabled_by_default"),
                icon=spec.get("icon"),
                entity_category=spec.get("entity_category")
            )
            entities.append(entity)

    return entities

async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities
    ) -> None:
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        entities = build_entities(coordinator, entry)
        async_add_entities(entities)
