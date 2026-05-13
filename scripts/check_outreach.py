#!/usr/bin/env python3
"""Check which live sites need outreach"""
import json

with open('data/leads.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for lead in data['leads']:
    if lead['status'] == 'live' and not lead.get('outreach_sent', False):
        print(f"{lead['id']} | {lead['name']} | {lead['url']}")
