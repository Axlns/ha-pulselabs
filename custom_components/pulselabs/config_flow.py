"""Config flow for the Pulse Labs integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol
import aiohttp

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_DEVICES
from .api import get_api

import logging
_LOGGER = logging.getLogger(__name__)

STEP_PLAN_SCHEMA = vol.Schema({
    vol.Required("plan", default="hobbyist"): selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                {"value": "hobbyist", "label": "Hobbyist (4,800/day)"},
                {"value": "enthusiast", "label": "Enthusiast (24,000/day)"},
                {"value": "professional", "label": "Professional (120,000/day)"},
            ],
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )
})

class PulseLabsConfigFlow(ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for Pulse Labs."""
    VERSION = 2

    _api_key: str

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:  # noqa: D401
        errors: dict[str, str] = {}

        if user_input is not None:
            self._api_key = user_input[CONF_API_KEY].strip()

            session = async_get_clientsession(self.hass)
            api = get_api(session, self._api_key)

            try:
                # 1️⃣ Сначала имя владельца из /users
                title = await api.async_get_owner_name()

                # 2️⃣ Потом список устройств
                devices = await api.async_get_all_devices()
                if not devices:
                    raise CannotConnect("no devices")

            except aiohttp.ClientError as exc:
                _LOGGER.debug("API error: %s", exc, exc_info=True)
                errors["base"] = "cannot_connect"
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.debug("Unexpected error: %s", exc, exc_info=True)
                errors["base"] = "unknown"
            
            if not errors:
                await self.async_set_unique_id(title.lower())  # 1‑интеграция на аккаунт
                self._abort_if_unique_id_configured()

                self._title = title
                self._devices = devices
                self._api_key = self._api_key
                return await self.async_step_plan()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_plan(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            return self.async_show_form(
                    step_id="plan",
                    data_schema=STEP_PLAN_SCHEMA,
                )

        return self.async_create_entry(
            title=self._title,
            data={
                CONF_API_KEY: self._api_key,
                CONF_DEVICES: self._devices,
            },
            options={
                "plan": user_input["plan"],
            },
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
