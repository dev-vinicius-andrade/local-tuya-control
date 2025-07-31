import tinytuya

def test_protocol_versions(device_id, ip, local_key, dp, value):
    """Test different protocol versions with a specific DP and value.
    
    This helps determine which protocol version works best for a specific data point.
    """
    versions = [3.1, 3.3, 3.5]
    
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
    
    print(f"Testing DP {dp} with value {typed_value} across different protocol versions...")
    
    results = {}
    
    for version in versions:
        print(f"\nTrying protocol version {version}...")
        
        device = tinytuya.OutletDevice(device_id, ip, local_key)
        device.set_version(version)
        
        try:
            # First try to get status
            status_result = device.status()
            status_success = 'dps' in status_result and str(dp) in status_result['dps']
            
            # Then try to set the value
            set_result = device.set_status(dp, typed_value)
            set_success = 'dps' in set_result if set_result else False
            
            results[version] = {
                'status_success': status_success,
                'set_success': set_success,
                'status_result': status_result,
                'set_result': set_result
            }
            
            if status_success and set_success:
                print(f"✓ Protocol version {version} works for both get and set operations")
            elif status_success:
                print(f"✓ Protocol version {version} works for get operations only")
            elif set_success:
                print(f"✓ Protocol version {version} works for set operations only")
            else:
                print(f"✗ Protocol version {version} does not work")
                
        except Exception as e:
            print(f"✗ Protocol version {version} failed: {e}")
            results[version] = {
                'status_success': False,
                'set_success': False,
                'error': str(e)
            }
    
    # Recommend the best version
    recommend_version = None
    for version in versions:
        if version in results and results[version].get('status_success') and results[version].get('set_success'):
            recommend_version = version
            break
    
    if recommend_version:
        print(f"\nRecommended protocol version for DP {dp}: {recommend_version}")
    else:
        # If no version works for both, find one that works for at least one operation
        for version in versions:
            if version in results and (results[version].get('status_success') or results[version].get('set_success')):
                recommend_version = version
                break
        
        if recommend_version:
            print(f"\nPartially working protocol version for DP {dp}: {recommend_version}")
        else:
            print(f"\nNo working protocol version found for DP {dp}")
    
    return results
