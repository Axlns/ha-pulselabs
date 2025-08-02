from abc import ABC
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry

from ..const import DOMAIN, DEVICE_TYPE_MAP, MANUFACTURER


class PulseSensor(CoordinatorEntity, ABC):
    """Базовый класс для всех Pulse-сенсоров (устройств и хабов)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)

        self.entity_description = description

        self._attr_unique_id = self._get_unique_id(entry)

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._get_device_identifier(entry))},
            name=self._get_device_name(entry),
            model=self._get_device_model(entry),
            manufacturer=MANUFACTURER,
        )

        if description.device_class is not None:
            self._attr_device_class = description.device_class

        if description.translation_key is not None:
            self._attr_translation_key = description.translation_key

        if description.native_unit_of_measurement is not None:
            self._attr_native_unit_of_measurement = description.native_unit_of_measurement

        if description.icon is not None:
            self._attr_icon = description.icon

        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

        if description.suggested_display_precision is not None:
            self._attr_suggested_display_precision = description.suggested_display_precision

        if description.state_class is not None:
            self._attr_state_class = description.state_class

    def _get_unique_id(self, entry: ConfigEntry) -> str:
        """Возвращает уникальный ID сенсора. Переопределяется в наследниках."""
        raise NotImplementedError

    def _get_device_identifier(self, entry: ConfigEntry) -> str:
        """Возвращает строку идентификатора устройства. Переопределяется в наследниках."""
        raise NotImplementedError

    def _get_device_name(self, entry: ConfigEntry) -> str:
        """Возвращает название устройства. Переопределяется в наследниках."""
        raise NotImplementedError

    def _get_device_model(self, entry: ConfigEntry) -> str:
        """Возвращает модель устройства. Переопределяется в наследниках."""
        raise NotImplementedError

   
