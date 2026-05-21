#!/usr/bin/env python3
"""
Process new leads and merge into data/leads.json
"""
import json
from datetime import datetime, timezone

# Load existing leads
with open('data/leads.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_names = { (l['name'], l['ort']) for l in data['leads'] }

# Load new leads
with open('leads/qualified_leads.json', 'r', encoding='utf-8') as f:
    new_leads_raw = json.load(f)

new_leads = []
for lead in new_leads_raw:
    if lead['score'] >= 70 and (lead['name'], lead['city']) not in existing_names:
        new_leads.append(lead)
        # Add to data
        data['leads'].append({
            'id': lead['place_id'],
            'name': lead['name'],
            'branche': lead['category'],
            'ort': lead['city'],
            'score': lead['score'],
            'has_website': lead['has_website'],
            'website_age': None,
            'mobile_friendly': None,
            'has_ssl': None,
            'social_active': None,
            'status': 'new',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'built_at': None,
            'deployed_at': None,
            'outreach_sent': False,
            'url': None
        })

data['last_updated'] = datetime.now(timezone.utc).isoformat()
data['stats']['total_leads'] = len(data['leads'])
data['stats']['approved'] = sum(1 for l in data['leads'] if l['score'] >= 70)

with open('data/leads.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Neue Leads hinzugefügt: {len(new_leads)}')
for l in new_leads:
    print(f"  - {l['name']} | Score: {l['score']} | {l['city']}")
