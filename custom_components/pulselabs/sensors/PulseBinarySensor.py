from homeassistant.components.binary_sensor import BinarySensorEntity

from .PulseSensor import PulseSensor

class PulseBinarySensor(PulseSensor, BinarySensorEntity):
    """Бинарный сенсор Pulse (например, Plugged In)."""

    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator, entry, description)

    @property
    def is_on(self):
        device_data = self.coordinator.data.get(self._section, {}).get(self._device_id, {})
        return bool(device_data.get(self._data_key))