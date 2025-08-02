"""Set‑up for Pulse Labs."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN
from .api import get_api
from .coordinator import PulseDeviceCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pulse Labs integration from a config entry."""
    session = async_get_clientsession(hass)
    api = get_api(session, entry.data[CONF_API_KEY])

    coordinator = PulseDeviceCoordinator(hass, api, entry)
    await coordinator.async_load_api_usage_state()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle migration of entity/device unique_ids to new prefixed format."""
    _LOGGER.info("Starting migration of Pulse Labs entry: %s", entry.entry_id)

    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)

    updated = False

    # Миграция устройств (device identifiers)
    for device in list(dev_reg.devices.values()):
        for ident in device.identifiers:
            if ident[0] == DOMAIN and not ident[1].startswith(entry.entry_id):
                raw = ident[1]
                if raw.isdigit():
                    new_id = f"{entry.entry_id}_device_{raw}"
                elif raw.startswith("hub_") and raw[4:].isdigit():
                    new_id = f"{entry.entry_id}_hub_{raw[4:]}"
                elif raw == "api" or raw == f"api_{entry.entry_id}" or raw == f"api_usage_{entry.entry_id}":
                    new_id = f"{entry.entry_id}_api"
                else:
                    continue

                _LOGGER.info("Migrating device identifier: %s → %s", raw, new_id)
                dev_reg.async_update_device(device.id, new_identifiers={(DOMAIN, new_id)})
                updated = True

    # Миграция сенсоров (unique_id)
    for entity in list(ent_reg.entities.values()):
        if entity.config_entry_id != entry.entry_id:
            continue

        uid = entity.unique_id
        if uid.startswith(entry.entry_id):
            continue  # уже мигрировано

        new_uid = None

        # API-сенсоры
        if uid.startswith(entry.entry_id + "_"):
            # уже в нужном формате (edge case)
            continue
        elif uid.startswith("api_") or uid in ("api_used", "api_remaining", "api_status"):
            key = uid.split("_", 1)[-1]
            new_uid = f"{entry.entry_id}_api_{key}"

        # Сенсоры устройств — начинаются с device_id
        elif uid.split("_", 1)[0].isdigit():
            device_id, key = uid.split("_", 1)
            new_uid = f"{entry.entry_id}_device_{device_id}_{key}"

        # Сенсоры хабов в старом формате не обрабатываются пока (опционально)
        # elif uid.startswith("hub_...")

        if new_uid:
            _LOGGER.info("Migrating entity unique_id: %s → %s", uid, new_uid)
            ent_reg.async_update_entity(entity.entity_id, new_unique_id=new_uid)
            updated = True

    if not updated:
        _LOGGER.info("No migration needed for entry: %s", entry.entry_id)

    return True
