from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .PulseSensor import PulseSensor

from ..const import DOMAIN

class PulseBinarySensor(PulseSensor, BinarySensorEntity):

    def __init__(
        self,
        coordinator,
        device_id,
        data_key,
        translation_key=None,
        device_class=None,
        disabled_by_default=False,
        icon = None,
        entity_category=None,
    ):
        super().__init__(coordinator, device_id, data_key, translation_key=translation_key, device_class=device_class, disabled_by_default=disabled_by_default, icon=icon)
        self._attr_entity_category = entity_category
        
    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._device_id, {}).get(self._data_key))