#!/usr/bin/env python3
"""
Hermes Pipeline - End-to-End Automation
Verbindet Lead-Scout → Content-Gen → Build → Deploy
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class HermesPipeline:
    """Hauptpipeline für autonome Website-Generierung"""
    
    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.leads_dir = base_dir / "leads"
        self.clients_dir = base_dir / "clients"
        self.pipeline_dir = base_dir / "pipeline"
        
    def run(self):
        """Führe komplette Pipeline aus"""
        print("=" * 70)
        print("🤖 HERMES AUTONOMOUS WEBDESIGN PIPELINE")
        print("=" * 70)
        print(f"⏰ Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Schritt 1: Lead-Scouting
        leads = self._run_scout()
        
        if not leads:
            print("❌ Keine qualifizierten Leads gefunden. Pipeline beendet.")
            return
        
        # Schritt 2: Website für ersten Lead bauen
        lead = leads[0]
        site_path = self._build_site(lead)
        
        # Schritt 3: Deploy (GitHub Pages / Netlify)
        deploy_url = self._deploy(site_path, lead)
        
        # Schritt 4: Report
        self._generate_report(lead, deploy_url)
        
        print()
        print("=" * 70)
        print("✅ PIPELINE ABGESCHLOSSEN")
        print("=" * 70)
        
    def _run_scout(self) -> list:
        """Führe Lead-Scout aus"""
        print("📡 SCHRETT 1: Lead-Scouting")
        print("-" * 70)
        
        result = subprocess.run(
            [sys.executable, "scripts/lead_scout.py", "--city", "Berlin", "--category", "restaurant"],
            capture_output=True,
            text=True,
            cwd=self.base_dir
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(f"⚠️  Scout-Fehler: {result.stderr}")
        
        # Lade qualifizierte Leads
        qualified_file = self.leads_dir / "qualified_leads.json"
        if qualified_file.exists():
            with open(qualified_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _build_site(self, lead: dict) -> Path:
        """Baue Website für Lead"""
        print("\n🏗️  SCHRETT 2: Website-Generierung")
        print("-" * 70)
        
        name = lead.get("name", "Unknown")
        category = lead.get("category", "restaurant")
        address = lead.get("address", "Berlin")
        phone = lead.get("phone", "030-12345678")
        city = lead.get("city", "Berlin")
        
        result = subprocess.run(
            [
                sys.executable, "scripts/build_site.py",
                "--name", name,
                "--category", category,
                "--address", address,
                "--phone", phone,
                "--city", city,
                "--template", f"./templates/{category}",
                "--output", "./clients"
            ],
            capture_output=True,
            text=True,
            cwd=self.base_dir
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(f"⚠️  Build-Fehler: {result.stderr}")
        
        # Rückgabe des erwarteten Pfads
        slug = self._slugify(name)
        return self.clients_dir / slug
    
    def _deploy(self, site_path: Path, lead: dict) -> str:
        """Deploy Website"""
        print("\n🚀 SCHRETT 3: Deployment")
        print("-" * 70)
        
        # Für MVP: Lokale Vorschau
        # In Produktion: GitHub Pages, Netlify, oder Vercel
        
        slug = self._slugify(lead.get("name", "site"))
        
        # Erstelle statische Vorschau
        preview_dir = self.base_dir / "preview" / slug
        preview_dir.mkdir(parents=True, exist_ok=True)
        
        # Kopiere dist-Inhalt
        dist_dir = site_path / "dist"
        if dist_dir.exists():
            import shutil
            if preview_dir.exists():
                shutil.rmtree(preview_dir)
            shutil.copytree(dist_dir, preview_dir)
        
        # Erstelle einfache index.html falls nicht vorhanden
        if not (preview_dir / "index.html").exists():
            self._create_fallback_html(preview_dir, lead)
        
        url = f"file://{preview_dir.absolute()}/index.html"
        print(f"📁 Lokale Vorschau: {url}")
        
        # GitHub Push (optional)
        self._push_to_github(site_path, slug)
        
        return url
    
    def _create_fallback_html(self, preview_dir: Path, lead: dict):
        """Erstelle Fallback-HTML falls Astro-Build fehlschlägt"""
        name = lead.get("name", "Business")
        address = lead.get("address", "")
        phone = lead.get("phone", "")
        
        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-4xl mx-auto p-8">
        <h1 class="text-4xl font-bold mb-4">{name}</h1>
        <p class="text-gray-600 mb-4">📍 {address}</p>
        <p class="text-gray-600 mb-8">📞 {phone}</p>
        <div class="bg-blue-100 p-4 rounded">
            <p>🚧 Vollständige Website wird generiert...</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(preview_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
    
    def _push_to_github(self, site_path: Path, slug: str):
        """Push zu GitHub (optional)"""
        print(f"📤 GitHub Push für {slug}...")
        
        # Prüfe ob gh CLI verfügbar
        result = subprocess.run(
            ["which", "gh"],
            capture_output=True
        )
        
        if result.returncode != 0:
            print("   ⚠️  gh CLI nicht installiert - überspringe")
            return
        
        # Erstelle Repo und pushe
        # (In echter Implementierung: gh repo create + push)
        print(f"   ℹ️  Repo würde erstellt: hermes-sites/{slug}")
    
    def _generate_report(self, lead: dict, deploy_url: str):
        """Generiere Pipeline-Report"""
        print("\n📊 SCHRETT 4: Report")
        print("-" * 70)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "lead": lead,
            "deploy_url": deploy_url,
            "status": "success"
        }
        
        report_file = self.pipeline_dir / "last_run.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Report gespeichert: {report_file}")
        print(f"\n🎯 ZUSAMMENFASSUNG:")
        print(f"   Unternehmen: {lead.get('name')}")
        print(f"   Score: {lead.get('score', 0)}/100")
        print(f"   Vorschau: {deploy_url}")
    
    def _slugify(self, name: str) -> str:
        """Erstelle URL-Slug"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]


def main():
    pipeline = HermesPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
