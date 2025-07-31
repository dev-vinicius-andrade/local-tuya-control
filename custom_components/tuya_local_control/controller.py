"""Controller for Tuya devices."""
import logging

import tinytuya

_LOGGER = logging.getLogger(__name__)

class TuyaLocalController:
    """Controller for Tuya devices."""

    def __init__(self, device_config):
        """Initialize a Tuya device controller with the provided configuration."""
        self.config = device_config
        self.name = device_config.get('name')
        self.device_id = device_config.get('device_id')
        self.ip = device_config.get('ip')
        self.local_key = device_config.get('local_key')
        self.version = device_config.get('version', 3.5)
        self.entities = device_config.get('entities', [])
        
        # Initialize the device connection
        self.device = self._create_device()
        
    def _create_device(self):
        """Create and configure a tinytuya device."""
        _LOGGER.debug(f"Creating Tuya device with ID: {self.device_id}, IP: {self.ip}, version: {self.version}")
        device = tinytuya.OutletDevice(
            dev_id=self.device_id,
            address=self.ip,
            local_key=self.local_key
        )
        device.set_version(self.version)
        device.set_socketPersistent(True)
        device.set_socketTimeout(10.0)  # Increase timeout to 10 seconds for more reliable communication
        return device
    
    def set_value(self, entity_id, value):
        """Set a value for a specific entity using its DP."""
        entity = self._find_entity(entity_id)
        if not entity:
            _LOGGER.error(f"Entity with ID {entity_id} not found")
            return False
        
        set_dp = entity.get('set_dp')
        if not set_dp:
            _LOGGER.error(f"Entity {entity_id} does not have a set_dp configured")
            return False
        
        # Check if we need to translate the value
        values_map = entity.get('values', {})
        if values_map and value in values_map:
            value = values_map[value]
        
        # Handle min/max constraints for number type
        if entity.get('type') == 'number':
            min_val = entity.get('min', 0)
            max_val = entity.get('max', 100)
            if isinstance(value, (int, float)):
                value = max(min_val, min(max_val, value))
        
        # Check if this entity uses a specific protocol version
        entity_version = entity.get('version')
        
        # Send the command to the device
        try:
            # Create a new device instance if using a different protocol version
            if entity_version is not None and entity_version != self.version:
                _LOGGER.debug(f"Using entity-specific protocol version {entity_version} for {entity_id}")
                temp_device = tinytuya.OutletDevice(
                    dev_id=self.device_id,
                    address=self.ip,
                    local_key=self.local_key
                )
                temp_device.set_version(entity_version)
                response = temp_device.set_status(set_dp, value)
            else:
                response = self.device.set_status(set_dp, value)
            
            _LOGGER.debug(f"Set value response for {entity_id}: {response}")
            return response
        except Exception as e:
            _LOGGER.error(f"Error setting value for {entity_id}: {e}")
            return False
    
    def get_value(self, entity_id):
        """Get the current value for a specific entity using its DP."""
        entity = self._find_entity(entity_id)
        if not entity:
            _LOGGER.error(f"Entity with ID {entity_id} not found")
            return None
        
        get_dp = entity.get('get_dp')
        if not get_dp:
            _LOGGER.error(f"Entity {entity_id} does not have a get_dp configured")
            return None
        
        # Check if this entity uses a specific protocol version
        entity_version = entity.get('version')
        
        # Get the device status
        try:
            # Create a new device instance if using a different protocol version
            if entity_version is not None and entity_version != self.version:
                _LOGGER.debug(f"Using entity-specific protocol version {entity_version} for {entity_id}")
                temp_device = tinytuya.OutletDevice(
                    dev_id=self.device_id,
                    address=self.ip,
                    local_key=self.local_key
                )
                temp_device.set_version(entity_version)
                status = temp_device.status()
            else:
                status = self.device.status()
                
            if not status or 'dps' not in status:
                _LOGGER.error(f"Unable to get status for {self.name}")
                return None
            
            # Get the value from the device status
            raw_value = status['dps'].get(str(get_dp))
            
            # Translate the value if necessary
            values_map = entity.get('values', {})
            if values_map:
                for key, val in values_map.items():
                    if val == raw_value:
                        return key
            
            return raw_value
        except Exception as e:
            _LOGGER.error(f"Error getting value for {entity_id}: {e}")
            return None
    
    def get_status(self):
        """Get the complete status from the device."""
        try:
            _LOGGER.debug(f"Getting status for device {self.device_id} at IP {self.ip}")
            status = self.device.status()
            _LOGGER.debug(f"Raw status response: {status}")
            return status
        except Exception as e:
            _LOGGER.error(f"Error getting status for {self.name}: {e}")
            return None
    
    def _find_entity(self, entity_id):
        """Find an entity by its unique_id."""
        for entity in self.entities:
            if entity.get('unique_id') == entity_id:
                return entity
        return None
    
    def get_entities(self):
        """Return all entities for this device."""
        return self.entities
