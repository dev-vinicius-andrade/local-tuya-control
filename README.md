# Local Tuya Control with Home Assistant Entities

This project allows you to control Tuya devices locally (without cloud access) using Home Assistant and the pyscript integration. It creates proper Home Assistant entities for your Tuya devices, making them available in automations, scenes, and the UI.

## Setup

1. Make sure you have the [pyscript HACS add-on](https://github.com/custom-components/pyscript) installed in your Home Assistant instance.
2. Make sure you have the [tinytuya library](https://github.com/jasonacox/tinytuya) installed (can be installed via HACS or manually).
3. Place the Python files from this repository in your Home Assistant's `pyscript` directory.

## Understanding Tuya DPs (Data Points)

Tuya devices use "DPs" (Data Points) to control different functions. Each device model has its own set of DPs with specific meanings:

- For a fan: DP 1 might be the speed (0=off, 1=low, 2=medium, 3=high)
- For a light: DP 1 might be on/off, DP 2 might be brightness, etc.

To identify the DPs for your specific device, you can:
1. Use the `get_tuya_device_status` service to see all available DPs
2. Use tools like [Tuya IoT Platform](https://iot.tuya.com/) or [TuyAPI](https://github.com/codetheweb/tuyapi)

## Files in this Project

- `tuya_helper.py`: Basic functions for sending commands and getting status from Tuya devices
- `tuya_entities.py`: Creates and manages Home Assistant entities for Tuya devices
- `tuya_examples.py`: Example configurations for different types of devices

## How to Use

### 1. Register Your Device

First, register your Tuya device with the system:

```python
import tuya_entities

tuya_entities.register_tuya_device(
    name="living_room_fan",  # Friendly name for your reference
    device_id="your_device_id_here",  # From Tuya IoT Platform or device scan
    local_key="your_local_key_here",  # From Tuya IoT Platform or device scan
    device_ip="192.168.1.x",  # Your device's local IP address
    version=3.3  # Protocol version, typically 3.3 for newer devices
)
```

### 2. Create Entities for Your Device

Depending on the type of device, create appropriate entities:

#### For a Fan:

```python
tuya_entities.create_tuya_fan(
    device_name="living_room_fan",  # Name used when registering the device
    entity_id="fan.living_room_fan",  # Home Assistant entity ID
    name="Living Room Fan",  # Friendly name to display in Home Assistant
    dp_id=1,  # The DP that controls fan speed
    speed_levels={1: "low", 2: "medium", 3: "high"}  # Map DP values to speed names
)
```

#### For a Switch/Light:

```python
tuya_entities.create_tuya_switch(
    device_name="bedroom_lamp", 
    entity_id="switch.bedroom_lamp",
    name="Bedroom Lamp",
    dp_id=1,  # The DP that controls on/off
    icon="mdi:lamp"
)
```

#### For a Sensor:

```python
tuya_entities.create_tuya_sensor(
    device_name="device_name",
    entity_id="sensor.device_temperature",
    name="Device Temperature",
    dp_id=12,  # The DP that provides the sensor value
    unit="°C",  # Unit of measurement (optional)
    icon="mdi:thermometer"  # Icon (optional)
)
```

### 3. Update Device Status

The system will automatically update all device statuses every minute. If you need to update manually:

```python
# Update all devices
tuya_entities.update_all_tuya_devices()

# Update a specific device
tuya_entities.update_tuya_device("living_room_fan")
```

### 4. Controlling Entities

Once the entities are created, they can be controlled through:

- Home Assistant UI
- Home Assistant automations
- Services provided by pyscript

For example, to set a fan speed:
```yaml
# In an automation or script
service: pyscript.set_fan_living_room_fan_speed
data:
  speed: medium
```

Or to turn on a switch:
```yaml
service: pyscript.turn_on_switch_bedroom_lamp
```

## Advanced Configuration

See `tuya_examples.py` for more complex setups, including devices with multiple functions like ceiling fans with lights.

## Troubleshooting

If you're having trouble with your Tuya devices:

1. Use `tuya_helper.get_tuya_device_status()` to verify your device ID, local key, and IP address are correct.
2. Check the logs for error messages (accessible through Home Assistant Developer Tools).
3. Make sure your device is on the same network as Home Assistant and accessible locally.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
