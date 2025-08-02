from homeassistant.config_entries import ConfigEntry
from .PulseBinarySensor import PulseBinarySensor
from ..const import DeviceType, DEVICE_TYPE_MAP


class PulseHubBinarySensor(PulseBinarySensor):
    """Бинарный сенсор, встроенный в хаб Pulse Hub."""

    def __init__(self, coordinator, entry, device, description):
        
        self._section = "hubs"
        self._device_id = str(device["id"])
        self._data_key=description.key
        self._device_name=device.get("name") or f"Hub {self.device_id}"

        super().__init__(coordinator, entry, description)

    def _get_unique_id(self, entry: ConfigEntry) -> str:
        return f"{entry.entry_id}_hub_{self._device_id}_{self._data_key}"

    def _get_device_identifier(self, entry: ConfigEntry) -> str:
        return f"{entry.entry_id}_hub_{self._device_id}"

    def _get_device_name(self, entry: ConfigEntry) -> str:
        return self._device_name

    def _get_device_model(self, entry: ConfigEntry) -> str:
        return DEVICE_TYPE_MAP.get(DeviceType.Hub)