from homeassistant.config_entries import ConfigEntry
from .PulseDataSensor import PulseDataSensor
from ..const import SENSOR_TYPE_MAP, DeviceType, DEVICE_TYPE_MAP, SensorType


class PulseHubConnectedSensor(PulseDataSensor):
    """Сенсор, физически подключённый к хабу (universalSensorView)."""

    def __init__(self, coordinator, entry, sensor, description):
        self._device_id=str(sensor["hubId"])
        self._device_name=sensor.get("hubName") or f"Hub { self._device_id}"
        self._section = "sensors"
        self._data_key = description.key

        super().__init__(coordinator, entry, description)

        self._sensor_name = sensor.get("name", f"Sensor: {sensor["id"]}")
        self._sensor_type_name = SENSOR_TYPE_MAP.get(SensorType.parse(sensor.get("type")))
        self._sensor_value_name = sensor.get("valueName")
        # не используем translation_key для определения названия сенсора - выставляем напрямую, т.к. хотим использовать тип сенсора в имени + valueName
        self._attr_has_entity_name = False
        self._attr_name=f"{self._sensor_type_name}: {sensor.get("valueName")}"

    def _get_unique_id(self, entry: ConfigEntry) -> str:
        return f"{entry.entry_id}_hub_{self._device_id}_{self._data_key}"

    def _get_device_identifier(self, entry: ConfigEntry) -> str:
        return f"{entry.entry_id}_hub_{self._device_id}"

    def _get_device_name(self, entry: ConfigEntry) -> str:
        return self._device_name

    def _get_device_model(self, entry: ConfigEntry) -> str:
        return DEVICE_TYPE_MAP.get(DeviceType.Hub)

    @property
    def native_value(self):
        device_data = self.coordinator.data.get(self._section, {}).get(self._data_key, {})
        val = device_data.get("value")
        return round(val, 2) if isinstance(val, float) else val

    @property
    def extra_state_attributes(self):
        return {
            "name": self._sensor_name,
            "type": self._sensor_type_name,
            "property": self._sensor_value_name
        }

    