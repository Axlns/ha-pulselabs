"""Fake Pulse Labs cloud API for local testing."""

from __future__ import annotations
from typing import Any, Dict, List
from .api import BaseApi 

MOCK_USERS: List[Dict[str, Any]] = [
    {"userName": "GrowMaster", "role": "Owner"},
    {"userName": "Viewer‑1", "role": "Viewer"},
]

MOCK_ALL_DEVICES: Dict[str, Any] = {
    "deviceViewDtos": [
        {   # ───── Pulse One (deviceType = 0) ──────────────────────────────
            "id": 10001,
            "deviceType": 0,
            "name": "Seedling Tent",
            "mostRecentDataPoint": {
                "deviceId": 10001,
                "deviceType": 0,
                "temperatureF": 75.2,
                "humidityRh": 64.5,
                "vpd": 0.97,
                "lightLux": 12.4,           # → 12.4 %
                "airPressure": 100215.0,    # Pa
                "pluggedIn": False,
                "signalStrength": -55,
                "createdAt": "2025‑07‑18T06:55:50",
            },
        },
        {   # ───── Pulse Pro (deviceType = 1) ──────────────────────────────
            "id": 20002,
            "deviceType": 1,
            "name": "Flower Room",
            "mostRecentDataPoint": {
                "deviceId": 20002,
                "deviceType": 1,
                "temperatureF": 82.4,
                "humidityRh": 58.1,
                "vpd": 1.32,
                "lightLux": 95.7,           # %
                "airPressure": 98908.5,     # Pa
                "co2": 561,
                "par": 450,                 # µmol m‑2 s‑1
                "voc": 0.2,                 # ppm
                "pluggedIn": True,
                "signalStrength": -61,
                "createdAt": "2025‑07‑18T03:38:47",
            },
        },
        {   # ───── Pulse Zero (deviceType = 5) ─────────────────────────────
            "id": 30003,
            "deviceType": 5,
            "name": "Drying Cabinet",
            "mostRecentDataPoint": {
                "deviceId": 30003,
                "deviceType": 5,
                "temperatureF": 68.0,
                "humidityRh": 50.0,
                "vpd": 0.82,
                "lightLux": 0.0,
                "airPressure": 100012.0,
                "pluggedIn": True,
                "signalStrength": -48,
                "createdAt": "2025‑07‑18T07:10:10",
            },
        },
    ]
}


class MockPulseApi(BaseApi):
    """Drop‑in replacement for PulseApi that returns canned JSON."""

    def __init__(self, *_, **__) -> None:
        super().__init__()          # ← инициализируем datapoints_today
        # Таблица «путь → payload», будет менять тест
        self._responses: dict[str, object] = {
            "/users": MOCK_USERS,
            "/all-devices": MOCK_ALL_DEVICES,
        }

    async def async_get(self, path: str):
        # Если ответ переопределён в тесте — берём его
        if path in self._responses:
            payload = self._responses[path]
        elif path.startswith("/devices/") and path.endswith("/recent-data"):
            dev_id = int(path.split("/")[2])
            payload = next(
                (
                    dev["mostRecentDataPoint"]
                    for dev in MOCK_ALL_DEVICES["deviceViewDtos"]
                    if dev["id"] == dev_id
                ),
                None,
            )
            if payload is None:
                raise ValueError(f"Unknown device id {dev_id}")
        else:
            raise ValueError(f"Unhandled mock path {path}")

        # Учтём расход datapoints
        self._register_usage(path, payload)
        return payload
