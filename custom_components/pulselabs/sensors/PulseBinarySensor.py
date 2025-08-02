from homeassistant.components.binary_sensor import BinarySensorEntity

from .PulseSensor import PulseSensor


class PulseBinarySensor(PulseSensor, BinarySensorEntity):
    """Бинарный сенсор Pulse (например, Plugged In)."""

    @property
    def is_on(self):
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        return bool(device_data.get(self._data_key))