import tinytuya
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tuya-local-control")

import tinytuya


@service
def send_tuya_command(device_id, local_key, device_ip, dp, value, version=3.3):
    d = tinytuya.Device(
        dev_id=device_id,
        local_key=local_key,
        address=device_ip,
    )
    d.set_version(version)
    d.set_value(dp, value)


@service
def get_tuya_device_status(device_id, local_key, device_ip, version=3.3):
    d = tinytuya.Device(
        dev_id=device_id,
        local_key=local_key,
        address=device_ip,
    )
    d.set_version(version)
    d.set_socketPersistent(True)
    r = d.status()
    return r
