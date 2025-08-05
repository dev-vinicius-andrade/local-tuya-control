import logging
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
import tuya_helper

# Configure logging
logger = logging.getLogger("tuya-local-entities")

# Dictionary to store the configured devices
TUYA_DEVICES = {}

class TuyaDevice:
    """Represents a Tuya device with its connection parameters."""
    def __init__(self, name, device_id, local_key, device_ip, version=3.3):
        self.name = name
        self.device_id = device_id
        self.local_key = local_key
        self.device_ip = device_ip
        self.version = version
        self.status = None
        self.entities = []

    def update_status(self):
        """Update the device status."""
        try:
            self.status = tuya_helper.get_tuya_device_status(
                self.device_id, 
                self.local_key, 
                self.device_ip, 
                self.version
            )
            logger.info(f"Updated status for {self.name}: {self.status}")
            # Update all related entities
            for entity in self.entities:
                entity.update_state()
            return self.status
        except Exception as e:
            logger.error(f"Error updating status for {self.name}: {e}")
            return None

    def send_command(self, dp, value):
        """Send command to the device."""
        try:
            tuya_helper.send_tuya_command(
                self.device_id,
                self.local_key,
                self.device_ip,
                dp,
                value,
                self.version
            )
            logger.info(f"Sent command to {self.name}: dp={dp}, value={value}")
            # Update status after sending command
            self.update_status()
        except Exception as e:
            logger.error(f"Error sending command to {self.name}: {e}")


class TuyaEntity:
    """Base class for Tuya entities."""
    def __init__(self, device, entity_id, name, dp_id, icon=None):
        self.device = device
        self.entity_id = entity_id
        self.name = name
        self.dp_id = dp_id
        self.icon = icon
        self.device.entities.append(self)
        
    def update_state(self):
        """Update entity state from device status."""
        raise NotImplementedError("Subclasses must implement update_state method")


class TuyaSensor(TuyaEntity):
    """Sensor entity for Tuya devices."""
    def __init__(self, device, entity_id, name, dp_id, unit=None, icon=None):
        super().__init__(device, entity_id, name, dp_id, icon)
        self.unit = unit
        # Initialize the entity in Home Assistant
        self._create_entity()
        
    def _create_entity(self):
        """Create the entity in Home Assistant."""
        attributes = {
            "friendly_name": self.name,
            "device_id": self.device.device_id,
        }
        if self.icon:
            attributes["icon"] = self.icon
        if self.unit:
            attributes["unit_of_measurement"] = self.unit
            
        state_entity(self.entity_id, STATE_UNKNOWN, attributes)
        
    def update_state(self):
        """Update entity state from device status."""
        if not self.device.status or "dps" not in self.device.status:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            return
            
        if str(self.dp_id) in self.device.status["dps"]:
            value = self.device.status["dps"][str(self.dp_id)]
            set_state(self.entity_id, value)
            logger.info(f"Updated sensor {self.entity_id} to {value}")
        else:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            logger.warning(f"DP {self.dp_id} not found in status for {self.entity_id}")


class TuyaFanControl(TuyaEntity):
    """Fan control entity for Tuya devices."""
    def __init__(self, device, entity_id, name, dp_id, speed_levels=None, icon="mdi:fan"):
        super().__init__(device, entity_id, name, dp_id, icon)
        self.speed_levels = speed_levels or {1: "low", 2: "medium", 3: "high"}
        self.speed_values = {v: k for k, v in self.speed_levels.items()}
        # Initialize the entity in Home Assistant
        self._create_entity()
        
    def _create_entity(self):
        """Create the entity in Home Assistant."""
        attributes = {
            "friendly_name": self.name,
            "device_id": self.device.device_id,
            "icon": self.icon,
            "supported_features": 1,  # SUPPORT_SET_SPEED
            "speed_list": list(self.speed_values.keys()),
            "percentage": 0,
            "preset_mode": None,
            "preset_modes": list(self.speed_values.keys()),
        }
        
        state_entity(self.entity_id, "off", attributes)
        
    def update_state(self):
        """Update entity state from device status."""
        if not self.device.status or "dps" not in self.device.status:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            return
            
        dp_str = str(self.dp_id)
        if dp_str in self.device.status["dps"]:
            value = self.device.status["dps"][dp_str]
            
            if value == 0:
                state = "off"
                percentage = 0
                preset_mode = None
            else:
                state = "on"
                speed_name = self.speed_levels.get(value, "unknown")
                percentage = int((value / max(self.speed_levels.keys())) * 100)
                preset_mode = speed_name
                
            attributes = {
                "percentage": percentage,
                "preset_mode": preset_mode,
            }
            
            set_state(self.entity_id, state, attributes)
            logger.info(f"Updated fan {self.entity_id} to {state}, speed={preset_mode}")
        else:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            logger.warning(f"DP {self.dp_id} not found in status for {self.entity_id}")
    
    def set_speed(self, speed):
        """Set the fan speed."""
        if speed == "off":
            self.device.send_command(self.dp_id, 0)
            return
            
        if speed in self.speed_values:
            speed_value = self.speed_values[speed]
            self.device.send_command(self.dp_id, speed_value)
        else:
            logger.error(f"Invalid speed {speed} for {self.entity_id}")


class TuyaSwitch(TuyaEntity):
    """Switch entity for Tuya devices."""
    def __init__(self, device, entity_id, name, dp_id, icon="mdi:power-socket"):
        super().__init__(device, entity_id, name, dp_id, icon)
        # Initialize the entity in Home Assistant
        self._create_entity()
        
    def _create_entity(self):
        """Create the entity in Home Assistant."""
        attributes = {
            "friendly_name": self.name,
            "device_id": self.device.device_id,
            "icon": self.icon,
        }
        
        state_entity(self.entity_id, "off", attributes)
        
    def update_state(self):
        """Update entity state from device status."""
        if not self.device.status or "dps" not in self.device.status:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            return
            
        if str(self.dp_id) in self.device.status["dps"]:
            value = self.device.status["dps"][str(self.dp_id)]
            state = "on" if value else "off"
            set_state(self.entity_id, state)
            logger.info(f"Updated switch {self.entity_id} to {state}")
        else:
            set_state(self.entity_id, STATE_UNAVAILABLE)
            logger.warning(f"DP {self.dp_id} not found in status for {self.entity_id}")
    
    def turn_on(self):
        """Turn the switch on."""
        self.device.send_command(self.dp_id, True)
    
    def turn_off(self):
        """Turn the switch off."""
        self.device.send_command(self.dp_id, False)


# Function to register a new Tuya device
@service
def register_tuya_device(name, device_id, local_key, device_ip, version=3.3):
    """Register a Tuya device to be used with entities."""
    if name in TUYA_DEVICES:
        logger.info(f"Updating existing device {name}")
    else:
        logger.info(f"Registering new device {name}")
    
    device = TuyaDevice(name, device_id, local_key, device_ip, version)
    TUYA_DEVICES[name] = device
    
    # Initialize the device by getting its status
    device.update_status()
    return device


# Function to create a Tuya fan entity
@service
def create_tuya_fan(device_name, entity_id, name, dp_id, speed_levels=None, icon="mdi:fan"):
    """Create a fan entity for a Tuya device."""
    if device_name not in TUYA_DEVICES:
        logger.error(f"Device {device_name} not registered")
        return None
        
    device = TUYA_DEVICES[device_name]
    fan = TuyaFanControl(device, entity_id, name, dp_id, speed_levels, icon)
    
    # Register service to set fan speed
    @service(f"set_{entity_id}_speed")
    def set_fan_speed(speed):
        fan.set_speed(speed)
    
    return fan


# Function to create a Tuya switch entity
@service
def create_tuya_switch(device_name, entity_id, name, dp_id, icon="mdi:power-socket"):
    """Create a switch entity for a Tuya device."""
    if device_name not in TUYA_DEVICES:
        logger.error(f"Device {device_name} not registered")
        return None
        
    device = TUYA_DEVICES[device_name]
    switch = TuyaSwitch(device, entity_id, name, dp_id, icon)
    
    # Register services to control the switch
    @service(f"turn_on_{entity_id}")
    def turn_on_switch():
        switch.turn_on()
    
    @service(f"turn_off_{entity_id}")
    def turn_off_switch():
        switch.turn_off()
    
    return switch


# Function to create a Tuya sensor entity
@service
def create_tuya_sensor(device_name, entity_id, name, dp_id, unit=None, icon=None):
    """Create a sensor entity for a Tuya device."""
    if device_name not in TUYA_DEVICES:
        logger.error(f"Device {device_name} not registered")
        return None
        
    device = TUYA_DEVICES[device_name]
    sensor = TuyaSensor(device, entity_id, name, dp_id, unit, icon)
    return sensor


# Function to update all devices
@service
def update_all_tuya_devices():
    """Update all registered Tuya devices."""
    for name, device in TUYA_DEVICES.items():
        device.update_status()


# Function to update a specific device
@service
def update_tuya_device(device_name):
    """Update a specific Tuya device."""
    if device_name not in TUYA_DEVICES:
        logger.error(f"Device {device_name} not registered")
        return None
        
    device = TUYA_DEVICES[device_name]
    return device.update_status()


# Set up automatic updates every minute
@time_trigger("period(1min)")
def auto_update_devices():
    """Automatically update all devices every minute."""
    update_all_tuya_devices()
