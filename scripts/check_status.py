import json, sys, os
from datetime import datetime, timezone

with open('data/queue.json', 'r') as f:
    q = json.load(f)

with open('data/leads.json', 'r') as f:
    l = json.load(f)

# Check for any built sites in queue
built_in_queue = [item for item in q['queue'] if item['status'] == 'built']

# Check for any leads with status 'built' but not in queue as live
built_leads = [lead for lead in l['leads'] if lead['status'] == 'built']

print('Built in queue:', [b['id'] for b in built_in_queue])
print('Built leads:', [b['id'] for b in built_leads])

# Also check if baeckerei-schmidt exists in leads or queue
all_ids = [item['id'] for item in q['queue']] + [lead['id'] for lead in l['leads']]
print('All tracked IDs:', all_ids)
print('baeckerei-schmidt in tracked:', 'baeckerei-schmidt' in all_ids)
