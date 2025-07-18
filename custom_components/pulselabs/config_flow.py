"""Config flow for the Pulse Labs integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_DEVICES
from .api import get_api

_LOGGER = logging.getLogger(__name__)


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

                return self.async_create_entry(
                    title=title,
                    data={CONF_API_KEY: self._api_key, CONF_DEVICES: devices},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
