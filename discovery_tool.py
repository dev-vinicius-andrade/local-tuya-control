#!/usr/bin/env python3
"""
Tuya Device Discovery Tool

This script helps to discover Tuya devices on your network and identify their data points (DPs).
"""
import argparse
import json
import time
import tinytuya
from protocol_test import test_protocol_versions

def scan_devices():
    """Scan for devices on the local network."""
    print("Scanning for Tuya devices on the local network...")
    print("This can take up to 60 seconds...")
    
    devices = tinytuya.deviceScan(False, 20)
    
    print(f"\nFound {len(devices)} device(s):\n")
    
    for dev_id, dev_info in devices.items():
        print(f"Device ID: {dev_id}")
        print(f"  IP Address: {dev_info['ip']}")
        print(f"  Product: {dev_info.get('productKey', 'Unknown')}")
        print(f"  Version: {dev_info.get('version', 'Unknown')}")
        print("")
    
    return devices

def get_device_status(device_id, ip, local_key, version):
    """Get the status of a specific device."""
    print(f"Getting status for device {device_id}...")
    
    device = tinytuya.OutletDevice(device_id, ip, local_key)
    device.set_version(version)
    
    try:
        status = device.status()
        print("\nDevice Status:")
        print(json.dumps(status, indent=2))
        
        if 'dps' in status:
            print("\nData Points (DPs):")
            for dp, value in status['dps'].items():
                print(f"  DP {dp}: {value} (type: {type(value).__name__})")
        
        return status
    except Exception as e:
        print(f"Error getting device status: {e}")
        return None

def set_device_dp(device_id, ip, local_key, version, dp, value):
    """Set a specific data point value on a device."""
    device = tinytuya.OutletDevice(device_id, ip, local_key)
    device.set_version(version)
    
    # Convert value string to appropriate type
    if value.lower() == 'true':
        typed_value = True
    elif value.lower() == 'false':
        typed_value = False
    elif value.isdigit():
        typed_value = int(value)
    elif value.replace('.', '', 1).isdigit():
        typed_value = float(value)
    else:
        typed_value = value
    
    print(f"Setting DP {dp} to {typed_value} (type: {type(typed_value).__name__})...")
    
    try:
        result = device.set_status(dp, typed_value)
        print("\nResult:")
        print(json.dumps(result, indent=2))
        
        # Get updated status
        time.sleep(1)
        status = device.status()
        print("\nUpdated Device Status:")
        print(json.dumps(status, indent=2))
        
        return result
    except Exception as e:
        print(f"Error setting device DP: {e}")
        return None

def test_dp_range(device_id, ip, local_key, version, dp, min_val, max_val, step):
    """Test a range of values for a specific data point."""
    device = tinytuya.OutletDevice(device_id, ip, local_key)
    device.set_version(version)
    
    print(f"Testing DP {dp} with values from {min_val} to {max_val} (step {step})...")
    
    for value in range(min_val, max_val + 1, step):
        try:
            print(f"\nSetting DP {dp} to {value}...")
            result = device.set_status(dp, value)
            print(f"Result: {result}")
            time.sleep(1)
        except Exception as e:
            print(f"Error setting value {value}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Tuya Device Discovery Tool')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan for Tuya devices on the network')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get device status')
    status_parser.add_argument('--id', required=True, help='Device ID')
    status_parser.add_argument('--ip', required=True, help='Device IP address')
    status_parser.add_argument('--key', required=True, help='Device local key')
    status_parser.add_argument('--version', type=float, default=3.5, help='Protocol version (default: 3.5)')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set device data point')
    set_parser.add_argument('--id', required=True, help='Device ID')
    set_parser.add_argument('--ip', required=True, help='Device IP address')
    set_parser.add_argument('--key', required=True, help='Device local key')
    set_parser.add_argument('--version', type=float, default=3.5, help='Protocol version (default: 3.5)')
    set_parser.add_argument('--dp', required=True, type=int, help='Data point ID')
    set_parser.add_argument('--value', required=True, help='Value to set')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a range of values for a data point')
    test_parser.add_argument('--id', required=True, help='Device ID')
    test_parser.add_argument('--ip', required=True, help='Device IP address')
    test_parser.add_argument('--key', required=True, help='Device local key')
    test_parser.add_argument('--version', type=float, default=3.5, help='Protocol version (default: 3.5)')
    test_parser.add_argument('--dp', required=True, type=int, help='Data point ID')
    test_parser.add_argument('--min', required=True, type=int, help='Minimum value')
    test_parser.add_argument('--max', required=True, type=int, help='Maximum value')
    test_parser.add_argument('--step', type=int, default=1, help='Step size (default: 1)')
    
    # Protocol version test command
    protocol_parser = subparsers.add_parser('protocol', help='Test different protocol versions with a specific data point')
    protocol_parser.add_argument('--id', required=True, help='Device ID')
    protocol_parser.add_argument('--ip', required=True, help='Device IP address')
    protocol_parser.add_argument('--key', required=True, help='Device local key')
    protocol_parser.add_argument('--dp', required=True, type=int, help='Data point ID')
    protocol_parser.add_argument('--value', required=True, help='Value to test')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        scan_devices()
    
    elif args.command == 'status':
        get_device_status(args.id, args.ip, args.key, args.version)
    
    elif args.command == 'set':
        set_device_dp(args.id, args.ip, args.key, args.version, args.dp, args.value)
    
    elif args.command == 'test':
        test_dp_range(args.id, args.ip, args.key, args.version, args.dp, args.min, args.max, args.step)
    
    elif args.command == 'protocol':
        test_protocol_versions(args.id, args.ip, args.key, args.dp, args.value)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
