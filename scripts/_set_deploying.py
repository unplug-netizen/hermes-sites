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
    if item['id'] in slugs and item['status'] == 'built':
        item['status'] = 'deploying'
        item['stage'] = 'deploy'
        item['last_action'] = now

with open('data/queue.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print('queue.json updated to deploying')
