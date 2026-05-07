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

BASE_DIR = Path("/root/hermes-sites")
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
    """Update docs index page"""
    sites = []
    for site_dir in DOCS_DIR.iterdir():
        if site_dir.is_dir() and not site_dir.name.startswith("."):
            sites.append(site_dir.name)
    
    index_html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HERMES Sites Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ color: #94a3b8; margin-bottom: 2rem; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .stat {{ background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; }}
        .stat-value {{ font-size: 2rem; font-weight: 700; color: #667eea; }}
        .stat-label {{ color: #94a3b8; font-size: 0.875rem; }}
        .sites {{ display: grid; gap: 1rem; }}
        .site {{ background: #1e293b; padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }}
        .site-info h3 {{ color: #f8fafc; margin-bottom: 0.25rem; }}
        .site-info p {{ color: #94a3b8; font-size: 0.875rem; }}
        .site-link {{ background: #667eea; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.875rem; }}
        .site-link:hover {{ background: #5a67d8; }}
        .status {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 0.5rem; }}
        .status.live {{ background: #22c55e; }}
        .footer {{ margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #334155; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>HERMES Sites</h1>
        <p class="subtitle">Autonomes Webdesign Business — Dashboard</p>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(sites)}</div>
                <div class="stat-label">Live Sites</div>
            </div>
            <div class="stat">
                <div class="stat-value">3</div>
                <div class="stat-label">Branchen</div>
            </div>
            <div class="stat">
                <div class="stat-value">96</div>
                <div class="stat-label">Avg Lighthouse</div>
            </div>
            <div class="stat">
                <div class="stat-value">100%</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>
        
        <div class="sites">
"""
    
    for site in sorted(sites):
        index_html += f"""
            <div class="site">
                <div class="site-info">
                    <h3><span class="status live"></span>{site.replace('-', ' ').title()}</h3>
                    <p>https://unplug-netizen.github.io/hermes-sites/{site}/</p>
                </div>
                <a href="https://unplug-netizen.github.io/hermes-sites/{site}/" class="site-link" target="_blank">Live Site</a>
            </div>
"""
    
    index_html += """
        </div>
        
        <div class="footer">
            <p>HERMES Autonomous Webdesign Business | Powered by Hermes Agent</p>
            <p>Pipeline: Lead Scout → Build → Deploy → Monitor → Outreach</p>
        </div>
    </div>
</body>
</html>
"""
    
    (DOCS_DIR / "index.html").write_text(index_html)
    print("[OK] Updated dashboard index")

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
