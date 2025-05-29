import yaml
import json
import time
from pythonosc.udp_client import SimpleUDPClient
import pymemcache.client.base

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_badge_data(config):
    memcached_config = config.get('memcached', {})
    host = memcached_config.get('host', '127.0.0.1')
    port = memcached_config.get('port', 11211)
    key = memcached_config.get('key', 'badge_data')
    
    print(f"Connecting to memcached at {host}:{port} with key {key}")
    client = pymemcache.client.base.Client((host, port))
    
    try:
        data = client.get(key)
        if data:
            return json.loads(data.decode('utf-8'))
        else:
            print(f"[ERROR] No data found in memcached with key '{key}'")
            return {}
    except Exception as e:
        print(f"[ERROR] Failed to get data from memcached: {e}")
        return {}

def send_osc_messages(config, badge_data):
    osc_config = config.get('osc', {})
    ip = osc_config.get('ip', '127.0.0.1')
    port = osc_config.get('port', 1337)
    print(f"Sending to {ip} on port {port}")
    client = SimpleUDPClient(ip, port)

    for mapping in config.get('mappings', []):
        field = mapping['field']
        if field not in badge_data:
            print(f"[WARN] Field '{field}' missing from badge data, using default value.")
            # Default to 0 for numbers, False for booleans, and empty string for text
            msg_type = mapping['type']
            if msg_type == 'launch':
                value = False
            elif msg_type == 'number':
                value = 0
            elif msg_type == 'text':
                value = ""
            else:
                print(f"[ERROR] Unknown type '{msg_type}' for field '{field}'.")
                continue
        else:
            value = badge_data[field]
        msg_type = mapping['type']
        path = mapping['path']

        if msg_type == 'launch':
            client.send_message(path, True if value else False)
        elif msg_type == 'number':
            client.send_message(path, float(value))
        elif msg_type == 'text':
            client.send_message(path, str(value))
        else:
            print(f"[ERROR] Unknown type '{msg_type}' for field '{field}'.")

if __name__ == "__main__":
    config = load_config("config.yaml")
    previous_badge_data = {}
    
    # Get polling interval from config, default to 1 second
    polling_interval = config.get('polling_interval', 1)
    
    print(f"Starting badge data polling loop with interval of {polling_interval} seconds")
    
    try:
        while True:
            badge_data = get_badge_data(config)
            
            # Only send OSC messages if the data has changed
            if badge_data != previous_badge_data:
                print("Badge data changed, sending OSC updates")
                send_osc_messages(config, badge_data)
                previous_badge_data = badge_data.copy()
            else:
                print("No change in badge data")
                
            time.sleep(polling_interval)
    except KeyboardInterrupt:
        print("\nExiting...")

