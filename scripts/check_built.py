import json

with open('data/queue.json') as f:
    data = json.load(f)

built = [s for s in data['queue'] if s['status'] == 'built']
print('BUILT_SITES=' + ' '.join([s['id'] for s in built]))
