from pymemcache.client import base
import json

client = base.Client(('localhost', 11211))
data = {
    "player_connect": True,
    "score": 140,
    "player_name": "ZEBBLER"
}
client.set("badge_data", json.dumps(data))
