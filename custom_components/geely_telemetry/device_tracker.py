"""GPS location of the vehicle from the in-car app."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GeelyVehicleTracker(coordinator, entry)])


class GeelyVehicleTracker(CoordinatorEntity, TrackerEntity):
    """A map-compatible GPS tracker for the car."""

    _attr_has_entity_name = True
    _attr_name = "Localização do veículo"
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:car"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_vehicle_location"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="Geely — Telemetria",
            manufacturer="Geely / Ecarx",
            model="Central multimídia",
        )

    @property
    def latitude(self) -> float | None:
        value = (self.coordinator.data.get("live") or {}).get("latitude")
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def longitude(self) -> float | None:
        value = (self.coordinator.data.get("live") or {}).get("longitude")
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def location_accuracy(self) -> float | None:
        value = (self.coordinator.data.get("live") or {}).get("gpsAccuracyM")
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        live = self.coordinator.data.get("live") or {}
        return {
            key: live[key]
            for key in ("gpsTimestamp", "altitudeM", "bearingDeg")
            if key in live
        }
