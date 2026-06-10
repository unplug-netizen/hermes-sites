#!/usr/bin/env python3
import json
import os
import datetime

# Load existing leads
with open('data/leads.json', 'r') as f:
    data = json.load(f)

existing = {(l['name'], l['ort']) for l in data['leads']}

# Simulierte neue Leads (aus lead_scout.py Output)
new_leads_raw = [
    {'name': 'Trattoria Bella Vista', 'branche': 'restaurant', 'ort': 'Berlin', 'score': 100, 'has_website': False, 'social_active': True},
    {'name': 'Curry House', 'branche': 'restaurant', 'ort': 'Berlin', 'score': 100, 'has_website': False, 'social_active': True},
    {'name': 'Pizza Roma', 'branche': 'restaurant', 'ort': 'Berlin', 'score': 95, 'has_website': False, 'social_active': True},
    {'name': 'Burger King Berlin Mitte', 'branche': 'restaurant', 'ort': 'Berlin', 'score': 65, 'has_website': True, 'social_active': True},
]

added = []
for lead in new_leads_raw:
    if (lead['name'], lead['ort']) in existing:
        print(f"SKIP (Duplikat): {lead['name']} in {lead['ort']}")
        continue
    if lead['score'] < 70:
        print(f"SKIP (Score <70): {lead['name']} Score={lead['score']}")
        continue
    new_id = lead['name'].lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    entry = {
        'id': new_id,
        'name': lead['name'],
        'branche': lead['branche'],
        'ort': lead['ort'],
        'score': lead['score'],
        'has_website': lead['has_website'],
        'website_age': None,
        'mobile_friendly': None,
        'has_ssl': None,
        'social_active': lead.get('social_active', False),
        'status': 'approved',
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'built_at': None,
        'deployed_at': None,
        'outreach_sent': False,
        'url': None
    }
    data['leads'].append(entry)
    added.append(entry)
    print(f"ADD: {lead['name']} Score={lead['score']}")

data['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
data['stats']['total_leads'] = len(data['leads'])
data['stats']['approved'] = sum(1 for l in data['leads'] if l['status'] == 'approved')

with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nGesamt: {len(added)} neue Leads hinzugefügt")
print(json.dumps(added, indent=2, ensure_ascii=False))
