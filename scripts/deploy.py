#!/usr/bin/env python3
"""
HERMES Sites — Deploy Script
GitHub Pages Deployment via docs/ folder
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
CLIENTS_DIR = BASE_DIR / "clients"
DOCS_DIR = BASE_DIR / "docs"
DATA_DIR = BASE_DIR / "data"

def load_queue():
    queue_file = DATA_DIR / "queue.json"
    if queue_file.exists():
        return json.loads(queue_file.read_text())
    return {"queue": [], "pending_deploys": []}

def save_queue(queue_data):
    queue_file = DATA_DIR / "queue.json"
    queue_data["last_updated"] = subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
    queue_file.write_text(json.dumps(queue_data, indent=2))

def deploy_site(site_id):
    """Deploy a single site to docs/ folder"""
    source = CLIENTS_DIR / site_id / "dist"
    target = DOCS_DIR / site_id
    
    if not source.exists():
        print(f"[ERROR] No dist folder for {site_id}")
        return False
    
    # Clean and copy
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    
    # Ensure .nojekyll
    nojekyll = DOCS_DIR / ".nojekyll"
    nojekyll.touch()
    
    print(f"[OK] Deployed {site_id} -> docs/{site_id}/")
    return True

def deploy_all():
    """Deploy all built sites"""
    queue_data = load_queue()
    deployed = []
    
    for item in queue_data.get("queue", []):
        if item["status"] == "built":
            site_id = item["id"]
            if deploy_site(site_id):
                item["status"] = "deploying"
                item["last_action"] = subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()
                deployed.append(site_id)
    
    # Update index
    update_index()
    
    save_queue(queue_data)
    print(f"[OK] Deployed {len(deployed)} sites: {deployed}")
    return deployed

def update_index():
    """Copy root index.html to docs/ for GitHub Pages"""
    root_index = BASE_DIR / "index.html"
    if root_index.exists():
        shutil.copy2(root_index, DOCS_DIR / "index.html")
        print("[OK] Copied root index.html to docs/")
    else:
        print("[WARN] No root index.html found, skipping dashboard update")

def main():
    if "--github-pages" in sys.argv or "--all" in sys.argv:
        deployed = deploy_all()
        print(f"\n[OK] GitHub Pages deployment complete")
        print(f"[INFO] Push to trigger Pages build: git push origin main")
        return len(deployed)
    
    print("Usage: python deploy.py --github-pages")
    return 0

if __name__ == "__main__":
    sys.exit(main())
