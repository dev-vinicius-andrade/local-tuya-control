# Contributing to Tuya Local Control

Thank you for your interest in contributing to the Tuya Local Control integration for Home Assistant!

## Development Environment Setup

1. Fork the repository
2. Clone your fork locally
3. Set up a test Home Assistant instance:
   ```bash
   mkdir homeassistant_test
   cd homeassistant_test
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install homeassistant
   ```

4. Create a custom_components directory in your Home Assistant test instance
5. Symlink or copy the tuya_local_control directory into the custom_components directory
6. Start Home Assistant in debug mode:
   ```bash
   hass -c . --debug
   ```

## Testing Your Changes

1. Make your changes to the code
2. Test your changes with actual Tuya devices
3. Use the included discovery and protocol testing tools:
   ```bash
   python discovery_tool.py scan
   python discovery_tool.py protocol --id YOUR_DEVICE_ID --ip YOUR_DEVICE_IP --key YOUR_LOCAL_KEY --dp 1 --value true
   ```

## Submitting a Pull Request

1. Make sure your code follows the existing style
2. Update documentation if necessary
3. Add test cases if applicable
4. Create a pull request with a clear description of the changes
5. Include any relevant issues by using the GitHub keywords (e.g., "Fixes #123")

## Code Style Guidelines

1. Follow PEP 8 for Python code
2. Use descriptive variable names
3. Include docstrings for functions and classes
4. Keep functions small and focused on a single task
5. Add comments for complex logic

## Adding Support for New Entity Types

If you want to add support for a new entity type:

1. Create a new platform file (e.g., `binary_sensor.py`)
2. Implement the required platform setup functions
3. Add the new entity type to the supported types in `__init__.py`
4. Update the documentation with examples for the new entity type
5. Test with actual devices

## Reporting Bugs

If you find a bug, please report it by creating an issue with:

1. A clear description of the problem
2. Steps to reproduce
3. Expected vs. actual behavior
4. Home Assistant version and relevant logs
5. Device information (model, firmware version if known)

## Feature Requests

If you have an idea for a new feature:

1. First check if it's already been requested
2. Create an issue with a clear description of the feature
3. Explain why it would be useful to the broader community
4. Include any implementation ideas you may have

Thank you for helping improve the Tuya Local Control integration!
