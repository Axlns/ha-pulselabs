from __future__ import annotations

from typing import Final, Any
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .coordinator import PulseDeviceCoordinator

from .entities import pulse_api, pulse_device, pulse_hub


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PulseDeviceCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    entities += await pulse_api.build_sensors(hass, entry, coordinator)
    entities += await pulse_device.build_sensors(hass, entry, coordinator)
    entities += await pulse_hub.build_sensors(hass, entry, coordinator)
    entities += await pulse_hub.build_connected_sensors(hass, entry, coordinator)

    async_add_entities(entities)
