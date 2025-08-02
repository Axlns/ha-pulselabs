from __future__ import annotations

import math
import logging
from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from homeassistant.helpers.storage import Store

from .const import DOMAIN, DeviceType, slugify

_LOGGER = logging.getLogger(__name__)

# какие ключи надо брать из корневого deviceViewDto
COPY_DEVICE_KEYS = (
    "proLightReadingPreviewDto", "vpdLeafTempOffsetInF", "name", "id"
)

class PulseDeviceCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """
    Опрос единственный: GET /all-devices
    data → dict[device_id] = mostRecentDataPoint + метаданные прибора
    """

    def __init__(self, hass: HomeAssistant, api, entry: ConfigEntry) -> None:
        self.hass = hass
        self.api = api

        self._last_successful_data: dict[str, dict] | None = None
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_all_devices",
            update_interval=timedelta(seconds=60),
            config_entry=entry
        )

        self._api_usage_store = Store(hass, 1, f"{DOMAIN}_api_usage_{entry.entry_id}.json")

        self._api_usage_state = {
            "used": 0,
            "last_call_datetime": dt_util.now().isoformat()
        }

        self.api.set_usage_update_callback(self._persist_api_usage)

    

    @staticmethod
    def _calc_air_vpd(
        tF: float,
        rh: float
    ) -> float:
        """Расчёт VPD воздуха (кПа), научно корректный.
        VPD = esat_buck(T_air) * (1 - RH/100)"""
        import math

        tC = (tF - 32) * 5 / 9

        def esat_buck(tc: float) -> float:
            return 0.61121 * math.exp((17.502 * tc) / (tc + 240.97))

        vpd = esat_buck(tC) * (1 - rh / 100.0)
        return round(vpd, 3)

    @staticmethod
    def _calc_leaf_vpd(
        tF: float,
        rh: float,
        leaf_delta_F: float
    ) -> float:
        """Расчёт VPD листа (кПа), научно корректный.
        VPD = esat_buck(T_leaf) - esat_buck(T_air) * RH/100
        где T_leaf = T_air + ΔT_leaf (в °C)"""
        import math

        tC = (tF - 32) * 5 / 9
        leafC = tC + (leaf_delta_F * 5 / 9)

        def esat_buck(tc: float) -> float:
            # Buck 1981 формула насыщенного давления (в кПа)
            return 0.61121 * math.exp((17.502 * tc) / (tc + 240.97))

        vpd = esat_buck(leafC) - esat_buck(tC) * rh / 100.0
        return round(vpd, 3)

    @staticmethod
    def _calc_dew_point_f(tF: float, rh: float) -> float:
        """Расчёт точки росы (в °F) из температуры воздуха (°F) и RH (%)"""
        import math

        # Переводим в °C
        tC = (tF - 32) * 5 / 9
        a, b = 17.27, 237.7
        alpha = (a * tC) / (b + tC) + math.log(rh / 100.0)
        dpC = (b * alpha) / (a - alpha)
        dpF = dpC * 9 / 5 + 32
        return round(dpF, 2)

    @callback
    def _wrap_device(self, device: dict, mrd: dict) -> dict:
        """Объединяем device + mostRecentDataPoint в один плоский объект."""
        wrapped = dict(mrd) if mrd else {}

        # копируем интересующие поля из корневого объекта device
        for k in COPY_DEVICE_KEYS:
            if k in device:
                if isinstance(device[k], dict):
                    wrapped.update(device[k])
                else:
                    wrapped[k] = device[k]

        # рассчитываем VPD воздуха, если есть температура воздуха и влажность
        if {"temperatureF", "humidityRh"} <= wrapped.keys():
            wrapped["avpd_calculated"] = self._calc_air_vpd(
                wrapped["temperatureF"],
                wrapped["humidityRh"]
            )

            wrapped["dpF_calculated"] = self._calc_dew_point_f(
                wrapped["temperatureF"],
                wrapped["humidityRh"]
            )

        # вычисляем VPD листа – если есть температура воздуха, влажность и разница между температурой листа и воздуха
        if {"temperatureF", "humidityRh", "vpdLeafTempOffsetInF"} <= wrapped.keys():
            wrapped["lvpd_calculated"] = self._calc_leaf_vpd(
                wrapped["temperatureF"],
                wrapped["humidityRh"],
                wrapped["vpdLeafTempOffsetInF"]
            )

        # 4) убираем None, чтобы build_entities не создавал лишних сенсоров
        return {k: v for k, v in wrapped.items() if v is not None}

    @callback
    def _wrap_hub(self, hub: dict, mrd: dict) -> dict:
        wrapped = dict(mrd) if mrd else {}

        # поля, которые мы хотим копировать из hub
        for key in ("id", "name", "deviceType"):
            if key in hub:
                wrapped[key] = hub[key]

        return wrapped

    @callback
    def _wrap_sensor(self,  hub: dict | None , sensor: dict, dp_value: dict) -> dict:
        
        hub_id=hub["id"] if hub else "hub_unassigned"
        hub_name = (hub.get("name")) if hub else "Hub: Unassigned Sensors"
        result = {
            # Обязательные поля
            "id": sensor["id"],
            "hubId": hub_id,
            "hubName":  hub_name,
            "deviceType":sensor.get("deviceType"), #должно быть всегда DeviceType.Sensor
            "name": sensor.get("name"),
            "type": sensor.get("sensorType"),
            "valueName":  dp_value["ParamName"],
            "measuringUnit": dp_value.get("MeasuringUnit"),
            "value":dp_value.get("ParamValue")
        }

        return result

    async def _async_update_data(self) -> dict[str, dict]:
        """Запрашиваем /all-devices и возвращаем данные всех приборов."""
        _LOGGER.debug("Coordinator fetch  id=%s  at=%s", id(self), dt_util.utcnow().isoformat(timespec="seconds"))

        try:
            raw = await self.api.async_get_all_devices()
            _LOGGER.debug(f"raw:{raw}")
            
            # собираем устройства и их сенсоры (из deviceViewDtos)
            device_list = raw.get("deviceViewDtos", [])
            devices: dict[str, dict] = {}

            for dev in device_list:
                dev_id = str(dev["id"])
                mrd = dev.get("mostRecentDataPoint", {})
                devices[dev_id] = self._wrap_device(dev, mrd)

            # собираем хабы и встроенные в него сенсоры (из hubViewDtos)
            hub_list = raw.get("hubViewDtos", [])
            hubs: dict[str, dict] = {}

            for hub in hub_list:
                hub_id = str(hub["id"])
                mrd = hub.get("mostRecentDataPoint", {})
                hubs[hub_id] = self._wrap_hub(hub, mrd)

            # собираем сенсоры подключенные к хабам (из universalSensorViews)
            sensors = {}
            hub_map = {hub["id"]: hub for hub in raw.get("hubViewDtos", [])}

            for sensor in raw.get("universalSensorViews", []):
                mrd = sensor.get("mostRecentDataPoint", {})
                hub_id = sensor.get("hubId")
                hub = hub_map.get(hub_id)

                for value in mrd.get("dataPointValues", []):
                    param_name = value.get("ParamName")
                    slug = slugify(param_name)
                    sensor_id = sensor.get("id")
                    key = f"{sensor_id}_{slug}"

                    sensors[key] = self._wrap_sensor(hub, sensor, value)

            result = {
                "devices": devices,
                "hubs": hubs,
                "sensors": sensors
            }

            _LOGGER.debug(f"result:{result}")

            self._last_successful_data = result
            return result

        except Exception as err:
            self.logger.warning("API fetch failed: %s", err)
            if self._last_successful_data is not None:
                self.logger.debug("Using cached data from previous update.")
                return self._last_successful_data
            raise UpdateFailed("Initial fetch failed and no cached data available") from err

    async def async_load_api_usage_state(self):
        saved = await self._api_usage_store.async_load()
        if saved:
            self._api_usage_state.update(saved)
            self.api.set_usage_state(
                used=saved.get("used", 0),
                last_call_datetime=saved.get("last_call_datetime")
            )

    def _persist_api_usage(self):
        self._api_usage_state["used"] = self.api.datapoints_today
        self._api_usage_state["last_call_datetime"] = self.api._last_call_datetime.isoformat()
        self.hass.async_create_task(self._api_usage_store.async_save(self._api_usage_state))
        