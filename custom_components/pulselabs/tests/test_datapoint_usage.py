# tests/test_datapoint_usage.py
"""Проверяем, что BaseApi правильно считает datapoints_today."""

import asyncio
import pytest

from custom_components.pulselabs.mock_api import MockPulseApi


# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def api():
    """Свежий экземпляр MockPulseApi для каждого теста."""
    return MockPulseApi()


def _set_response(api: MockPulseApi, path: str, payload):
    """Удобный шорткат для записи ответа внутрь mock‑клиента."""
    # MockPulseApi держит ответы в dict path → payload; у него нет проверки
    # метода, поэтому нам достаточно перезаписать ключ.
    api._responses[path] = payload   # pylint: disable=protected-access


# ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_all_devices_with_history(api):
    """
    /all‑devices:
        • 2 устройства
        • MRD + 3 точки lastHourData для каждого
    Ожидаем расход 2 × (1 + 3) = 8 datapoints.
    """
    payload = {
        "deviceViewDtos": [
            {
                "mostRecentDataPoint": {"dummy": 1},        # DataPointDto
                "lastHourData": [{}, {}, {}],               # 3 точки
            },
            {
                "mostRecentDataPoint": {"dummy": 2},
                "lastHourData": [{}, {}, {}],

            },
            {
                "mostRecentDataPoint": {"dummy": 3},
                "lastHourData": None,
            }
        ]
    }
    _set_response(api, "/all-devices", payload)

    await api.async_get("/all-devices")
    assert api.datapoints_today == 9


@pytest.mark.asyncio
async def test_devices_recent_data(api):
    """GET /devices/{id}/recent‑data:   1 PublicApiDataPoint  → +1."""
    payload = {"dummy": "PublicApiDataPoint"}
    _set_response(api, "/devices/xyz/recent-data", payload)

    await api.async_get("/devices/xyz/recent-data")
    assert api.datapoints_today == 1


@pytest.mark.asyncio
async def test_devices_data_range(api):
    """Массив из 5 PublicApiDataPoint → +5."""
    payload = [{} for _ in range(5)]
    _set_response(api, "/devices/xyz/data-range", payload)

    await api.async_get("/devices/xyz/data-range")
    assert api.datapoints_today == 5


@pytest.mark.asyncio
async def test_unknown_endpoint_fallback(api):
    """Любой путь вне карты должен засчитываться как 1 datapoint."""
    payload = {"not": "a datapoint"}
    _set_response(api, "/users", payload)

    await api.async_get("/users")
    assert api.datapoints_today == 1
