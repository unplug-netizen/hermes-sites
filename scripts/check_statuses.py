import json

with open('data/queue.json') as f:
    data = json.load(f)

for s in data['queue']:
    print(f"{s['id']}: {s['status']}")
