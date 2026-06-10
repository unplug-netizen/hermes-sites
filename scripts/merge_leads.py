#!/usr/bin/env python3
"""
Merge neue Leads aus leads/qualified_leads.json in data/leads.json
- Prüft Duplikate (Name + Ort)
- Filtert Score >= 70
- Aktualisiert Stats
"""
import json
import datetime

# Load existing leads
with open('data/leads.json', 'r') as f:
    data = json.load(f)

existing = {(l['name'], l['ort']) for l in data['leads']}

# Load neue Leads
with open('leads/qualified_leads.json', 'r') as f:
    new_leads = json.load(f)

added = []
for lead in new_leads:
    name = lead['name']
    ort = lead['city']
    score = lead['score']

    if (name, ort) in existing:
        print(f"SKIP (Duplikat): {name} in {ort}")
        continue
    if score < 70:
        print(f"SKIP (Score <70): {name} Score={score}")
        continue

    new_id = name.lower().replace(' ', '-').replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    entry = {
        'id': new_id,
        'name': name,
        'branche': lead['category'],
        'ort': ort,
        'score': score,
        'has_website': lead['has_website'],
        'website_age': None,
        'mobile_friendly': None,
        'has_ssl': None,
        'social_active': True,  # Demo-Annahme
        'status': 'approved',
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z'),
        'built_at': None,
        'deployed_at': None,
        'outreach_sent': False,
        'url': None
    }
    data['leads'].append(entry)
    added.append(entry)
    print(f"ADD: {name} Score={score}")

data['last_updated'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
data['stats']['total_leads'] = len(data['leads'])
data['stats']['approved'] = sum(1 for l in data['leads'] if l['status'] in ('approved', 'live'))

with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nGesamt: {len(added)} neue Leads hinzugefügt")
