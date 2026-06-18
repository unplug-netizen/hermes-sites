#!/usr/bin/env python3
import json

q = json.load(open('data/queue.json'))
for item in q['queue']:
    if item['id'] in ('trattoria-bella-vista', 'curry-house', 'pizza-roma'):
        print(item)
