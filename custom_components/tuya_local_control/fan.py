"""Fan platform for Tuya Local Control."""
import logging
from typing import Any, Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util.percentage import (
    int_states_in_range,
    ranged_value_to_percentage,
    percentage_to_ranged_value,
)

from .const import DOMAIN
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya Local Control fan platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in hass.data[DOMAIN].values():
        controller = TuyaLocalController(device_config)
        
        for entity_config in controller.get_entities():
            if entity_config.get('type') == 'fan':
                devices.append(TuyaLocalFan(controller, entity_config))
    
    async_add_entities(devices)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Tuya Local Control fan based on config_entry."""
    device_config = hass.data[DOMAIN].get(entry.entry_id)
    if not device_config:
        return
    
    controller = TuyaLocalController(device_config)
    devices = []
    
    for entity_config in controller.get_entities():
        if entity_config.get('type') == 'fan':
            devices.append(TuyaLocalFan(controller, entity_config))
    
    async_add_entities(devices)

class TuyaLocalFan(FanEntity):
    """Representation of a Tuya Local Control fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED

    def __init__(self, controller, entity_config):
        """Initialize the fan."""
        self._controller = controller
        self._config = entity_config
        self._attr_name = entity_config.get('name')
        self._attr_unique_id = f"{controller.device_id}_{entity_config.get('unique_id')}"
        self._attr_is_on = False
        self._attr_percentage = 0
        
        # Configure speed settings based on min/max values
        self._speed_min = entity_config.get('min', 1)
        self._speed_max = entity_config.get('max', 3)
        self._speed_step = entity_config.get('step', 1)
        self._speed_range = (self._speed_min, self._speed_max)
        
        # Set speed list for compatibility
        self._attr_speed_count = int_states_in_range(self._speed_range)
        
    @property
    def device_info(self):
        """Return device info for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._controller.device_id)},
            name=self._controller.name,
            manufacturer="Tuya",
            model=f"Tuya Local ({self._controller.device_id})",
        )
    
    async def async_update(self):
        """Fetch state from the device."""
        value = await self.hass.async_add_executor_job(
            self._controller.get_value, self._config.get('unique_id')
        )
        
        if value is not None:
            if value == 0:
                self._attr_is_on = False
                self._attr_percentage = 0
            else:
                self._attr_is_on = True
                self._attr_percentage = ranged_value_to_percentage(
                    self._speed_range, value
                )
    
    async def async_turn_on(
        self, percentage: Optional[int] = None, preset_mode: Optional[str] = None, **kwargs
    ) -> None:
        """Turn on the fan."""
        if percentage is None:
            # Just turn on using the last known speed or default to 50%
            percentage = self._attr_percentage or 50
        
        await self.async_set_percentage(percentage)
    
    async def async_turn_off(self, **kwargs) -> None:
        """Turn the fan off."""
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), 0
        )
        self._attr_is_on = False
        self._attr_percentage = 0
        self.async_write_ha_state()
    
    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return
        
        # Convert percentage to the device's speed value
        speed_value = int(percentage_to_ranged_value(self._speed_range, percentage))
        
        # Ensure we're within the device's allowed range
        speed_value = max(self._speed_min, min(self._speed_max, speed_value))
        
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), speed_value
        )
        
        self._attr_is_on = True
        self._attr_percentage = percentage
        self.async_write_ha_state()
