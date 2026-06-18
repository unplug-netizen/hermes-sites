#!/usr/bin/env python3
import json
from datetime import datetime, timezone

with open('/root/hermes-sites/data/queue.json', 'r') as f:
    q = json.load(f)

for item in q['queue']:
    if item['status'] == 'built':
        item['status'] = 'live'
        item['stage'] = 'completed'
        item['last_action'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        item['next_action'] = None

q['last_updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('/root/hermes-sites/data/queue.json', 'w') as f:
    json.dump(q, f, indent=2, ensure_ascii=False)

print('✅ Status auf live gesetzt')
