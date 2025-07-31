# Home Assistant Integration for Tuya Local Control

## Installation Instructions

To use this integration with Home Assistant:

1. Copy the `custom_components/tuya_local_control` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the configuration to your `configuration.yaml` file

## Configuration Example

```yaml
# configuration.yaml
tuya_local_control:
  devices:
    - name: "FAN_EXAMPLE_DEVICE"
      device_id: "DEVICE_ID_HERE"
      ip: "LOCAL_IP_ADDRESS_HERE"
      local_key: "LOCAL_KEY_HERE"
      version: 3.5  # Default protocol version for the device
      entities:
        - name: "Fan Speed"
          unique_id: "fan_speed"
          type: "fan"
          set_dp: 62
          get_dp: 62
          min: 1
          max: 3
          step: 1
          version: 3.3  # Override protocol version for this specific entity
        - name: "Fan Oscillation"
          unique_id: "fan_oscillation"
          type: "switch"
          set_dp: 8
          get_dp: 8
          values:
            "on": true
            "off": false
```

## Protocol Version Configuration

Some Tuya devices require specific protocol versions for certain functions to work correctly. This integration allows you to:

1. Set a default protocol version for the entire device (usually 3.1, 3.3, or 3.5)
2. Override the protocol version for specific entities when needed

To determine which protocol version works best for each entity:

```
# Test different protocol versions for a specific data point
python discovery_tool.py protocol --id YOUR_DEVICE_ID --ip YOUR_DEVICE_IP --key YOUR_LOCAL_KEY --dp 62 --value 3
```

## Finding the Right DPs

Use the included discovery tool to find the right data points for your device:

```
# Scan for devices
python discovery_tool.py scan

# Get device status
python discovery_tool.py status --id YOUR_DEVICE_ID --ip YOUR_DEVICE_IP --key YOUR_LOCAL_KEY

# Test setting a specific DP
python discovery_tool.py set --id YOUR_DEVICE_ID --ip YOUR_DEVICE_IP --key YOUR_LOCAL_KEY --dp 62 --value 3

# Test a range of values for a DP
python discovery_tool.py test --id YOUR_DEVICE_ID --ip YOUR_DEVICE_IP --key YOUR_LOCAL_KEY --dp 62 --min 1 --max 5
```

## Services

Once the integration is set up, you can use these services:

- `tuya_local_control.set_device_value`: Set a raw value for a specific DP
- `tuya_local_control.get_device_status`: Get the full status of a device

## Troubleshooting

If you encounter issues:

1. Make sure your device is on the same network as Home Assistant
2. Verify the IP address is correct
3. Try different protocol versions (3.1, 3.3, or 3.5)
4. Check the Home Assistant logs for error messages
