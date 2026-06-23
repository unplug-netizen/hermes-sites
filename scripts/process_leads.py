import json
from datetime import datetime

# Load existing leads
with open('data/leads.json', 'r') as f:
    data = json.load(f)

existing_leads = data['leads']
existing_ids = {l['id'] for l in existing_leads}

# Load new qualified leads
with open('leads/qualified_leads.json', 'r') as f:
    new_leads_raw = json.load(f)

new_leads = []
for lead in new_leads_raw:
    lead_id = lead['name'].lower().replace(' ', '-')
    if lead['city']:
        lead_id += '-' + lead['city'].lower()
    
    # Check for duplicate by id
    if lead_id in existing_ids:
        print(f'SKIP (duplicate): {lead["name"]} in {lead["city"]}')
        continue
    
    # Also check by name+city combination
    is_duplicate = any(
        l['name'] == lead['name'] and l['ort'] == lead['city']
        for l in existing_leads
    )
    if is_duplicate:
        print(f'SKIP (duplicate name+ort): {lead["name"]} in {lead["city"]}')
        continue
    
    new_lead = {
        'id': lead_id,
        'name': lead['name'],
        'branche': lead['category'],
        'ort': lead['city'],
        'score': lead['score'],
        'has_website': lead['has_website'],
        'website_age': None,
        'mobile_friendly': None,
        'has_ssl': None,
        'social_active': True if lead['review_count'] and lead['review_count'] > 50 else False,
        'status': 'approved',
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'built_at': None,
        'deployed_at': None,
        'outreach_sent': False,
        'url': None
    }
    new_leads.append(new_lead)
    existing_leads.append(new_lead)
    existing_ids.add(lead_id)
    print(f'ADD: {lead["name"]} ({lead["city"]}) - Score {lead["score"]}')

# Update stats
data['stats']['total_leads'] = len(existing_leads)
data['stats']['approved'] = len([l for l in existing_leads if l['status'] == 'approved'])
data['last_updated'] = datetime.utcnow().isoformat() + '+00:00'

with open('data/leads.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'\nTotal leads: {len(existing_leads)}')
print(f'New leads added: {len(new_leads)}')
