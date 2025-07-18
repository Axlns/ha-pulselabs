import os
import aiohttp
import async_timeout
from .const import BASE_URL
# !!! не импортируем MockPulseApi здесь, чтобы избежать «цикличной» зависимости

class BaseApi:
    """Общие helper‑методы; наследники должны реализовать async_get()."""

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
        data = await self.async_get("/all-devices")
        return data.get("deviceViewDtos", []) if isinstance(data, dict) else data

# ------------------------------------------------------------------
class PulseApi(BaseApi):
    """Реальный REST‑клиент Pulse Labs."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str):
        self._session = session
        self._api_key = api_key

    async def async_get(self, path: str):
        url = f"{BASE_URL}{path}"
        headers = {"x-api-key": self._api_key}
        async with async_timeout.timeout(15):
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

# ------------------------------------------------------------------
# ФАБРИКА
def get_api(session: aiohttp.ClientSession, api_key: str) -> BaseApi:
    from .mock_api import MockPulseApi  # локальный импорт, чтобы не ловить циклы

    if os.getenv("PULSE_API_MODE", "").lower() == "mock" or str(api_key).lower() == "mock":
        return MockPulseApi()           # наследник BaseApi
    return PulseApi(session, api_key)

# удобный вызов PulseApi.get_api(...)
#PulseApi.get_api = staticmethod(get_api)