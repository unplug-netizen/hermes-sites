#!/usr/bin/env python3
"""
HERMES Outreach Orchestrator
Generates outreach emails for live sites with outreach_sent=false.
Also corrects queue/leads status if a site is not actually reachable.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
QUEUE_FILE = BASE_DIR / "data" / "queue.json"
LEADS_FILE = BASE_DIR / "data" / "leads.json"
OUTREACH_DIR = BASE_DIR / "outreach"


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_url(url: str) -> bool:
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return result.stdout.strip() == "200"
    except Exception as e:
        print(f"  ⚠️ Reachability check failed for {url}: {e}")
        return False


def generate_email(slug: str) -> Path | None:
    """Run the outreach script for a slug and return the generated HTML file."""
    result = subprocess.run(
        [sys.executable, str(BASE_DIR / "scripts" / "outreach.py"), slug],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"  ❌ outreach.py failed for {slug}:\n{result.stderr}")
        return None
    # The outreach script saves {slug}_outreach.html/.json by default.
    # Rename to the required {slug}-email.html/.json pattern.
    html_src = OUTREACH_DIR / f"{slug}_outreach.html"
    json_src = OUTREACH_DIR / f"{slug}_outreach.json"
    html_dst = OUTREACH_DIR / f"{slug}-email.html"
    json_dst = OUTREACH_DIR / f"{slug}-email.json"
    if html_src.exists():
        html_src.replace(html_dst)
    if json_src.exists():
        json_src.replace(json_dst)
    if html_dst.exists():
        print(f"  ✅ Saved {html_dst}")
        return html_dst
    return None


def main():
    queue = load_json(QUEUE_FILE)
    leads = load_json(LEADS_FILE)

    lead_by_id = {lead["id"]: lead for lead in leads["leads"]}

    generated = []
    corrected = []

    for item in queue.get("queue", []):
        slug = item["id"]
        if item.get("status") != "live":
            continue

        lead = lead_by_id.get(slug)
        if not lead:
            print(f"⚠️ {slug}: live in queue but no lead record found. Reverting to 'built'.")
            item["status"] = "built"
            item["stage"] = "build"
            corrected.append(slug)
            continue

        site_url = lead.get("url") or f"https://unplug-netizen.github.io/hermes-sites/{slug}/"
        print(f"🔍 {slug}: checking {site_url} ...")
        if not check_url(site_url):
            print(f"  ⚠️ Site not reachable. Reverting status to 'built'.")
            item["status"] = "built"
            item["stage"] = "build"
            lead["status"] = "built"
            lead["url"] = None
            corrected.append(slug)
            continue

        if lead.get("outreach_sent") is True:
            print(f"⏭️ {slug}: outreach already sent.")
            continue

        print(f"  📧 Generating outreach email for {slug}")
        email_path = generate_email(slug)
        if email_path:
            lead["outreach_sent"] = True
            generated.append({"slug": slug, "url": site_url, "email": str(email_path)})

    # Update stats in leads.json
    statuses = [lead["status"] for lead in leads["leads"]]
    leads["stats"] = {
        "total_leads": len(leads["leads"]),
        "approved": statuses.count("approved"),
        "built": statuses.count("built"),
        "live": statuses.count("live"),
        "outreach_pending": sum(1 for l in leads["leads"] if not l.get("outreach_sent", False)),
    }
    leads["last_updated"] = datetime.now(timezone.utc).isoformat()
    queue["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    save_json(LEADS_FILE, leads)
    save_json(QUEUE_FILE, queue)

    print("\n--- Summary ---")
    print(f"Generated emails: {len(generated)}")
    for g in generated:
        print(f"  - {g['slug']}: {g['url']} -> {g['email']}")
    print(f"Corrected statuses (not reachable / no lead): {len(corrected)}")
    for c in corrected:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
