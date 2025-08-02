
from homeassistant.components.sensor import SensorEntity

from .ApiSensor import ApiSensor

class ApiRemainingSensor(ApiSensor, SensorEntity):
    _attr_translation_key = "api_usage_remaining"
    _attr_icon = "mdi:chart-line"
    _attr_native_unit_of_measurement = "dps"

    def __init__(self, coordinator, entry, limit: int, plan: str):
        super().__init__(coordinator, entry)
        self._limit = limit
        self._plan = plan
        self._attr_unique_id = f"{entry.entry_id}_api_remaining"

    @property
    def native_value(self):
        used = self.coordinator.api.datapoints_today
        return max(0, self._limit - used)

    @property
    def extra_state_attributes(self):
        return {
            "limit": self._limit,
            "plan": self._plan,
        }