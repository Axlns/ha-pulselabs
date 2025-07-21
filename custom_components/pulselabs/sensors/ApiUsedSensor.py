from homeassistant.components.sensor import SensorEntity

from .ApiSensor import ApiSensor

class ApiUsedSensor(ApiSensor, SensorEntity):
    _attr_translation_key = "api_usage_today"
    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = "dps"

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator, entry_id)
        self._attr_unique_id = f"{entry_id}_api_used"
        
    @property
    def native_value(self):
        return self.coordinator.api.datapoints_today