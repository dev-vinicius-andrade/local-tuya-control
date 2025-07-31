"""
Tuya Local Control integration for Home Assistant.
"""
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.components import persistent_notification

from .const import DOMAIN, CONF_DEVICES
from .controller import TuyaLocalController

_LOGGER = logging.getLogger(__name__)

DEVICE_SCHEMA = vol.Schema({
    vol.Required('name'): cv.string,
    vol.Required('device_id'): cv.string,
    vol.Required('ip'): cv.string,
    vol.Required('local_key'): cv.string,
    vol.Optional('version', default=3.5): vol.Coerce(float),
    vol.Required('entities'): vol.All(
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
        
        _LOGGER.debug(f"set_device_value called with device_id={device_id}, dp={dp}, value={value}")
        _LOGGER.debug(f"Available devices in hass.data[DOMAIN]: {list(hass.data[DOMAIN].keys())}")
        
        device_found = False
        
        # Search through all data in the domain
        for key, device_data in hass.data[DOMAIN].items():
            if isinstance(device_data, dict):
                # Check if it's a device config with matching device_id
                if device_data.get("device_id") == device_id:
                    device_found = True
                    _LOGGER.debug(f"Found device with ID {device_id}")
                    controller = TuyaLocalController(device_data)
                    try:
                        result = await hass.async_add_executor_job(
                            controller.device.set_status, dp, value
                        )
                        _LOGGER.info(f"Set value result for device {device_id}, dp={dp}, value={value}: {result}")
                        
                        # Create a persistent notification to show the result
                        message = f"DP {dp} set to {value}\nResult: {result}"
                        persistent_notification.create(
                            hass,
                            message,
                            title=f"Tuya Device Update: {device_id}",
                            notification_id=f"tuya_set_{device_id}_{dp}"
                        )
                        return
                    except Exception as e:
                        _LOGGER.error(f"Error setting value for device {device_id}: {e}", exc_info=True)
                        return
        
        if not device_found:
            _LOGGER.error(f"Device with ID {device_id} not found in any configuration")
    
    async def get_device_status(call: ServiceCall) -> None:
        """Service to get the full status of a device."""
        device_id = call.data.get("device_id")
        
        _LOGGER.debug(f"get_device_status called with device_id={device_id}")
        _LOGGER.debug(f"Available devices in hass.data[DOMAIN]: {list(hass.data[DOMAIN].keys())}")
        
        device_found = False
        
        # Search through all data in the domain
        for key, device_data in hass.data[DOMAIN].items():
            if isinstance(device_data, dict):
                # Check if it's a device config with matching device_id
                if device_data.get("device_id") == device_id:
                    device_found = True
                    _LOGGER.debug(f"Found device with ID {device_id}")
                    controller = TuyaLocalController(device_data)
                    try:
                        status = await hass.async_add_executor_job(controller.get_status)
                        _LOGGER.info(f"Status for device {device_id}: {status}")
                        
                        # Create a persistent notification to show the status
                        if status and "dps" in status:
                            message = f"Device Status for {device_id}:\n"
                            for dp, val in status["dps"].items():
                                message += f"DP {dp}: {val}\n"
                            
                            persistent_notification.create(
                                hass,
                                message,
                                title=f"Tuya Device Status: {device_id}",
                                notification_id=f"tuya_status_{device_id}"
                            )
                        return
                    except Exception as e:
                        _LOGGER.error(f"Error getting status for device {device_id}: {e}", exc_info=True)
                        return
        
        if not device_found:
            _LOGGER.error(f"Device with ID {device_id} not found in any configuration")
    
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
            hass.config_entries.async_forward_entry_setups(entry, [component])
        )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    components = ["switch", "number", "light", "sensor", "fan"]
    unload_ok = await hass.config_entries.async_unload_platforms(entry, components)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok
