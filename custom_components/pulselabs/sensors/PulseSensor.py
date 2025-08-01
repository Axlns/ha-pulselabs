from abc import ABC
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from ..const import DOMAIN, DEVICE_TYPE_MAP, MANUFACTURER

class PulseSensor(CoordinatorEntity, ABC):
    _attr_has_entity_name = True

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

        self._device_id = device_id
        self._data_key = data_key

        device = coordinator.data.get(device_id, {})
        device_type = device.get("deviceType", -1)

        self._attr_device_info = {
            "identifiers": {(DOMAIN, str(device_id))},
            "name": device.get("name", f"Device {device_id}"),
            "model": DEVICE_TYPE_MAP.get(device_type, f"Unknown model, device type: {device_type}"),
            "manufacturer": MANUFACTURER,
        }

        self._attr_unique_id = f"{device_id}_{data_key}"
        self._attr_device_class = device_class
        if translation_key is not None:
            self._attr_translation_key = translation_key
        if disabled_by_default:
            self._attr_entity_registry_enabled_default = False
        if icon:
            self._attr_icon = icon
            

