import json
from datetime import datetime, timezone

with open('data/queue.json', 'r') as f:
    data = json.load(f)

now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
slugs = [
    'trattoria-bella-vista-frankfurt',
    'curry-house-frankfurt',
    'pizza-roma-frankfurt'
]

for item in data['queue']:
    if item['id'] in slugs and item['status'] == 'deploying':
        item['status'] = 'live'
        item['stage'] = 'completed'
        item['last_action'] = now
        item['next_action'] = None

with open('data/queue.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('queue.json updated to live')
