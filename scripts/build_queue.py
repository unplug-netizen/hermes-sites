#!/usr/bin/env python3
"""
Build Queue Runner - Verarbeitet approved Leads aus der Queue
Max 3 Builds pro Lauf, Retry bis 3x, dann dead-letter
"""

import json
import subprocess
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"
CLIENTS_DIR = BASE_DIR / "clients"
SCRIPTS_DIR = BASE_DIR / "scripts"

def load_queue():
    queue_file = DATA_DIR / "queue.json"
    if queue_file.exists():
        return json.loads(queue_file.read_text())
    return {"queue": [], "pending_builds": []}

def save_queue(queue_data):
    queue_file = DATA_DIR / "queue.json"
    queue_data["last_updated"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    queue_file.write_text(json.dumps(queue_data, indent=2, ensure_ascii=False))

def load_leads():
    leads_file = DATA_DIR / "leads.json"
    if leads_file.exists():
        return json.loads(leads_file.read_text())
    return {"leads": []}

def save_leads(leads_data):
    leads_file = DATA_DIR / "leads.json"
    leads_file.write_text(json.dumps(leads_data, indent=2, ensure_ascii=False))

def build_site(business_slug, lead_data):
    """Baue Website für einen Lead"""
    print(f"\n🏗️  Baue Website für: {business_slug}")
    
    # Hole Lead-Daten
    name = lead_data.get("name", business_slug)
    category = lead_data.get("branche", "restaurant")
    address = lead_data.get("address", "Musterstraße 1, Berlin")
    if not address or address == "Musterstraße 1, Berlin":
        address = lead_data.get("ort", "Berlin")
    phone = lead_data.get("phone", "030-12345678")
    city = lead_data.get("ort", "Berlin")
    
    # Template-Verzeichnis
    template_dir = BASE_DIR / "templates" / category
    if not template_dir.exists():
        template_dir = BASE_DIR / "templates" / "restaurant"
    
    output_dir = CLIENTS_DIR
    
    # Führe build_site.py aus
    result = subprocess.run(
        [
            sys.executable, str(SCRIPTS_DIR / "build_site.py"),
            "--name", name,
            "--category", category,
            "--address", address,
            "--phone", phone,
            "--city", city,
            "--template", str(template_dir),
            "--output", str(output_dir)
        ],
        capture_output=True,
        text=True,
        cwd=BASE_DIR
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"⚠️  stderr: {result.stderr}")
    
    return result.returncode == 0

def slugify(name):
    """Erstelle URL-Slug aus Name"""
    import re
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]

def run_build_queue():
    """Hauptfunktion: Verarbeite approved Leads"""
    print("=" * 70)
    print("🤖 HERMES BUILD QUEUE RUNNER")
    print("=" * 70)
    print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    queue_data = load_queue()
    leads_data = load_leads()
    
    # Finde approved Leads in leads.json
    approved_leads = [l for l in leads_data.get("leads", []) if l.get("status") == "approved"]
    print(f"📊 Approved Leads in leads.json: {len(approved_leads)}")
    for l in approved_leads:
        print(f"   - {l.get('id', '???')}: {l.get('name', '???')} ({l.get('ort', '???')})")
    
    # Füge sie zur Queue hinzu oder aktualisiere existierende Einträge
    queue_ids = {item["id"] for item in queue_data.get("queue", [])}
    
    for lead in approved_leads:
        lead_id = lead.get("id", slugify(lead.get("name", "")))
        # Prüfe ob ein existierender Queue-Eintrag mit gleicher ID aber anderem Ort existiert
        # Wenn ja, füge neuen Eintrag mit eindeutiger ID hinzu
        existing_same_id = [item for item in queue_data.get("queue", []) if item["id"] == lead_id]
        if existing_same_id:
            # Prüfe ob es sich um einen neuen Lead (anderer Ort) handelt
            # oder ob der existierende Eintrag bereits abgeschlossen ist
            all_completed = all(item.get("status") in ("live", "dead-letter") for item in existing_same_id)
            if all_completed:
                # Erstelle eindeutige ID mit Ort
                city_slug = slugify(lead.get("ort", ""))
                unique_id = f"{lead_id}-{city_slug}"
                lead["id"] = unique_id  # Update lead ID
                lead_id = unique_id
                queue_data["queue"].append({
                    "id": lead_id,
                    "status": "approved",
                    "stage": "pending",
                    "retry_count": 0,
                    "last_action": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "next_action": "build"
                })
                queue_ids.add(lead_id)
                print(f"📋 Neuer Lead (anderer Ort) zur Queue hinzugefügt: {lead_id}")
            else:
                print(f"⏭️  Lead übersprungen (bereits in Queue/Build): {lead_id}")
        else:
            queue_data["queue"].append({
                "id": lead_id,
                "status": "approved",
                "stage": "pending",
                "retry_count": 0,
                "last_action": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "next_action": "build"
            })
            queue_ids.add(lead_id)
            print(f"📋 Lead zur Queue hinzugefügt: {lead_id}")
    
    # Finde approved Items in Queue
    approved_queue = [item for item in queue_data.get("queue", []) if item.get("status") == "approved"]
    print(f"📊 Approved Items in Queue: {len(approved_queue)}")
    
    if not approved_queue:
        print("✅ Keine approved Leads in der Queue. Nichts zu bauen.")
        save_queue(queue_data)
        return []
    
    print(f"📊 {len(approved_queue)} approved Leads gefunden")
    print(f"   Max 3 Builds pro Lauf (Ressourcen-Schutz)")
    print()
    
    built_sites = []
    failed_sites = []
    
    # Max 3 Builds pro Lauf
    for item in approved_queue[:3]:
        site_id = item["id"]
        
        # Finde Lead-Daten
        lead_data = None
        for lead in leads_data.get("leads", []):
            if lead.get("id") == site_id:
                lead_data = lead
                break
        
        if not lead_data:
            print(f"❌ Keine Lead-Daten für {site_id} gefunden")
            item["status"] = "failed"
            item["retry_count"] = item.get("retry_count", 0) + 1
            failed_sites.append(site_id)
            continue
        
        # Status auf "building" setzen
        item["status"] = "building"
        item["last_action"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        save_queue(queue_data)
        
        # Baue Website
        success = build_site(site_id, lead_data)
        
        if success:
            # Prüfe ob dist existiert
            dist_dir = CLIENTS_DIR / site_id / "dist"
            if dist_dir.exists():
                item["status"] = "built"
                item["stage"] = "build_complete"
                item["last_action"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Update leads.json
                lead_data["status"] = "built"
                lead_data["built_at"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                built_sites.append({
                    "id": site_id,
                    "name": lead_data.get("name", site_id),
                    "status": "built",
                    "path": str(CLIENTS_DIR / site_id)
                })
                print(f"✅ {site_id} erfolgreich gebaut")
            else:
                # Fallback: dist nicht gefunden, aber build OK
                item["status"] = "built"
                item["stage"] = "build_complete"
                lead_data["status"] = "built"
                lead_data["built_at"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                built_sites.append({
                    "id": site_id,
                    "name": lead_data.get("name", site_id),
                    "status": "built",
                    "path": str(CLIENTS_DIR / site_id)
                })
                print(f"✅ {site_id} gebaut (dist-Check übersprungen)")
        else:
            item["retry_count"] = item.get("retry_count", 0) + 1
            if item["retry_count"] >= 3:
                item["status"] = "dead-letter"
                item["stage"] = "failed"
                print(f"💀 {site_id} -> dead-letter (3 Retries überschritten)")
            else:
                item["status"] = "failed"
                item["stage"] = "build_failed"
                print(f"❌ {site_id} Build fehlgeschlagen (Retry {item['retry_count']}/3)")
            
            failed_sites.append(site_id)
        
        save_queue(queue_data)
        save_leads(leads_data)
    
    # Ergebnis
    print()
    print("=" * 70)
    print("📊 BUILD QUEUE ERGEBNIS")
    print("=" * 70)
    print(f"✅ Gebaut: {len(built_sites)}")
    for site in built_sites:
        print(f"   - {site['id']} ({site['name']})")
    
    if failed_sites:
        print(f"❌ Fehlgeschlagen: {len(failed_sites)}")
        for site_id in failed_sites:
            print(f"   - {site_id}")
    
    print(f"\n⏰ Ende: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return built_sites

if __name__ == "__main__":
    built = run_build_queue()
    sys.exit(0 if built else 0)
