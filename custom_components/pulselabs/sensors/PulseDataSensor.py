from homeassistant.components.sensor import SensorEntity

from .PulseSensor import PulseSensor


class PulseDataSensor(PulseSensor, SensorEntity):
    """Обычный сенсор данных Pulse (температура, влажность, CO₂ и т.д.)."""

    @property
    def native_value(self):
        device_data = self.coordinator.data.get("devices", {}).get(self.device_id, {})
        val = device_data.get(self._data_key)
        return round(val, 2) if isinstance(val, float) else val
