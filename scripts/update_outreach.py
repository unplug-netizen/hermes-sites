#!/usr/bin/env python3
"""Update outreach_sent flag in leads.json"""
import json

with open('data/leads.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

updated = []
for lead in data['leads']:
    if lead['status'] == 'live' and not lead.get('outreach_sent', False):
        lead['outreach_sent'] = True
        updated.append(lead['id'])

with open('data/leads.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated outreach_sent for: {updated}")
