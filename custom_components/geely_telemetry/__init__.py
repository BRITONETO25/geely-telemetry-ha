"""Home Assistant integration for local Geely telemetry polling."""

from __future__ import annotations

import logging
from datetime import timedelta
from aiohttp import web

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.core import callback
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import TelemetryConnectionError, async_fetch_telemetry
from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]


class OAuthClientView(HomeAssistantView):
    """Publish this integration's native-app redirect registration."""

    url = "/geely_telemetry/oauth-client"
    name = "geely_telemetry:oauth-client"
    requires_auth = False

    async def get(self, request):
        return web.Response(
            text="<!doctype html><html><head><link rel='redirect_uri' href='telemetriaauto://oauth'></head><body>Geely Telemetry Home Assistant authorization client</body></html>",
            content_type="text/html",
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a configured telemetry endpoint."""

    cache = Store(hass, 1, f"{DOMAIN}_{entry.entry_id}_last_data")
    last_data = await cache.async_load()
    if not isinstance(last_data, dict):
        last_data = {"live": {}, "trip": None, "charge": None}
    last_data["_connected"] = False
    if not hass.data.get(f"{DOMAIN}_oauth_view"):
        hass.http.register_view(OAuthClientView)
        hass.data[f"{DOMAIN}_oauth_view"] = True

    coordinator_box: list[DataUpdateCoordinator] = []

    @callback
    def handle_push(event) -> None:
        nonlocal last_data
        frame = event.data
        if not isinstance(frame, dict) or "speed" not in frame:
            return
        coordinator = coordinator_box[0] if coordinator_box else None
        previous = coordinator.data if coordinator is not None and coordinator.data else last_data
        merged = dict(previous) if isinstance(previous, dict) else {}
        merged.update({"live": frame, "_connected": True, "_last_push": hass.loop.time()})
        if isinstance(frame.get("trip"), dict):
            merged["trip"] = frame["trip"]
        if isinstance(frame.get("charge"), dict):
            merged["charge"] = frame["charge"]
        merged.setdefault("trip", None)
        merged.setdefault("charge", None)
        last_data = merged
        if coordinator is not None:
            coordinator.async_set_updated_data(merged)

    unsub_push = hass.bus.async_listen("geely_telemetry_frame", handle_push)
    async def async_update_data() -> dict:
        nonlocal last_data
        if entry.data.get("mode") == "push":
            if hass.loop.time() - last_data.get("_last_push", 0.0) >= 15:
                last_data["_connected"] = False
            return last_data
        if hass.loop.time() - last_data.get("_last_push", 0.0) < 15:
            return last_data
        try:
            data = await async_fetch_telemetry(entry.data["host"], entry.data["port"])
            data["_connected"] = True
            last_data = data
            await cache.async_save(data)
            return data
        except TelemetryConnectionError:
            # Keep the last successful frame in the coordinator. Raising
            # UpdateFailed would make every CoordinatorEntity unavailable.
            last_data["_connected"] = False
            return last_data

    coordinator = DataUpdateCoordinator(
        hass,
        logger=logging.getLogger(__name__),
        name="Geely telemetry",
        update_method=async_update_data,
        update_interval=timedelta(
            seconds=entry.options.get("scan_interval", 5)
        ),
    )
    coordinator_box.append(coordinator)
    entry.async_on_unload(unsub_push)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a telemetry entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when integration options change."""

    await hass.config_entries.async_reload(entry.entry_id)
