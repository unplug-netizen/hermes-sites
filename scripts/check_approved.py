#!/usr/bin/env python3
import json

with open('data/queue.json') as f:
    q = json.load(f)

approved = [i for i in q['queue'] if i['status'] == 'approved']
print(f'Approved in queue: {len(approved)}')
print([i['id'] for i in approved])
