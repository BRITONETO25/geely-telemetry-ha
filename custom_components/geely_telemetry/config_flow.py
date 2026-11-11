"""Config flow for the Geely telemetry endpoint."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback

from .api import TelemetryConnectionError, async_fetch_telemetry
from .const import DOMAIN


class GeelyTelemetryConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure a local Geely head-unit telemetry endpoint."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            mode = user_input.get("mode", "local")
            if mode == "push":
                await self.async_set_unique_id("external-push")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Geely — Telemetria pela internet",
                    data={"mode": "push"},
                )
            return await self.async_step_local()

        schema = vol.Schema(
            {
                vol.Required("mode", default="local"): vol.In(
                    {"local": "Rede local", "push": "App do carro pela internet"}
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_local(self, user_input=None):
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()
            try:
                await async_fetch_telemetry(host, port)
            except TelemetryConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title="Geely — Telemetria", data={CONF_HOST: host, CONF_PORT: port}
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="192.168.7.36"): str,
                vol.Required(CONF_PORT, default=47800): vol.All(
                    int, vol.Range(min=1, max=65535)
                ),
            }
        )
        return self.async_show_form(step_id="local", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GeelyTelemetryOptionsFlow(config_entry)


class GeelyTelemetryOptionsFlow(config_entries.OptionsFlow):
    """Configure the polling interval."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = vol.Schema(
            {
                vol.Required(
                    "scan_interval",
                    default=self.config_entry.options.get("scan_interval", 5),
                ): vol.All(int, vol.Range(min=5, max=900)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
