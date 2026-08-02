"""Support for Google Maps battery sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import GMConfigEntry, GMDataUpdateCoordinator
from .helpers import CFG_UNIQUE_IDS, ConfigID, UniqueID, dev_ids


async def async_setup_entry(
    hass: HomeAssistant, entry: GMConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Google Maps battery sensors."""
    cid = ConfigID(entry.entry_id)
    coordinator = entry.runtime_data.coordinator
    unique_ids = hass.data[CFG_UNIQUE_IDS]

    # Find unique IDs for this config entry
    uids = frozenset(coordinator.data)
    sensor_uids = unique_ids.take(cid, uids)

    entities = [
        GoogleMapsBatterySensor(coordinator, uid)
        for uid in sensor_uids
    ]
    async_add_entities(entities)


class GoogleMapsBatterySensor(CoordinatorEntity[GMDataUpdateCoordinator], SensorEntity):
    """Google Maps Battery Sensor Entity."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True

    def __init__(self, coordinator: GMDataUpdateCoordinator, uid: UniqueID) -> None:
        """Initialize the battery sensor."""
        super().__init__(coordinator)
        self._uid = uid
        self._attr_unique_id = f"{uid}_battery"

        data = coordinator.data[uid]
        full_name = data.misc.full_name if data.misc else "Device"
        
        # Link sensor to the same parent device in Home Assistant
        self._attr_device_info = dr.DeviceInfo(
            identifiers=dev_ids(uid),
            name=f"Google Maps {full_name}",
            serial_number=uid,
        )

    @property
    def native_value(self) -> int | None:
        """Return the current battery percentage."""
        if (data := self.coordinator.data.get(self._uid)) and data.misc:
            return data.misc.battery_level
        return None
