#!/usr/bin/env python3
"""
Hermes Monitor - Uptime & Performance Monitoring
Tracks site health and sends alerts
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

@dataclass
class SiteCheck:
    url: str
    status_code: int
    response_time_ms: float
    is_up: bool
    timestamp: str
    error: Optional[str] = None

@dataclass
class LighthouseScore:
    performance: int
    accessibility: int
    best_practices: int
    seo: int
    overall: int
    timestamp: str

class Monitor:
    """Monitors deployed websites for uptime and performance"""
    
    def __init__(self, sites_file: Path = Path("pipeline/deployed_sites.json")):
        self.sites_file = sites_file
        self.sites = self._load_sites()
        self.results_dir = Path("docs/reports")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_sites(self) -> List[dict]:
        """Load deployed sites list"""
        if self.sites_file.exists():
            with open(self.sites_file, "r") as f:
                return json.load(f)
        return []
    
    def check_uptime(self, url: str, timeout: int = 10) -> SiteCheck:
        """Check if a site is accessible"""
        start = time.time()
        try:
            response = urllib.request.urlopen(url, timeout=timeout)
            elapsed = (time.time() - start) * 1000
            return SiteCheck(
                url=url,
                status_code=response.getcode(),
                response_time_ms=round(elapsed, 2),
                is_up=response.getcode() == 200,
                timestamp=datetime.now().isoformat()
            )
        except urllib.error.HTTPError as e:
            elapsed = (time.time() - start) * 1000
            return SiteCheck(
                url=url,
                status_code=e.code,
                response_time_ms=round(elapsed, 2),
                is_up=False,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SiteCheck(
                url=url,
                status_code=0,
                response_time_ms=round(elapsed, 2),
                is_up=False,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def check_all_sites(self) -> List[SiteCheck]:
        """Check all deployed sites"""
        results = []
        for site in self.sites:
            url = site.get("url", "")
            if url:
                print(f"🔍 Checking {site.get('name', url)}...")
                check = self.check_uptime(url)
                results.append(check)
                status = "✅ UP" if check.is_up else "❌ DOWN"
                print(f"   {status} ({check.status_code}) - {check.response_time_ms}ms")
        return results
    
    def run_lighthouse_check(self, url: str) -> Optional[LighthouseScore]:
        """Run Lighthouse CI check on a site"""
        try:
            import subprocess
            result = subprocess.run(
                ["lighthouse", url, "--output=json", "--chrome-flags=--headless", "--quiet"],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                report = json.loads(result.stdout)
                categories = report.get("categories", {})
                
                perf = int(categories.get("performance", {}).get("score", 0) * 100)
                a11y = int(categories.get("accessibility", {}).get("score", 0) * 100)
                bp = int(categories.get("best-practices", {}).get("score", 0) * 100)
                seo = int(categories.get("seo", {}).get("score", 0) * 100)
                overall = (perf + a11y + bp + seo) // 4
                
                return LighthouseScore(
                    performance=perf,
                    accessibility=a11y,
                    best_practices=bp,
                    seo=seo,
                    overall=overall,
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            print(f"⚠️  Lighthouse check failed: {e}")
        return None
    
    def generate_report(self, checks: List[SiteCheck]) -> Path:
        """Generate monitoring report"""
        report_file = self.results_dir / f"uptime_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_sites": len(checks),
            "sites_up": sum(1 for c in checks if c.is_up),
            "sites_down": sum(1 for c in checks if not c.is_up),
            "checks": [asdict(c) for c in checks]
        }
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Markdown summary
        md_file = self.results_dir / "uptime_report.md"
        with open(md_file, "w") as f:
            f.write("# 📊 Uptime Monitoring Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Total Sites | {report['total_sites']} |\n")
            f.write(f"| Sites Up | {report['sites_up']} ✅ |\n")
            f.write(f"| Sites Down | {report['sites_down']} ❌ |\n\n")
            f.write("## Site Details\n\n")
            f.write("| Site | Status | Code | Response Time |\n")
            f.write("|------|--------|------|---------------|\n")
            for check in checks:
                status = "✅ UP" if check.is_up else "❌ DOWN"
                f.write(f"| {check.url} | {status} | {check.status_code} | {check.response_time_ms}ms |\n")
        
        print(f"📊 Report saved: {report_file}")
        return report_file
    
    def add_site(self, name: str, url: str, site_id: str):
        """Add a new site to monitoring"""
        self.sites.append({
            "name": name,
            "url": url,
            "site_id": site_id,
            "added": datetime.now().isoformat()
        })
        self._save_sites()
    
    def _save_sites(self):
        """Save sites list"""
        self.sites_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.sites_file, "w") as f:
            json.dump(self.sites, f, indent=2)


def main():
    """CLI for monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Site Monitor")
    parser.add_argument("--check", action="store_true", help="Check all sites")
    parser.add_argument("--add", help="Add site to monitoring (format: name,url,id)")
    parser.add_argument("--lighthouse", help="Run Lighthouse on specific URL")
    
    args = parser.parse_args()
    
    monitor = Monitor()
    
    if args.add:
        parts = args.add.split(",")
        if len(parts) == 3:
            monitor.add_site(parts[0], parts[1], parts[2])
            print(f"✅ Added {parts[0]} to monitoring")
        else:
            print("❌ Format: name,url,site_id")
    
    if args.check:
        checks = monitor.check_all_sites()
        monitor.generate_report(checks)
    
    if args.lighthouse:
        print(f"🔍 Running Lighthouse on {args.lighthouse}...")
        score = monitor.run_lighthouse_check(args.lighthouse)
        if score:
            print(f"\n📊 Lighthouse Scores:")
            print(f"   Performance: {score.performance}")
            print(f"   Accessibility: {score.accessibility}")
            print(f"   Best Practices: {score.best_practices}")
            print(f"   SEO: {score.seo}")
            print(f"   Overall: {score.overall}")


if __name__ == "__main__":
    main()
