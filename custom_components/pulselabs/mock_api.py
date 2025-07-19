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

    def __init__(self, *args, **kwargs) -> None:
        pass  # api_key и session не нужны

    async def async_get(self, path: str):
        if path == "/users":
            return MOCK_USERS
        if path == "/all-devices":
            return MOCK_ALL_DEVICES
        if path.startswith("/devices/") and path.endswith("/recent-data"):
            dev_id = int(path.split("/")[2])
            for dev in MOCK_ALL_DEVICES["deviceViewDtos"]:
                if dev["id"] == dev_id:
                    return dev["mostRecentDataPoint"]
            raise ValueError(f"Unknown device id {dev_id}")
        raise ValueError(f"Unhandled mock path {path}")
