# PowerShell Helper Script for Tuya Local Control Tools

# Function to display usage
function Show-Usage {
    Write-Host "Tuya Local Control Tools Helper"
    Write-Host "==============================="
    Write-Host ""
    Write-Host "Usage: .\tuya_tools.ps1 [command] [options]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  scan                     Scan for Tuya devices on your network"
    Write-Host "  status [id] [ip] [key]   Get the status of a device"
    Write-Host "  set [id] [ip] [key] [dp] [value]  Set a value for a data point"
    Write-Host "  test-range [id] [ip] [key] [dp] [min] [max]  Test a range of values"
    Write-Host "  test-protocol [id] [ip] [key] [dp] [value]  Test protocol versions"
    Write-Host "  test-config              Test your configuration file"
    Write-Host "  help                     Show this help message"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\tuya_tools.ps1 scan"
    Write-Host "  .\tuya_tools.ps1 status ebfd12345678 192.168.1.100 abcdef123456"
    Write-Host "  .\tuya_tools.ps1 set ebfd12345678 192.168.1.100 abcdef123456 1 true"
    Write-Host ""
}

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python is not installed or not in your PATH"
    exit 1
}

# Parse command
if ($args.Count -lt 1) {
    Show-Usage
    exit 1
}

$command = $args[0]
$params = $args[1..($args.Count-1)]

switch ($command) {
    "scan" {
        python discovery_tool.py scan
    }
    "status" {
        if ($params.Count -lt 3) {
            Write-Host "Error: Missing parameters for status command"
            Write-Host "Usage: .\tuya_tools.ps1 status [device_id] [ip] [key]"
            exit 1
        }
        python discovery_tool.py status --id $params[0] --ip $params[1] --key $params[2]
    }
    "set" {
        if ($params.Count -lt 5) {
            Write-Host "Error: Missing parameters for set command"
            Write-Host "Usage: .\tuya_tools.ps1 set [device_id] [ip] [key] [dp] [value]"
            exit 1
        }
        python discovery_tool.py set --id $params[0] --ip $params[1] --key $params[2] --dp $params[3] --value $params[4]
    }
    "test-range" {
        if ($params.Count -lt 6) {
            Write-Host "Error: Missing parameters for test-range command"
            Write-Host "Usage: .\tuya_tools.ps1 test-range [device_id] [ip] [key] [dp] [min] [max]"
            exit 1
        }
        python discovery_tool.py test --id $params[0] --ip $params[1] --key $params[2] --dp $params[3] --min $params[4] --max $params[5]
    }
    "test-protocol" {
        if ($params.Count -lt 5) {
            Write-Host "Error: Missing parameters for test-protocol command"
            Write-Host "Usage: .\tuya_tools.ps1 test-protocol [device_id] [ip] [key] [dp] [value]"
            exit 1
        }
        python discovery_tool.py protocol --id $params[0] --ip $params[1] --key $params[2] --dp $params[3] --value $params[4]
    }
    "test-config" {
        python config_tester.py
    }
    "help" {
        Show-Usage
    }
    default {
        Write-Host "Error: Unknown command '$command'"
        Show-Usage
        exit 1
    }
}
