"""Sets up the sensors for the Brisbane Bin Day service."""

from __future__ import annotations

#import logging

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .data import BccApiData
from .coordinator import BccApiDataUpdateCoordinator


@dataclass(frozen=True)
class BinDaySensorEntityDescription(SensorEntityDescription):
    """Describes a Solar Forecast Sensor."""
    state: Callable[[BccApiData], Any] | None = None


# pylint: disable=unexpected-keyword-arg
SENSORS: tuple[BinDaySensorEntityDescription, ...] = (
    BinDaySensorEntityDescription(
        key="property_number",
        translation_key="property_number",
        state=lambda data: data.property_number,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="suburb",
        translation_key="suburb",
        state=lambda data: data.suburb,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="street",
        translation_key="street",
        state=lambda data: data.street_name,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="house_number",
        translation_key="house_number",
        state=lambda data: data.house_number,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="collection_day",
        translation_key="collection_day",
        state=lambda data: data.collection_day,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="collection_zone",
        translation_key="collection_zone",
        state=lambda data: data.collection_zone,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="alert_hours",
        translation_key="alert_hours",
        state=lambda data: data.alert_hours,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="green_bin",
        translation_key="green_bin",
        state=lambda data: data.green_bin,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="polling_interval_hours",
        translation_key="polling_interval_hours",
        state=lambda data: data.polling_interval_hours,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    BinDaySensorEntityDescription(
        key="next_collection_date",
        translation_key="next_collection_date",
        state=lambda data: data.next_collection_date(),
    ),
    BinDaySensorEntityDescription(
        key="due_in_hours",
        translation_key="due_in_hours",
        state=lambda data: data.due_in_hours(),
    ),
    BinDaySensorEntityDescription(
        key="extra_bin_text",
        translation_key="extra_bin_test",
        state=lambda data: data.extra_bin_text(),
    ),
    BinDaySensorEntityDescription(
        key="is_recycling_week",
        translation_key="is_recycling_week",
        state=lambda data: data.is_recycling_week(),
    ),
    BinDaySensorEntityDescription(
        key="is_green_waste_week",
        translation_key="is_green_waste_week",
        state=lambda data: data.is_green_waste_week(),
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback
) -> None:
    """Defer sensor setup to the shared sensor module."""
    coordinator: BccApiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        BinDaySensorEntity(
            entry_id=entry.entry_id,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSORS
    )


class BinDaySensorEntity(CoordinatorEntity[BccApiDataUpdateCoordinator], SensorEntity):
    """Defines a bin day sensor."""

    entity_description: BinDaySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        entry_id: str,
        coordinator: BccApiDataUpdateCoordinator,
        entity_description: BinDaySensorEntityDescription,
    ) -> None:
        """Initialize bin day sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self.entity_id = f"{SENSOR_DOMAIN}.{entity_description.key}"
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            name="Brisbane bin day",
        )

    async def _update_callback(self, _now: datetime) -> None:
        """Update the entity without fetching data from server."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()

        # Update the state of the sensor every minute without
        # fetching new data from the server.
        async_track_utc_time_change(
            self.hass,
            self._update_callback,
            second=0,
        )

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        return self.entity_description.state(self.coordinator.data)
