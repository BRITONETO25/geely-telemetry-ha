"""Sensors provided by the Geely telemetry endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfElectricPotential, UnitOfEnergy, UnitOfPower, UnitOfSpeed, UnitOfTemperature, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass(frozen=True, kw_only=True)
class GeelySensorDescription(SensorEntityDescription):
    """Sensor description with the telemetry object and field name."""

    source: str = "live"
    field: str = ""


def _sensor(
    source: str,
    field: str,
    name: str,
    unit: str | None = None,
    device_class: SensorDeviceClass | None = None,
    state_class: SensorStateClass | None = None,
    category: EntityCategory | None = None,
    icon: str | None = None,
) -> GeelySensorDescription:
    return GeelySensorDescription(
        key=field,
        name=name,
        source=source,
        field=field,
        native_unit_of_measurement=unit,
        device_class=device_class,
        state_class=state_class,
        entity_category=category,
        icon=icon,
    )


LIVE_SENSORS = (
    _sensor("live", "speed", "Velocidade", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT),
    _sensor("live", "gearLabel", "Marcha"),
    _sensor("live", "soc", "Bateria de tração", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    _sensor("live", "range", "Autonomia", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT),
    _sensor("live", "odo", "Odômetro", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.TOTAL_INCREASING),
    _sensor("live", "outTemp", "Temperatura externa", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    _sensor("live", "tripAKm", "Viagem A distância", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT),
    _sensor("live", "tripAAvgKmh", "Viagem A velocidade média", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT),
    _sensor("live", "tripBKm", "Viagem B distância", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT),
    _sensor("live", "tripBAvgKmh", "Viagem B velocidade média", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT),
)

TRIP_SENSORS = (
    _sensor("trip", "durationS", "Última viagem duração", "s", state_class=SensorStateClass.MEASUREMENT),
    _sensor("trip", "distanceKm", "Última viagem distância", UnitOfLength.KILOMETERS, SensorDeviceClass.DISTANCE, SensorStateClass.MEASUREMENT),
    _sensor("trip", "kwhUsed", "Última viagem energia consumida", UnitOfEnergy.KILO_WATT_HOUR),
    _sensor("trip", "kwhRegen", "Última viagem energia regenerada", UnitOfEnergy.KILO_WATT_HOUR),
    _sensor("trip", "avgSpeedKmh", "Última viagem velocidade média", UnitOfSpeed.KILOMETERS_PER_HOUR, SensorDeviceClass.SPEED, SensorStateClass.MEASUREMENT),
    _sensor("trip", "avgConsKwh100", "Última viagem consumo médio", "kWh/100 km", state_class=SensorStateClass.MEASUREMENT),
    _sensor("trip", "socStart", "Última viagem bateria inicial", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    _sensor("trip", "socEnd", "Última viagem bateria final", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
)

CHARGE_SENSORS = (
    _sensor("charge", "durationS", "Última recarga duração", "s", state_class=SensorStateClass.MEASUREMENT),
    _sensor("charge", "socStart", "Última recarga bateria inicial", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    _sensor("charge", "socEnd", "Última recarga bateria final", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
)

DETAIL_SENSORS = (
    _sensor("trip_details", "available", "Dados completos da última viagem", icon="mdi:map-marker-path"),
    _sensor("charge_details", "available", "Dados completos da última recarga", icon="mdi:ev-station"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    descriptions = (*LIVE_SENSORS, *TRIP_SENSORS, *CHARGE_SENSORS, *DETAIL_SENSORS)
    async_add_entities(
        GeelyTelemetrySensor(coordinator, entry, description)
        for description in descriptions
    )


class GeelyTelemetrySensor(CoordinatorEntity, SensorEntity):
    """Sensor entity backed by one field or a complete raw-data snapshot."""

    entity_description: GeelySensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, description: GeelySensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.source}_{description.field}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="Geely — Telemetria",
            manufacturer="Geely / Ecarx",
            model="Central multimídia",
        )

    @property
    def native_value(self) -> Any:
        description = self.entity_description
        data = self.coordinator.data
        if description.source == "snapshot":
            return "online" if data.get("_connected") else "offline"
        if description.source == "trip_details":
            return "disponível" if data.get("trip") else None
        if description.source == "charge_details":
            return "disponível" if data.get("charge") else None
        return (data.get(description.source) or {}).get(description.field)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        source = self.entity_description.source
        data = self.coordinator.data
        if source == "snapshot":
            return dict(data.get("live") or {})
        if source == "trip_details":
            return dict(data.get("trip") or {})
        if source == "charge_details":
            return dict(data.get("charge") or {})
        return None
