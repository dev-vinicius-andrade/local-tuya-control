"""Config flow for Tuya Local Control integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DEVICE_ID, CONF_LOCAL_KEY, CONF_IP, CONF_VERSION

_LOGGER = logging.getLogger(__name__)

class TuyaLocalControlFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Local Control."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate the input
            try:
                return self.async_create_entry(
                    title=user_input.get("name", "Tuya Device"),
                    data=user_input
                )
            except Exception as e:
                _LOGGER.error(f"Error adding Tuya device: {e}")
                errors["base"] = "unknown"
        
        # Show the form
        data_schema = vol.Schema({
            vol.Required("name"): str,
            vol.Required(CONF_DEVICE_ID): str,
            vol.Required(CONF_IP): str,
            vol.Required(CONF_LOCAL_KEY): str,
            vol.Optional(CONF_VERSION, default=3.5): float,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
    
    async def async_step_import(self, import_info=None) -> FlowResult:
        """Handle import from configuration.yaml."""
        return self.async_create_entry(
            title=import_info.get("name", "Imported Tuya Device"),
            data=import_info
        )
