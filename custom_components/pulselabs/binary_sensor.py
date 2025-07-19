# custom_components/pulselabs/binary_sensor.py
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICES, MANUFACTURER


class PluggedInBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """True – прибор питается от сети, False – от батареи."""

    _attr_translation_key = "plugged_in"           # можно убрать, если довольны системным переводом
    _attr_device_class = BinarySensorDeviceClass.PLUG
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, dev_name: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_pluggedIn"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device_id)},
            "manufacturer": MANUFACTURER,
            "name": dev_name,
        }

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._device_id, {}).get("pluggedIn")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Создаём сущности только для приборов, у которых в данных есть `pluggedIn`."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []
    for dev in entry.data[CONF_DEVICES]:
        dev_id = str(dev["id"])
        # ← проверяем наличие ключа в данных, полученных с /all-devices
        if "pluggedIn" in coordinator.data.get(dev_id, {}):
            entities.append(
                PluggedInBinarySensor(
                    coordinator,
                    dev_id,
                    dev.get("name") or f"{dev['deviceType']} {dev_id}",
                )
            )

    if entities:                      # если нет подходящих устройств – сущности не создаём
        async_add_entities(entities)
