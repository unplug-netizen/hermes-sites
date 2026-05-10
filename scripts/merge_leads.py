#!/usr/bin/env python3
"""Merge new qualified leads into leads.json with deduplication."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

def main():
    # Load existing leads
    with open('data/leads.json', 'r') as f:
        existing = json.load(f)

    # Load new qualified leads
    with open('data/leads_out/qualified_leads.json', 'r') as f:
        new_leads = json.load(f)

    existing_names = { (l['name'], l['ort']) for l in existing['leads'] }
    new_added = []

    for nl in new_leads:
        key = (nl['name'], nl['city'])
        if key not in existing_names:
            lead_id = nl['name'].lower().replace(' ', '-').replace('ü', 'u').replace('ö', 'o').replace('ä', 'a').replace('ß', 'ss')
            entry = {
                'id': lead_id,
                'name': nl['name'],
                'branche': nl['category'],
                'ort': nl['city'],
                'score': nl['score'],
                'has_website': nl['has_website'],
                'website_age': None,
                'mobile_friendly': None,
                'has_ssl': None,
                'social_active': True if nl['review_count'] and nl['review_count'] > 50 else False,
                'status': 'new',
                'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'built_at': None,
                'deployed_at': None,
                'outreach_sent': False,
                'url': None
            }
            existing['leads'].append(entry)
            new_added.append(entry)
            print(f"Neuer Lead: {nl['name']} | Score: {nl['score']} | {nl['city']}")
        else:
            print(f"Duplikat übersprungen: {nl['name']} in {nl['city']}")

    existing['last_updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    existing['stats']['total_leads'] = len(existing['leads'])
    existing['stats']['approved'] = len([l for l in existing['leads'] if l['score'] >= 70])

    with open('data/leads.json', 'w') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\nGesamt: {len(new_added)} neue Leads hinzugefügt")
    # Write list of new lead IDs for downstream processing
    with open('data/new_lead_ids.txt', 'w') as f:
        for l in new_added:
            f.write(l['id'] + '\n')

if __name__ == '__main__':
    main()
