#!/usr/bin/env python3
"""Merge new leads into leads.json, avoiding duplicates."""
import json
from datetime import datetime, timezone
from pathlib import Path

def main():
    with open('data/leads.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_leads = data['leads']
    existing_names = {(l['name'], l['ort']) for l in existing_leads}

    with open('leads/qualified_leads.json', 'r', encoding='utf-8') as f:
        new_leads_raw = json.load(f)

    new_leads = []
    for l in new_leads_raw:
        if (l['name'], l['city']) not in existing_names and l['score'] >= 70:
            new_leads.append({
                'id': l['place_id'],
                'name': l['name'],
                'branche': l['category'],
                'ort': l['city'],
                'score': l['score'],
                'has_website': l['has_website'],
                'website_age': None,
                'mobile_friendly': None,
                'has_ssl': None,
                'social_active': l['review_count'] > 50 if l['review_count'] else False,
                'status': 'new',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'built_at': None,
                'deployed_at': None,
                'outreach_sent': False,
                'url': None
            })

    print(f'New leads to add: {len(new_leads)}')
    for nl in new_leads:
        print(f"  - {nl['name']} ({nl['ort']}) Score: {nl['score']}")

    if new_leads:
        existing_leads.extend(new_leads)
        data['last_updated'] = datetime.now(timezone.utc).isoformat()
        data['stats']['total_leads'] = len(existing_leads)
        data['stats']['approved'] = len([l for l in existing_leads if l['score'] >= 70])

        with open('data/leads.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print('Saved to data/leads.json')
    else:
        print('No new leads to add.')

    return new_leads

if __name__ == '__main__':
    main()
