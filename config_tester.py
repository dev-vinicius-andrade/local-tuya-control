#!/usr/bin/env python3
"""
Tuya Configuration Tester

This script validates your configuration and tests connections to your Tuya devices.
"""
import argparse
import sys
import yaml
import tinytuya
from tuya_controller_fixed import TuyaController


def validate_config(config_path):
    """Validate the configuration file format."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        if not config:
            print("Error: Configuration is empty")
            return False

        if "devices" not in config:
            print("Error: 'devices' section is missing from configuration")
            return False

        devices = config.get("devices", [])
        if not devices:
            print("Error: No devices configured")
            return False

        for i, device in enumerate(devices):
            if not validate_device_config(device, i):
                return False

        print("✓ Configuration format is valid")
        return True

    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_path}")
        return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML configuration: {e}")
        return False


def validate_device_config(device, index):
    """Validate a single device configuration."""
    required_fields = ["name", "device_id", "ip", "local_key"]
    for field in required_fields:
        if field not in device:
            print(f"Error in device #{index+1}: Missing required field '{field}'")
            return False

    if "entities" not in device or not device["entities"]:
        print(f"Error in device '{device.get('name')}': No entities configured")
        return False

    for i, entity in enumerate(device["entities"]):
        required_entity_fields = ["name", "unique_id", "type", "set_dp", "get_dp"]
        for field in required_entity_fields:
            if field not in entity:
                print(
                    f"Error in entity #{i+1} of device '{device.get('name')}': Missing required field '{field}'"
                )
                return False

        entity_type = entity.get("type")
        if entity_type not in ["switch", "number", "light", "sensor", "fan"]:
            print(
                f"Error in entity '{entity.get('name')}': Invalid type '{entity_type}'"
            )
            return False

    return True


def test_device_connection(device_config):
    """Test connection to a Tuya device."""
    print(f"\nTesting connection to {device_config.get('name')}...")

    device = tinytuya.OutletDevice(
        dev_id=device_config.get("device_id"),
        address=device_config.get("ip"),
        local_key=device_config.get("local_key"),
    )

    version = device_config.get("version", 3.5)
    device.set_version(version)

    try:
        status = device.status()
        if not status:
            print(f"✗ Failed to get status from {device_config.get('name')}")
            return False

        if "dps" not in status:
            print(f"✗ Device responded but did not return data points")
            return False

        print(f"✓ Successfully connected to {device_config.get('name')}")
        print(f"  Data points found: {list(status['dps'].keys())}")
        return True
    except Exception as e:
        print(f"✗ Error connecting to {device_config.get('name')}: {e}")
        print("  Possible issues:")
        print("  - The device may be offline")
        print("  - IP address may be incorrect")
        print("  - Local key may be incorrect")
        print("  - Protocol version may be incorrect (try 3.1, 3.3, or 3.5)")
        return False


def test_entities(device_config):
    """Test each entity configuration by attempting to get values."""
    print(f"\nTesting entities for {device_config.get('name')}...")

    controller = TuyaController(device_config)
    success_count = 0
    failure_count = 0

    for entity in device_config.get("entities", []):
        entity_id = entity.get("unique_id")
        entity_name = entity.get("name")
        entity_type = entity.get("type")
        get_dp = entity.get("get_dp")

        print(
            f"\n  Testing entity: {entity_name} (ID: {entity_id}, Type: {entity_type}, DP: {get_dp})"
        )

        try:
            value = controller.get_value(entity_id)
            if value is not None:
                print(f"  ✓ Successfully retrieved value: {value}")
                success_count += 1
            else:
                print(f"  ✗ Failed to get value (null response)")
                failure_count += 1
        except Exception as e:
            print(f"  ✗ Error getting value: {e}")
            failure_count += 1

    print(
        f"\n{success_count}/{len(device_config.get('entities', []))} entities tested successfully"
    )
    return success_count, failure_count


def test_protocol_versions(device_config):
    """Test different protocol versions with a device."""
    print(f"\nTesting protocol versions for {device_config.get('name')}...")

    device_id = device_config.get("device_id")
    ip = device_config.get("ip")
    local_key = device_config.get("local_key")

    versions = [3.1, 3.3, 3.5]
    results = {}

    for version in versions:
        print(f"\n  Testing protocol version {version}...")

        device = tinytuya.OutletDevice(
            dev_id=device_id, address=ip, local_key=local_key
        )
        device.set_version(version)

        try:
            status = device.status()
            success = status and "dps" in status

            if success:
                dps_count = len(status["dps"]) if "dps" in status else 0
                print(f"  ✓ Version {version} works (found {dps_count} data points)")
                results[version] = {
                    "success": True,
                    "dps_count": dps_count,
                    "dps": list(status["dps"].keys()) if "dps" in status else [],
                }
            else:
                print(f"  ✗ Version {version} failed to get data")
                results[version] = {"success": False}

        except Exception as e:
            print(f"  ✗ Version {version} error: {e}")
            results[version] = {"success": False, "error": str(e)}

    # Find best version based on number of DPs found
    best_version = None
    max_dps = 0

    for version, result in results.items():
        if result.get("success") and result.get("dps_count", 0) > max_dps:
            max_dps = result.get("dps_count", 0)
            best_version = version

    if best_version:
        print(
            f"\nRecommended protocol version: {best_version} (found {max_dps} data points)"
        )
    else:
        print("\nNo working protocol version found")

    return results


def main():
    parser = argparse.ArgumentParser(description="Tuya Configuration Tester")
    parser.add_argument(
        "--config", default="config.yaml", help="Path to configuration file"
    )
    parser.add_argument(
        "--test-protocol", action="store_true", help="Test different protocol versions"
    )
    parser.add_argument(
        "--device", type=str, help="Test only a specific device by name"
    )

    args = parser.parse_args()

    print("Tuya Configuration Tester")
    print("========================\n")

    # Validate configuration
    if not validate_config(args.config):
        sys.exit(1)

    # Load configuration
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    devices = config.get("devices", [])
    success_count = 0

    # Filter devices if specified
    if args.device:
        devices = [d for d in devices if d.get("name") == args.device]
        if not devices:
            print(f"Error: Device '{args.device}' not found in configuration")
            sys.exit(1)

    # Test each device
    for device in devices:
        if test_device_connection(device):
            success_count += 1

            # Test protocol versions
            if args.test_protocol:
                test_protocol_versions(device)

            # Test entities
            test_entities(device)

    # Print summary
    print("\nSummary")
    print("=======")
    print(f"{success_count}/{len(devices)} devices connected successfully")

    if success_count == len(devices):
        print("\nAll devices are working properly!")
    else:
        print("\nSome devices had connection issues. Please review the output above.")


if __name__ == "__main__":
    main()
