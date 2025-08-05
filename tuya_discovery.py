import logging
import json
import tuya_helper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tuya-discovery")

@service
def scan_device_dps(device_id, local_key, device_ip, version=3.3):
    """
    Scan a Tuya device and return all its data points with their current values.
    This helps identify which DP controls which function.
    """
    logger.info(f"Scanning device {device_id} at {device_ip}")
    
    try:
        # Get the current status
        status = tuya_helper.get_tuya_device_status(device_id, local_key, device_ip, version)
        
        if not status:
            logger.error("Failed to get device status")
            return {"error": "Failed to get device status"}
            
        # Extract and format the DPs
        if "dps" in status:
            dps = status["dps"]
            result = {
                "device_id": device_id,
                "ip": device_ip,
                "data_points": dps,
                "raw_response": status
            }
            
            # Log the results
            logger.info(f"Found {len(dps)} data points")
            for dp, value in dps.items():
                logger.info(f"DP {dp}: {value} (type: {type(value).__name__})")
                
            # Create a formatted JSON string for better readability
            formatted_json = json.dumps(result, indent=2)
            logger.info(f"Full device scan result:\n{formatted_json}")
            
            return result
        else:
            logger.error("No data points found in status")
            return {"error": "No data points found", "raw_response": status}
    
    except Exception as e:
        logger.error(f"Error scanning device: {e}")
        return {"error": str(e)}


@service
def monitor_dp_changes(device_id, local_key, device_ip, version=3.3):
    """
    Monitor a device and log any changes to help identify which DP controls which function.
    Call this service, then manually operate your device (e.g., turn on/off, change speed)
    to see which DPs change.
    """
    logger.info(f"Starting to monitor device {device_id} at {device_ip}")
    logger.info("Operate your device manually to see which values change")
    
    try:
        # Get initial status
        initial_status = tuya_helper.get_tuya_device_status(device_id, local_key, device_ip, version)
        
        if not initial_status or "dps" not in initial_status:
            logger.error("Failed to get initial device status")
            return {"error": "Failed to get initial device status"}
            
        initial_dps = initial_status["dps"]
        logger.info(f"Initial state: {json.dumps(initial_dps, indent=2)}")
        
        # Start monitoring loop (will run for 5 minutes by default)
        import time
        end_time = time.time() + (5 * 60)  # 5 minutes from now
        
        last_dps = initial_dps.copy()
        
        while time.time() < end_time:
            time.sleep(2)  # Check every 2 seconds
            
            current_status = tuya_helper.get_tuya_device_status(device_id, local_key, device_ip, version)
            if not current_status or "dps" not in current_status:
                logger.warning("Failed to get current status")
                continue
                
            current_dps = current_status["dps"]
            
            # Check for changes
            for dp, value in current_dps.items():
                if dp not in last_dps or last_dps[dp] != value:
                    logger.info(f"DP {dp} changed: {last_dps.get(dp, 'N/A')} -> {value}")
            
            last_dps = current_dps.copy()
        
        logger.info("Monitoring completed")
        return {"message": "Monitoring completed"}
        
    except Exception as e:
        logger.error(f"Error monitoring device: {e}")
        return {"error": str(e)}
