"""Switch platform for Tuya Local Control."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya Local Control switch platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in hass.data[DOMAIN].values():
        controller = TuyaLocalController(device_config)
        
        for entity_config in controller.get_entities():
            if entity_config.get('type') == 'switch':
                devices.append(TuyaLocalSwitch(controller, entity_config))
    
    async_add_entities(devices)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Tuya Local Control switch based on config_entry."""
    device_config = hass.data[DOMAIN].get(entry.entry_id)
    if not device_config:
        return
    
    controller = TuyaLocalController(device_config)
    devices = []
    
    for entity_config in controller.get_entities():
        if entity_config.get('type') == 'switch':
            devices.append(TuyaLocalSwitch(controller, entity_config))
    
    async_add_entities(devices)

class TuyaLocalSwitch(SwitchEntity):
    """Representation of a Tuya Local Control switch."""

    def __init__(self, controller, entity_config):
        """Initialize the switch."""
        self._controller = controller
        self._config = entity_config
        self._attr_name = entity_config.get('name')
        self._attr_unique_id = f"{controller.device_id}_{entity_config.get('unique_id')}"
        self._state = None
        
    @property
    def device_info(self):
        """Return device info for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._controller.device_id)},
            name=self._controller.name,
            manufacturer="Tuya",
            model=f"Tuya Local ({self._controller.device_id})",
        )
    
    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._state
    
    async def async_update(self):
        """Fetch state from the device."""
        value = await self.hass.async_add_executor_job(
            self._controller.get_value, self._config.get('unique_id')
        )
        
        if value in (True, 'on', 1):
            self._state = True
        else:
            self._state = False
    
    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), True
        )
        self._state = True
        self.async_write_ha_state()
    
    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), False
        )
        self._state = False
        self.async_write_ha_state()
