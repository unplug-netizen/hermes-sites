#!/usr/bin/env python3
"""Merge new qualified leads into data/leads.json, avoiding duplicates."""
import json
from datetime import datetime, timezone
from pathlib import Path

def main():
    # Load existing leads
    with open('data/leads.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load new qualified leads
    with open('leads/qualified_leads.json', 'r', encoding='utf-8') as f:
        new_leads = json.load(f)

    added = 0
    for lead in new_leads:
        name = lead['name']
        ort = lead['city']
        # Check for duplicates by name+ort
        is_duplicate = any(
            l['name'].lower().strip() == name.lower().strip() and l['ort'].lower().strip() == ort.lower().strip()
            for l in data['leads']
        )
        if not is_duplicate:
            new_id = name.lower().replace(' ', '-').replace('gmbh', '').strip('-')
            data['leads'].append({
                'id': new_id,
                'name': name,
                'branche': lead['category'],
                'ort': ort,
                'score': lead['score'],
                'has_website': lead['has_website'],
                'website_age': None,
                'mobile_friendly': None,
                'has_ssl': None,
                'social_active': True if lead['review_count'] and lead['review_count'] > 50 else False,
                'status': 'new',
                'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'built_at': None,
                'deployed_at': None,
                'outreach_sent': False,
                'url': None
            })
            added += 1

    data['stats']['total_leads'] = len(data['leads'])
    data['stats']['approved'] = len([l for l in data['leads'] if l['score'] >= 70])
    data['last_updated'] = datetime.now(timezone.utc).isoformat()

    with open('data/leads.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'Added {added} new leads')

if __name__ == '__main__':
    main()
