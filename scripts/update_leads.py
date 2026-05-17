#!/usr/bin/env python3
"""Update leads.json timestamp and append new qualified leads."""
import json
from datetime import datetime, timezone
from pathlib import Path

NOW = datetime.now(timezone.utc).isoformat()

# Load existing leads
leads_path = Path("data/leads.json")
with open(leads_path, "r", encoding="utf-8") as f:
    data = json.load(f)

existing_ids = {lead["id"] for lead in data["leads"]}
existing_names = {(lead["name"], lead["ort"]) for lead in data["leads"]}

# Load new qualified leads
scout_path = Path("data/scout/qualified_leads.json")
with open(scout_path, "r", encoding="utf-8") as f:
    new_leads_raw = json.load(f)

new_leads = []
for raw in new_leads_raw:
    lead_id = raw["name"].lower().replace(" ", "-").replace("ß", "ss").replace("ü", "ue").replace("ö", "oe").replace("ä", "ae")
    if lead_id in existing_ids:
        continue
    if (raw["name"], raw["city"]) in existing_names:
        continue

    lead = {
        "id": lead_id,
        "name": raw["name"],
        "branche": raw["category"],
        "ort": raw["city"],
        "score": raw["score"],
        "has_website": raw["has_website"],
        "website_age": None,
        "mobile_friendly": None,
        "has_ssl": None,
        "social_active": raw.get("social_active", None),
        "status": "new",
        "created_at": NOW,
        "built_at": None,
        "deployed_at": None,
        "outreach_sent": False,
        "url": None
    }
    new_leads.append(lead)
    data["leads"].append(lead)

# Update stats
data["last_updated"] = NOW
data["stats"]["total_leads"] = len(data["leads"])
data["stats"]["approved"] = sum(1 for l in data["leads"] if l["score"] >= 70)

with open(leads_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_leads)} new leads.")
for l in new_leads:
    print(f"  - {l['name']} ({l['ort']}) — Score: {l['score']}")
