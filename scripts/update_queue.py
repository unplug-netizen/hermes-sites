#!/usr/bin/env python3
import json, datetime, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
queue_file = BASE_DIR / "data" / "queue.json"

with open(queue_file) as f:
    q = json.load(f)

for item in q['queue']:
    if item['status'] == 'built':
        item['status'] = 'live'
        item['stage'] = 'completed'
        item['last_action'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        item['next_action'] = None

q['last_updated'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
live_ids = [i['id'] for i in q['queue'] if i['status'] == 'live']
q['pending_deploys'] = [x for x in q.get('pending_deploys', []) if x not in live_ids]

with open(queue_file, 'w') as f:
    json.dump(q, f, indent=2)

print('Queue updated')
