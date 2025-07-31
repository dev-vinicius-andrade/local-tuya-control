"""Sensor platform for Tuya Local Control."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Tuya Local Control sensor platform."""
    if discovery_info is None:
        return
    
    devices = []
    for device_config in hass.data[DOMAIN].values():
        controller = TuyaLocalController(device_config)
        
        for entity_config in controller.get_entities():
            if entity_config.get('type') == 'sensor':
                devices.append(TuyaLocalSensor(controller, entity_config))
    
    async_add_entities(devices)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up Tuya Local Control sensor based on config_entry."""
    device_config = hass.data[DOMAIN].get(entry.entry_id)
    if not device_config:
        return
    
    controller = TuyaLocalController(device_config)
    devices = []
    
    for entity_config in controller.get_entities():
        if entity_config.get('type') == 'sensor':
            devices.append(TuyaLocalSensor(controller, entity_config))
    
    async_add_entities(devices)

class TuyaLocalSensor(SensorEntity):
    """Representation of a Tuya Local Control sensor."""

    def __init__(self, controller, entity_config):
        """Initialize the sensor."""
        self._controller = controller
        self._config = entity_config
        self._attr_name = entity_config.get('name')
        self._attr_unique_id = f"{controller.device_id}_{entity_config.get('unique_id')}"
        self._attr_native_value = None
        
        # Set unit of measurement if provided
        if 'unit' in entity_config:
            self._attr_native_unit_of_measurement = entity_config.get('unit')
        
        # Set device class if provided
        if 'device_class' in entity_config:
            self._attr_device_class = entity_config.get('device_class')
        
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
        
        self._attr_native_value = value
