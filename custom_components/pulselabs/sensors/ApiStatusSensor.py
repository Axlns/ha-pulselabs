from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

from .ApiSensor import ApiSensor

class ApiStatusSensor(ApiSensor, BinarySensorEntity):

    _attr_translation_key = "api_status"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_api_status"

    @property
    def is_on(self) -> bool:
        return self.coordinator.api.last_call_success

    @property
    def available(self) -> bool:
        return True
