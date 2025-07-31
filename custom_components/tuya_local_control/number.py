"""Number platform for Tuya Local Control."""
import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya Local Control number platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in hass.data[DOMAIN].values():
        controller = TuyaLocalController(device_config)
        
        for entity_config in controller.get_entities():
            if entity_config.get('type') == 'number':
                devices.append(TuyaLocalNumber(controller, entity_config))
    
    async_add_entities(devices)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Tuya Local Control number based on config_entry."""
    device_config = hass.data[DOMAIN].get(entry.entry_id)
    if not device_config:
        return
    
    controller = TuyaLocalController(device_config)
    devices = []
    
    for entity_config in controller.get_entities():
        if entity_config.get('type') == 'number':
            devices.append(TuyaLocalNumber(controller, entity_config))
    
    async_add_entities(devices)

class TuyaLocalNumber(NumberEntity):
    """Representation of a Tuya Local Control number."""

    def __init__(self, controller, entity_config):
        """Initialize the number."""
        self._controller = controller
        self._config = entity_config
        self._attr_name = entity_config.get('name')
        self._attr_unique_id = f"{controller.device_id}_{entity_config.get('unique_id')}"
        self._attr_native_min_value = entity_config.get('min', 0)
        self._attr_native_max_value = entity_config.get('max', 100)
        self._attr_native_step = entity_config.get('step', 1)
        self._attr_native_value = None
        
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
        
        if isinstance(value, (int, float)):
            self._attr_native_value = value
    
    async def async_set_native_value(self, value):
        """Set the value."""
        await self.hass.async_add_executor_job(
            self._controller.set_value, self._config.get('unique_id'), value
        )
        self._attr_native_value = value
        self.async_write_ha_state()
