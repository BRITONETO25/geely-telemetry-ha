"""Binary telemetry sensors."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    async_add_entities(
        [
            GeelyBinarySensor(coordinator, entry, "_connected", "Conexão com o veículo"),
            GeelyBinarySensor(coordinator, entry, "charging", "Recarga ativa"),
        ]
    )


class GeelyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """One binary sensor from the live telemetry frame."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="Geely — Telemetria",
            manufacturer="Geely / Ecarx",
            model="Central multimídia",
        )

    @property
    def is_on(self) -> bool | None:
        if self._key == "_connected":
            return bool(self.coordinator.data.get("_connected"))
        value = self.coordinator.data["live"].get(self._key)
        return value if isinstance(value, bool) else None
