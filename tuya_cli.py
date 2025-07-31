#!/usr/bin/env python3
import argparse
from config_manager import ConfigManager
from tuya_controller_fixed import TuyaController

def main():
    parser = argparse.ArgumentParser(description='Control Tuya devices using tinytuya')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--list-devices', action='store_true', help='List all configured devices')
    parser.add_argument('--device', type=str, help='Device name to control')
    parser.add_argument('--list-entities', action='store_true', help='List all entities for the specified device')
    parser.add_argument('--entity', type=str, help='Entity ID to control')
    parser.add_argument('--set', type=str, help='Value to set for the entity')
    parser.add_argument('--get', action='store_true', help='Get the current value of the entity')
    parser.add_argument('--status', action='store_true', help='Get full device status')
    
    args = parser.parse_args()
    
    config_manager = ConfigManager(args.config)
    
    # List all devices
    if args.list_devices:
        devices = config_manager.get_devices()
        print(f"Found {len(devices)} device(s):")
        for device in devices:
            print(f"- {device.get('name')} (ID: {device.get('device_id')})")
        return
    
    # Check if a device was specified
    if not args.device and (args.list_entities or args.entity or args.status):
        print("Error: You must specify a device with --device")
        return
    
    # Get device configuration
    if args.device:
        device_config = config_manager.get_device_by_name(args.device)
        if not device_config:
            print(f"Error: Device '{args.device}' not found in configuration")
            return
        
        # Create controller for the device
        controller = TuyaController(device_config)
        
        # List all entities for the device
        if args.list_entities:
            entities = controller.get_entities()
            print(f"Found {len(entities)} entity/entities for '{args.device}':")
            for entity in entities:
                print(f"- {entity.get('name')} (ID: {entity.get('unique_id')}, Type: {entity.get('type')})")
            return
        
        # Get full device status
        if args.status:
            status = controller.get_status()
            print(f"Status for '{args.device}':")
            print(status)
            return
        
        # Check if an entity was specified
        if not args.entity and (args.get or args.set is not None):
            print("Error: You must specify an entity with --entity")
            return
        
        # Get the current value of an entity
        if args.entity and args.get:
            try:
                value = controller.get_value(args.entity)
                print(f"Current value of '{args.entity}': {value}")
            except Exception as e:
                print(f"Error getting value: {e}")
            return
        
        # Set a value for an entity
        if args.entity and args.set is not None:
            try:
                # Convert value to appropriate type
                value = args.set
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)
                
                response = controller.set_value(args.entity, value)
                print(f"Set '{args.entity}' to '{value}'")
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error setting value: {e}")
            return

if __name__ == "__main__":
    main()
