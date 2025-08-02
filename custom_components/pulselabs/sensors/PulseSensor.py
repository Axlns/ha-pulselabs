from abc import ABC
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.entity import EntityCategory
from homeassistant.config_entries import ConfigEntry

from ..const import DOMAIN, DEVICE_TYPE_MAP, MANUFACTURER


class PulseSensor(CoordinatorEntity, ABC):
    """Базовый класс для всех Pulse-сенсоров (устройств и хабов)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, device_id: str, description: SensorEntityDescription) -> None:
        
        super().__init__(coordinator, device_id)

        self.device_id = device_id
        self._data_key = description.key
        self.entity_description = description

        # Попытка извлечь device_type из coordinator (если доступен)
        device_data = coordinator.data.get("devices", {}).get(self.device_id, {})
        device_type = device_data.get("deviceType", -1)
        name = device_data.get("name") or f"Device {self.device_id}"

        # Префикс: device_ или hub_
        if device_type == 2:
            identifier = f"{entry.entry_id}_hub_{self.device_id}"
        else:
            identifier = f"{entry.entry_id}_device_{self.device_id}"

        self._attr_unique_id = f"{identifier}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, identifier)},
            name=name,
            model=DEVICE_TYPE_MAP.get(device_type, f"Unknown model (type: {device_type})"),
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

        # Может отсутствовать — безопасно получить через getattr
        self._attr_suggested_display_precision = getattr(description, "suggested_display_precision", None)
