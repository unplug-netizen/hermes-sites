#!/usr/bin/env python3
"""
Merge new qualified leads into leads.json, checking for duplicates and score thresholds.
"""
import json
from datetime import datetime, timezone

# Load existing leads
with open('data/leads.json', 'r') as f:
    data = json.load(f)

existing_leads = data.get('leads', [])
existing_ids = {l['id'] for l in existing_leads}
existing_name_ort = {(l['name'], l['ort']) for l in existing_leads}

# Load new qualified leads
with open('leads/qualified_leads.json', 'r') as f:
    new_leads_raw = json.load(f)

new_added = []
for lead in new_leads_raw:
    name = lead['name']
    ort = lead['city']
    branche = lead['category']
    score = lead['score']
    
    # Duplicate check
    if (name, ort) in existing_name_ort:
        print(f"DUPLICATE skipped: {name} in {ort}")
        continue
    
    # Score check
    if score < 70:
        print(f"LOW SCORE skipped: {name} ({score})")
        continue
    
    # Generate ID
    lead_id = f"{name.lower().replace(' ', '-').replace('.', '').replace('gmbh', '').strip('-')}-{ort.lower()}"
    
    new_lead = {
        'id': lead_id,
        'name': name,
        'branche': branche,
        'ort': ort,
        'score': score,
        'has_website': lead['has_website'],
        'website_age': None,
        'mobile_friendly': None,
        'has_ssl': None,
        'social_active': True if lead['review_count'] and lead['review_count'] > 50 else False,
        'status': 'new',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'built_at': None,
        'deployed_at': None,
        'outreach_sent': False,
        'url': None
    }
    
    existing_leads.append(new_lead)
    existing_ids.add(lead_id)
    existing_name_ort.add((name, ort))
    new_added.append(new_lead)
    print(f"NEW lead added: {name} ({ort}) -- Score: {score}")

# Update stats
stats = data.get('stats', {})
stats['total_leads'] = len(existing_leads)
stats['approved'] = sum(1 for l in existing_leads if l['score'] >= 70)
stats['built'] = sum(1 for l in existing_leads if l['status'] in ('built', 'live'))
stats['live'] = sum(1 for l in existing_leads if l['status'] == 'live')
stats['outreach_pending'] = sum(1 for l in existing_leads if l['status'] == 'new' and l['score'] >= 70)

data['last_updated'] = datetime.now(timezone.utc).isoformat()
data['leads'] = existing_leads
data['stats'] = stats

with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Save new_qualified for issue creation
with open('leads/new_qualified.json', 'w') as f:
    json.dump(new_added, f, indent=2, ensure_ascii=False)

print(f"\nSummary: {len(new_added)} new leads added, {len(existing_leads)} total leads")
