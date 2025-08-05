import tuya_entities
import logging

# Configure logging
logger = logging.getLogger("tuya-examples")

# Example: Register a fan device
@pyscript_executor
def setup_tuya_fan():
    # Register the device
    tuya_entities.register_tuya_device(
        name="living_room_fan",
        device_id="your_device_id_here",
        local_key="your_local_key_here",
        device_ip="192.168.1.x",  # Your device's IP address
        version=3.3  # Adjust if needed
    )
    
    # Create a fan entity
    tuya_entities.create_tuya_fan(
        device_name="living_room_fan",
        entity_id="fan.living_room_fan",
        name="Living Room Fan",
        dp_id=1,  # Replace with the actual DP ID for your fan's speed control
        speed_levels={1: "low", 2: "medium", 3: "high"}  # Adjust based on your fan's capabilities
    )
    
    logger.info("Living room fan entity has been set up")

# Example: Register a smart plug/switch
@pyscript_executor
def setup_tuya_switch():
    # Register the device
    tuya_entities.register_tuya_device(
        name="bedroom_lamp",
        device_id="your_device_id_here",
        local_key="your_local_key_here", 
        device_ip="192.168.1.x",  # Your device's IP address
    )
    
    # Create a switch entity
    tuya_entities.create_tuya_switch(
        device_name="bedroom_lamp",
        entity_id="switch.bedroom_lamp",
        name="Bedroom Lamp",
        dp_id=1,  # Replace with the actual DP ID for your switch's on/off control
        icon="mdi:lamp"
    )
    
    logger.info("Bedroom lamp entity has been set up")

# Example: Register a device with multiple entities (e.g., a fan with light)
@pyscript_executor
def setup_multi_function_device():
    # Register the device
    tuya_entities.register_tuya_device(
        name="ceiling_fan",
        device_id="your_device_id_here",
        local_key="your_local_key_here",
        device_ip="192.168.1.x",  # Your device's IP address
    )
    
    # Create a fan entity
    tuya_entities.create_tuya_fan(
        device_name="ceiling_fan",
        entity_id="fan.ceiling_fan",
        name="Ceiling Fan",
        dp_id=1,  # Replace with the actual DP ID for fan speed control
    )
    
    # Create a light switch entity for the same device
    tuya_entities.create_tuya_switch(
        device_name="ceiling_fan",
        entity_id="light.ceiling_fan_light",
        name="Ceiling Fan Light",
        dp_id=9,  # Replace with the actual DP ID for light control
        icon="mdi:ceiling-light"
    )
    
    # Create a sensor for the temperature (if your device has one)
    tuya_entities.create_tuya_sensor(
        device_name="ceiling_fan",
        entity_id="sensor.ceiling_fan_temperature",
        name="Ceiling Fan Temperature",
        dp_id=12,  # Replace with the actual DP ID for temperature
        unit="°C",
        icon="mdi:thermometer"
    )
    
    logger.info("Ceiling fan with multiple entities has been set up")

# Uncomment and modify these function calls to use them
# setup_tuya_fan()
# setup_tuya_switch()
# setup_multi_function_device()
