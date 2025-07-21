from abc import ABC

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import EntityCategory

from ..const import DOMAIN, MANUFACTURER

class ApiSensor(CoordinatorEntity, ABC):
    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)

        self._attr_device_info = {
            "identifiers":{(DOMAIN, f"api_usage_{entry_id}")},
            "name":"Pulse API",
            "manufacturer":MANUFACTURER,
            "entry_type":DeviceEntryType.SERVICE
        }