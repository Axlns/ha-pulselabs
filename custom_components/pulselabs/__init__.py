"""Set‑up for Pulse Labs."""
from __future__ import annotations

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, CONF_DEVICES, DEVICE_TYPE_MAP, MANUFACTURER
from .api import get_api
from .coordinator import PulseDeviceCoordinator

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pulse Labs integration from a config entry (one coordinator for all devices)."""
    session = async_get_clientsession(hass)
    api = get_api(session, entry.data[CONF_API_KEY])

    coordinator = PulseDeviceCoordinator(
        hass,
        api,
        entry,
        entry.data[CONF_DEVICES],     # ← список устройств из config_flow
    )

    await coordinator.async_load_api_usage_state()
    await coordinator.async_config_entry_first_refresh()

    # регистрируем каждое устройство
    device_registry = dr.async_get(hass)

    for device in entry.data[CONF_DEVICES]:
        device_id = str(device["id"])
        model = DEVICE_TYPE_MAP.get(device.get("deviceType"), f"Pulse {device.get('deviceType')}")
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            model=model,
            name=device.get("name") or f"{model} {device_id}",
            sw_version=str(device.get("firmwareVersion") or ""),
        )
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
