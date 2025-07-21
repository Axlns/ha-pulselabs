from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .PulseSensor import PulseSensor

from ..const import DOMAIN

class PulseDataSensor(PulseSensor, SensorEntity):
    
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        device_id,
        data_key,
        translation_key=None,
        device_class=None,
        disabled_by_default=False,
        icon = None,
        unit=None,
        entity_category=None,
        suggested_display_precision=None
    ):
        super().__init__(coordinator, device_id, data_key, translation_key=translation_key, device_class=device_class, disabled_by_default=disabled_by_default, icon=icon)

        self._attr_native_unit_of_measurement = unit
        self._attr_entity_category = entity_category
        self._attr_suggested_display_precision=suggested_display_precision

    @property
    def native_value(self) -> Any:
        val = self.coordinator.data.get(self._device_id, {}).get(self._data_key)
        return round(val, 2) if isinstance(val, float) else val