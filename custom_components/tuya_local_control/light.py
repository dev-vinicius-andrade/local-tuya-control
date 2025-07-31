"""Light platform for Tuya Local Control."""
import logging
from typing import Any, Optional

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya Local Control light platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in hass.data[DOMAIN].values():
        controller = TuyaLocalController(device_config)
        
        for entity_config in controller.get_entities():
            if entity_config.get('type') == 'light':
                devices.append(TuyaLocalLight(controller, entity_config))
    
    async_add_entities(devices)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Tuya Local Control light based on config_entry."""
    device_config = hass.data[DOMAIN].get(entry.entry_id)
    if not device_config:
        return
    
    controller = TuyaLocalController(device_config)
    devices = []
    
    for entity_config in controller.get_entities():
        if entity_config.get('type') == 'light':
            devices.append(TuyaLocalLight(controller, entity_config))
    
    async_add_entities(devices)

class TuyaLocalLight(LightEntity):
    """Representation of a Tuya Local Control light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, controller, entity_config):
        """Initialize the light."""
        self._controller = controller
        self._config = entity_config
        self._attr_name = entity_config.get('name')
        self._attr_unique_id = f"{controller.device_id}_{entity_config.get('unique_id')}"
        self._attr_is_on = False
        self._attr_brightness = 255
        
        # Configure brightness settings
        self._brightness_min = entity_config.get('min', 1)
        self._brightness_max = entity_config.get('max', 255)
        
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
            if value in (0, False, 'off'):
                self._attr_is_on = False
            else:
                self._attr_is_on = True
                # If the value is a number and greater than 1, it might be a brightness level
                if isinstance(value, (int, float)) and value > 1:
                    # Scale the device brightness to Home Assistant's 0-255 range
                    self._attr_brightness = int(
                        (value - self._brightness_min) / 
                        (self._brightness_max - self._brightness_min) * 255
                    )
    
    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        if brightness is not None:
            # Scale Home Assistant's 0-255 brightness to the device's range
            device_brightness = int(
                self._brightness_min + 
                (brightness / 255) * (self._brightness_max - self._brightness_min)
            )
            
            await self.hass.async_add_executor_job(
                self._controller.set_value, 
                self._config.get('unique_id'), 
                device_brightness
            )
            
            self._attr_brightness = brightness
        else:
            # Just turn on without changing brightness
            # If we have a previous brightness value, use that
            if hasattr(self, '_attr_brightness') and self._attr_brightness:
                device_brightness = int(
                    self._brightness_min + 
                    (self._attr_brightness / 255) * (self._brightness_max - self._brightness_min)
                )
                await self.hass.async_add_executor_job(
                    self._controller.set_value, 
                    self._config.get('unique_id'), 
                    device_brightness
                )
            else:
                # Default to full brightness
                await self.hass.async_add_executor_job(
                    self._controller.set_value, 
                    self._config.get('unique_id'), 
                    self._brightness_max
                )
                self._attr_brightness = 255
        
        self._attr_is_on = True
        self.async_write_ha_state()
    
    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), 0
        )
        self._attr_is_on = False
        self.async_write_ha_state()
