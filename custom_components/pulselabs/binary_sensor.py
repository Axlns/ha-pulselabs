from __future__ import annotations
from typing import Final, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import PulseCoordinatorEntity
from .const import DOMAIN, CONF_DEVICES, MANUFACTURER

BINARY_SENSOR_MAP: Final[dict[str, dict[str, Any]]] = {
    "pluggedIn": {
        "translation_key": "plugged_in",
        "device_class": BinarySensorDeviceClass.PLUG,
        "disabled_by_default": True,
    }
}

def build_entities(coordinator, config_entry):
    entities = []

    for device_id, data in coordinator.data.items():
        for key in BINARY_SENSOR_MAP:
            if key not in data or data[key] is None:
                continue

            spec = BINARY_SENSOR_MAP[key]
            entity = PulseBinarySensorEntity(
                coordinator=coordinator,
                device_id=device_id,
                data_key=key,
                translation_key=spec.get("translation_key"),
                device_class=spec.get("device_class"),
                disabled_by_default=spec.get("disabled_by_default"),
                icon=spec.get("icon")
            )

            entities.append(entity)

    return entities

async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities
    ) -> None:
        coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        entities = build_entities(coordinator, entry)
        async_add_entities(entities)

class PulseBinarySensorEntity(PulseCoordinatorEntity, BinarySensorEntity):

    def __init__(
        self,
        coordinator,
        device_id,
        data_key,
        translation_key=None,
        device_class=None,
        disabled_by_default=False,
        icon = None
    ):
        super().__init__(coordinator, device_id)
        self._api_key = data_key
        self._attr_unique_id = f"{device_id}_{data_key}"
        self._attr_device_class = device_class
        if translation_key is not None:
            self._attr_translation_key = translation_key
        if disabled_by_default:
            self._attr_entity_registry_enabled_default = False
        if icon:
            self._attr_icon = icon
        
    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._device_id, {}).get(self._api_key))

    
