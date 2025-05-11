import yaml
from pythonosc.udp_client import SimpleUDPClient

# Dummy badge data
badge_data = {
    "player_connect": True,
    "score": 140,
    "player_name": "David"
}

def load_config(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def send_osc_messages(config, badge_data):
    osc_config = config.get('osc', {})
    ip = osc_config.get('ip', '127.0.0.1')
    port = osc_config.get('port', 1337)
    print(f"Sending to {ip} on port {port}")
    client = SimpleUDPClient(ip, port)

    for mapping in config.get('mappings', []):
        field = mapping['field']
        if field not in badge_data:
            print(f"[WARN] Field '{field}' missing from badge data.")
            continue

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
    send_osc_messages(config, badge_data)

