#!/bin/bash
# Helper script for Tuya Local Control tools

# Function to display usage
show_usage() {
    echo "Tuya Local Control Tools Helper"
    echo "==============================="
    echo ""
    echo "Usage: ./tuya_tools.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  scan                     Scan for Tuya devices on your network"
    echo "  status [id] [ip] [key]   Get the status of a device"
    echo "  set [id] [ip] [key] [dp] [value]  Set a value for a data point"
    echo "  test-range [id] [ip] [key] [dp] [min] [max]  Test a range of values"
    echo "  test-protocol [id] [ip] [key] [dp] [value]  Test protocol versions"
    echo "  test-config              Test your configuration file"
    echo "  help                     Show this help message"
    echo ""
    echo "Example:"
    echo "  ./tuya_tools.sh scan"
    echo "  ./tuya_tools.sh status ebfd12345678 192.168.1.100 abcdef123456"
    echo "  ./tuya_tools.sh set ebfd12345678 192.168.1.100 abcdef123456 1 true"
    echo ""
}

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in your PATH"
    exit 1
fi

# Parse command
if [ $# -lt 1 ]; then
    show_usage
    exit 1
fi

command="$1"
shift

case "$command" in
    scan)
        python discovery_tool.py scan
        ;;
    status)
        if [ $# -lt 3 ]; then
            echo "Error: Missing parameters for status command"
            echo "Usage: ./tuya_tools.sh status [device_id] [ip] [key]"
            exit 1
        fi
        python discovery_tool.py status --id "$1" --ip "$2" --key "$3"
        ;;
    set)
        if [ $# -lt 5 ]; then
            echo "Error: Missing parameters for set command"
            echo "Usage: ./tuya_tools.sh set [device_id] [ip] [key] [dp] [value]"
            exit 1
        fi
        python discovery_tool.py set --id "$1" --ip "$2" --key "$3" --dp "$4" --value "$5"
        ;;
    test-range)
        if [ $# -lt 6 ]; then
            echo "Error: Missing parameters for test-range command"
            echo "Usage: ./tuya_tools.sh test-range [device_id] [ip] [key] [dp] [min] [max]"
            exit 1
        fi
        python discovery_tool.py test --id "$1" --ip "$2" --key "$3" --dp "$4" --min "$5" --max "$6"
        ;;
    test-protocol)
        if [ $# -lt 5 ]; then
            echo "Error: Missing parameters for test-protocol command"
            echo "Usage: ./tuya_tools.sh test-protocol [device_id] [ip] [key] [dp] [value]"
            exit 1
        fi
        python discovery_tool.py protocol --id "$1" --ip "$2" --key "$3" --dp "$4" --value "$5"
        ;;
    test-config)
        python config_tester.py
        ;;
    help)
        show_usage
        ;;
    *)
        echo "Error: Unknown command '$command'"
        show_usage
        exit 1
        ;;
esac
