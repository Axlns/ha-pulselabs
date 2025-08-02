"""
custom_components.pulselabs.api
--------------------------------
REST‑клиент Pulse API с централизованным учётом суточной квоты **datapoints**.

Алгоритм расхода:
* Загружаем `resources/swagger.json` при импорте.
* По Swagger‑схемам строим карту:  
  path‑regex → список «JSON‑пойнтеров» (типа `['deviceViewDtos', '*', 'mostRecentDataPoint']`), 
  указывающих, где в ответе находятся объекты из `_COUNTABLE_TYPES`.
* Каждый успешный `async_get()` вызывает `_register_datapoints()`,
  который берёт подходящий список путей и пересчитывает, сколько
  объектов фактически вернулось (для `*` — длина списка, иначе 1).
* Если ни одного объекта не найдено → расход 1 datapoint (правило API).

Обновлять счётчик приходится **до** возврата данных в вызывающий код,
чтобы Coordinator и сенсоры могли сразу показать актуальное значение.
"""

from __future__ import annotations

import os
import re
import json

from dataclasses import dataclass
from datetime import datetime
from importlib.resources import files
from typing import Any, Dict, List, Sequence, Callable

import asyncio
import aiohttp
import async_timeout

from homeassistant.util import dt as dt_util

from .const import BASE_URL, DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1) Константы

# DTO‑типы, которые *засчитываются* как расход квоты
_COUNTABLE_TYPES: set[str] = {
    "DataPointDto",
    "UniversalDataPointDto",
    "PublicApiDataPoint",
    "HubDataPointDto",
}

# Где лежит Pulse API swagger.json
_SWAGGER_PATH = f"custom_components.{DOMAIN}.resources.swagger.json"

@dataclass
class _PathPointers:
    regex: re.Pattern  # compiled ^/devices/[^/]+/recent-data$
    pointers: List[List[str]]  # [['deviceViewDtos', '*', 'mostRecentDataPoint'], ...]

# ---------------------------------------------------------------------------
# 2) Построение карты path → pointers по swagger
def _build_dp_schema_map() -> List[_PathPointers]:
    """Строит карту REST‑путь → JSON‑пойнтеры для DTO‑datapoint."""

    # ---------- helpers ----------
    def _load_swagger() -> Dict[str, Any]:
        return json.loads(files("custom_components.pulselabs.resources").joinpath("swagger.json").read_text())

    def _schema_name(ref: str) -> str | None:
        return ref.split("/")[-1] if ref.startswith("#/components/schemas/") else None

    def _merge_composite(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Разворачивает allOf/oneOf/anyOf в плоский dict."""
        for key in ("allOf", "oneOf", "anyOf"):
            if key in schema:
                merged: Dict[str, Any] = {}
                for sub in schema[key]:
                    merged.update(_merge_composite(sub))
                return merged
        return schema

    def _traverse_schema(schema: Dict[str, Any], prefix: List[str], stack: List[str]) -> List[List[str]]:
        """Ищет пути до countable‑DTO.
        `stack` хранит имена `$ref`, встреченные в текущей цепочке, чтобы
        избегать локальных циклов, но не блокировать такие же схемы по
        другим путям.
        """
        found: List[List[str]] = []
        schema = _merge_composite(schema)

        # --- $ref ---
        if "$ref" in schema:
            ref_name = _schema_name(schema["$ref"])
            if not ref_name:
                return found
            if ref_name in stack:  # цикл A→B→A
                return found

            if ref_name in _COUNTABLE_TYPES:
                found.append(prefix.copy())
                # продолжаем обход, чтобы захватить дочерние массивы, если есть
            # рекурсивно раскрываем, передавая обновлённый стек
            resolved = components.get(ref_name, {})
            if resolved:
                found.extend(_traverse_schema(resolved, prefix, stack + [ref_name]))
            return found

        stype = schema.get("type")

        # объект‑контейнер
        if stype == "object":
            for prop, subschema in (schema.get("properties") or {}).items():
                found.extend(_traverse_schema(subschema, prefix + [prop], stack))
            return found

        # массив
        if stype == "array":
            found.extend(_traverse_schema(schema.get("items", {}), prefix + ["*"], stack))
        return found

    # ---------- основная логика ----------
    swagger = _load_swagger()
    components = swagger.get("components", {}).get("schemas", {})
    paths_obj = swagger.get("paths", {})

    result: List[_PathPointers] = []
    for raw_path, methods in paths_obj.items():
        get_def = methods.get("get")
        if not get_def:
            continue

        resp_block = get_def.get("responses", {}).get("200", {})
        content = resp_block.get("content")
        if content:
            resp_schema = next(iter(content.values())).get("schema", {})
        else:
            resp_schema = resp_block.get("schema", {})
        if not resp_schema:
            continue

        pointers = _traverse_schema(resp_schema, [], stack=[])
        if not pointers:
            continue

        regex = re.compile("^" + re.sub(r"{[^/]+}", "[^/]+", raw_path) + "$")
        result.append(_PathPointers(regex=regex, pointers=pointers))

    return result

_DP_SCHEMA_MAP: List[_PathPointers] = _build_dp_schema_map()

_LOGGER.debug(_DP_SCHEMA_MAP)

# ---------------------------------------------------------------------------
# 3) Счётчик datapoint‑ов по payload & pointers
def _count_by_pointers(payload: Any, pointers: Sequence[Sequence[str]]) -> int:
    """Считает datapoints, обходя payload только по интересующим путям."""

    def _count_for_ptr(node: Any, ptr: Sequence[str]) -> int:
        if not ptr:
            # оказались на объекте, который swagger пометил как countable
            if isinstance(node, list):
                return len(node)
            return 1 if node is not None else 0

        key, *rest = ptr
        if key == "*":
            if not isinstance(node, list):
                return 0
            return sum(_count_for_ptr(child, rest) for child in node)
        if isinstance(node, dict) and key in node:
            return _count_for_ptr(node[key], rest)
        return 0

    return sum(_count_for_ptr(payload, ptr) for ptr in pointers)

# ---------------------------------------------------------------------------
# 4) Базовый API‑клиент
class BaseApi:
    """Общие helper‑методы **и централизованный счётчик datapoints**.

    Наследники обязаны переопределить `async_get()`, но **должны**
    вызывать `self._register_datapoints(path, payload)` перед возвратом
    ответа, чтобы корректно учитывать расход суточной квоты.
    """

    def __init__(self) -> None:
        self.datapoints_today = 0
        self._last_call_datetime = dt_util.now()
        self._last_call_success: bool = False

        self._on_usage_update: Callable[[], None] | None = None

    def set_usage_state(self, used: int, last_call_datetime: str):
        self.datapoints_today = used
        self._last_call_datetime = dt_util.parse_datetime(last_call_datetime) or dt_util.now()


    def set_usage_update_callback(self, callback: Callable[[], None]):
        self._on_usage_update = callback

    # ---------------- internal helpers

    def _reset_usage_if_new_day(self) -> None:
        now = dt_util.now()
        today = now.date()
        if today != self._last_call_datetime.date():
            self.datapoints_today = 0
            self._last_call_datetime = now

    def _increment_usage(self, amount: int) -> None:
        self._reset_usage_if_new_day()
        self.datapoints_today += max(amount, 1)
        self._last_call_datetime =  dt_util.now()
        if self._on_usage_update:
            self._on_usage_update()

    def _register_usage(self, path: str, payload: Any) -> None:
        """Определяет расход квоты по swagger‑карте. Если подходящего
        пути нет или ничего не найдено, засчитывает 1 datapoint.
        """
        plain_path = path.split("?")[0]
        total = 0
        for entry in _DP_SCHEMA_MAP:
            if entry.regex.match(plain_path):
                total = _count_by_pointers(payload, entry.pointers)
                break
        if total == 0:
            total = 1  # правило API: вызов без datapoints = 1
        self._increment_usage(total)

    # ---------------- public helpers (должны вызывать _register_dp)

    async def async_get(self, path: str):
        raise NotImplementedError

    async def async_get_users(self):
        return await self.async_get("/users")

    async def async_get_owner_name(self) -> str:
        users = await self.async_get_users()
        for u in users:
            if u.get("role") == "Owner":
                return u.get("userName")
        return users[0].get("userName", "PulseLabs") if users else "PulseLabs"

    async def async_get_all_devices(self):
        return await self.async_get("/all-devices")
        #return data.get("deviceViewDtos", []) if isinstance(data, dict) else data


    @property
    def last_call_success(self) -> bool:
        return self._last_call_success

# ---------------------------------------------------------------------------
# 5) Реальный REST‑клиент
class PulseApi(BaseApi):
    """Реальный REST‑клиент Pulse Labs."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        super().__init__()
        self._session = session
        self._api_key = api_key

    async def async_get(self, path: str):
        url = f"{BASE_URL}{path}"
        headers = {"x-api-key": self._api_key}
        try:
            async with async_timeout.timeout(15):
                async with self._session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    self._last_call_success = True
        except aiohttp.ClientError as err:
            _LOGGER.warning("Pulse API network error (%s): %s", path, err)
            self._last_call_success = False
            raise
        except asyncio.TimeoutError:
            _LOGGER.warning("Pulse API request timed out: %s", path)
            self._last_call_success = False
            raise
        except Exception:
            _LOGGER.exception("Unexpected error calling Pulse API on path %s", path)
            self._last_call_success = False
            raise

        # Учтём расход datapoints до возврата вызывающему коду
        self._register_usage(path, data)
        return data

# ---------------------------------------------------------------------------
# 6) Фабрика — возвращает real / mock
def get_api(session: aiohttp.ClientSession, api_key: str) -> BaseApi:
    from .mock_api import MockPulseApi  # локальный импорт, чтобы не ловить циклы

    if os.getenv("PULSE_API_MODE", "").lower() == "mock" or str(api_key).lower() == "mock":
        return MockPulseApi()           # наследник BaseApi
    return PulseApi(session, api_key)