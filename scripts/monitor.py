#!/usr/bin/env python3
"""
Hermes Lighthouse CI - Performance Monitoring
Prüft Uptime und Lighthouse Scores für alle live Sites.
"""

import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional

BASE_URL = "https://unplug-netizen.github.io/hermes-sites"
REPORTS_DIR = Path("reports")
QUEUE_FILE = Path("data/queue.json")
THRESHOLD = 90

def run_lighthouse(slug: str) -> Dict:
    url = f"{BASE_URL}/{slug}/"
    output_path = REPORTS_DIR / f"{slug}-lighthouse.json"
    cmd = [
        "lighthouse", url,
        "--output=json",
        "--output-path", str(output_path),
        "--chrome-flags=--headless --no-sandbox --disable-gpu",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--preset=desktop",
        "--max-wait-for-load=60000"
    ]
    print(f"🔍 Lighthouse für {slug}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not output_path.exists():
            print(f"⚠️ Lighthouse Output fehlt für {slug}")
            return {"error": "no output", "stderr": result.stderr}
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        scores = {}
        for cat in ["performance", "accessibility", "best-practices", "seo"]:
            val = data.get("categories", {}).get(cat, {}).get("score")
            scores[cat] = round(val * 100) if val is not None else None
        overall = round(sum(v for v in scores.values() if v is not None) / len([v for v in scores.values() if v is not None]))
        scores["overall"] = overall
        # Überschreibe Report mit kompakterem Format
        report = {
            "slug": slug,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
            "passed": overall >= THRESHOLD
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return report
    except Exception as e:
        print(f"❌ Lighthouse Fehler für {slug}: {e}")
        return {"error": str(e)}

def check_http(slug: str) -> int:
    url = f"{BASE_URL}/{slug}/"
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=30
        )
        code = int(result.stdout.strip())
        print(f"  HTTP {code} für {slug}")
        return code
    except Exception as e:
        print(f"  ❌ HTTP-Check Fehler für {slug}: {e}")
        return 0

def create_github_issue(slug: str, score: int):
    title = f"[ALERT] {slug} Lighthouse Score {score}"
    body = f"Lighthouse Overall Score für **{slug}** ist **{score}** (Threshold: {THRESHOLD}).\n\nBitte prüfen."
    cmd = [
        "gh", "issue", "create",
        "--repo", "unplug-netizen/hermes-sites",
        "--title", title,
        "--body", body
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"  🐛 GitHub Issue erstellt: {result.stdout.strip()}")
        else:
            print(f"  ⚠️ GitHub Issue fehlgeschlagen: {result.stderr.strip()}")
    except Exception as e:
        print(f"  ⚠️ Konnte kein GitHub Issue erstellen: {e}")

def main():
    if not QUEUE_FILE.exists():
        print("❌ queue.json nicht gefunden")
        sys.exit(1)
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue_data = json.load(f)
    live_sites = [item["id"] for item in queue_data.get("queue", []) if item.get("status") == "live"]
    if not live_sites:
        print("ℹ️ Keine live Sites gefunden.")
        sys.exit(0)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sites": {}
    }
    alerts = []
    for slug in live_sites:
        print(f"\n📡 Prüfe {slug}...")
        http_code = check_http(slug)
        site_summary = {
            "http_status": http_code,
            "http_ok": http_code == 200
        }
        if http_code != 200:
            alerts.append(f"{slug}: HTTP {http_code}")
            site_summary["lighthouse"] = {"error": "skipped due to HTTP error"}
        else:
            lh = run_lighthouse(slug)
            site_summary["lighthouse"] = lh
            if "error" in lh:
                alerts.append(f"{slug}: Lighthouse Fehler")
            else:
                overall = lh["scores"].get("overall")
                if overall is not None and overall < THRESHOLD:
                    alerts.append(f"{slug}: Lighthouse Score {overall}")
                    create_github_issue(slug, overall)
        summary["sites"][slug] = site_summary
    summary["alerts"] = alerts
    summary["total_sites"] = len(live_sites)
    summary["alerts_count"] = len(alerts)
    summary_file = REPORTS_DIR / f"monitor-summary-{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H')}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Summary gespeichert: {summary_file}")
    print(f"\n📊 Zusammenfassung:")
    print(f"  Sites geprüft: {len(live_sites)}")
    print(f"  Alerts: {len(alerts)}")
    for a in alerts:
        print(f"    ⚠️ {a}")
    if not alerts:
        print("    ✅ Alle Sites OK")
    # Git add / commit / push
    print("\n🚀 Git push...")
    subprocess.run(["git", "add", "reports/"], check=False)
    commit_msg = f"monitor: Lighthouse {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=False)
    subprocess.run(["git", "push"], check=False)
    print("✅ Fertig.")

if __name__ == "__main__":
    main()
