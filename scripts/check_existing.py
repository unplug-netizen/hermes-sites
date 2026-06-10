#!/usr/bin/env python3
import json

with open('data/leads.json', 'r') as f:
    data = json.load(f)

existing = {(l['name'], l['ort']) for l in data['leads']}
print('Existing leads:', existing)
