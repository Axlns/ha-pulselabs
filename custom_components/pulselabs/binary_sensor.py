from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .coordinator import PulseDeviceCoordinator

from .entities import pulse_api, pulse_device, pulse_hub


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PulseDeviceCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = []

    entities += await pulse_api.build_binary_sensors(hass, entry, coordinator)
    entities += await pulse_device.build_binary_sensors(hass, entry, coordinator)
    entities += await pulse_hub.build_binary_sensors(hass, entry, coordinator)

    async_add_entities(entities)
