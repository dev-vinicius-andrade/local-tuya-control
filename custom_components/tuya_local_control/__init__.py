"""
Tuya Local Control integration for Home Assistant.
"""
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, CONF_DEVICES
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema({
    vol.Required('name'): cv.string,
    vol.Required('device_id'): cv.string,
    vol.Required('ip'): cv.string,
    vol.Required('local_key'): cv.string,
    vol.Optional('version', default=3.5): vol.Coerce(float),    vol.Required('entities'): vol.All(
        vol.Length(min=1),
        [vol.Schema({
            vol.Required('name'): cv.string,
            vol.Required('unique_id'): cv.string,
            vol.Required('type'): vol.In(['switch', 'number', 'light', 'sensor', 'fan']),
            vol.Required('set_dp'): vol.Coerce(int),
            vol.Required('get_dp'): vol.Coerce(int),
            vol.Optional('min'): vol.Coerce(float),
            vol.Optional('max'): vol.Coerce(float),
            vol.Optional('step'): vol.Coerce(float),
            vol.Optional('version'): vol.Coerce(float),
            vol.Optional('values'): vol.Schema({str: vol.Any(bool, int, float, str)})
        })]
    )
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_DEVICES): vol.All(
            vol.Length(min=1),
            [DEVICE_SCHEMA]
        )
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Tuya Local Control from configuration.yaml."""
    if DOMAIN not in config:
        return True
    
    hass.data.setdefault(DOMAIN, {})
    domain_config = config[DOMAIN]
    
    for device_config in domain_config[CONF_DEVICES]:
        hass.data[DOMAIN][device_config['name']] = device_config
    
    # Register services
    async def set_device_value(call: ServiceCall) -> None:
        """Service to set a value for a specific DP on a device."""
        device_id = call.data.get("device_id")
        dp = call.data.get("dp")
        value = call.data.get("value")
        
        # Find the device by ID
        for name, device_data in hass.data[DOMAIN].items():
            if isinstance(device_data, dict) and device_data.get("device_id") == device_id:
                controller = TuyaLocalController(device_data)
                await hass.async_add_executor_job(
                    controller.device.set_status, dp, value
                )
                return
        
        _LOGGER.error(f"Device with ID {device_id} not found")
    
    async def get_device_status(call: ServiceCall) -> None:
        """Service to get the full status of a device."""
        device_id = call.data.get("device_id")
        
        # Find the device by ID
        for name, device_data in hass.data[DOMAIN].items():
            if isinstance(device_data, dict) and device_data.get("device_id") == device_id:
                controller = TuyaLocalController(device_data)
                status = await hass.async_add_executor_job(controller.get_status)
                _LOGGER.info(f"Status for device {device_id}: {status}")
                return
        
        _LOGGER.error(f"Device with ID {device_id} not found")
    
    hass.services.async_register(
        DOMAIN, "set_device_value", set_device_value
    )
    
    hass.services.async_register(
        DOMAIN, "get_device_status", get_device_status
    )
    
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "import"}
        )
    )
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya Local Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Store the config entry data
    hass.data[DOMAIN][entry.entry_id] = entry.data
    
    # Forward setup to platforms
    for component in ["switch", "number", "light", "sensor", "fan"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    import asyncio
    
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in ["switch", "number", "light", "sensor", "fan"]
            ]
        )
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
