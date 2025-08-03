from homeassistant.components.sensor import SensorEntity

from .PulseSensor import PulseSensor


class PulseDataSensor(PulseSensor, SensorEntity):
    """Обычный сенсор данных Pulse (температура, влажность, CO₂ и т.д.)."""

    def __init__(self, coordinator, entry, description):
       super().__init__(coordinator, entry, description)
    
    @property
    def native_value(self):
        device_data = self.coordinator.data.get(self._section, {}).get(self._device_id, {})
        val = device_data.get(self._data_key)
        return round(val, 2) if isinstance(val, float) else val
