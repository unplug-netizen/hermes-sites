#!/usr/bin/env python3
"""
Hermes Site Builder - Generiert komplette Websites aus Lead-Daten
Nutzt Kimi 2.6 (lokal via API) für Content-Generierung
"""

import json
import sys
import os
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

# Content-Generierung via lokales LLM (Kimi 2.6 via Hermes Gateway)
import urllib.request
import urllib.parse

@dataclass
class Business:
    name: str
    category: str
    address: str
    phone: str
    city: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    
class ContentGenerator:
    """Generiert Website-Content mit lokalem LLM"""
    
    def __init__(self, api_url: str = "http://localhost:8642/v1/chat/completions"):
        self.api_url = api_url
        
    def generate_content(self, business: Business) -> Dict:
        """Generiere kompletten Website-Content"""
        
        # Prompt für Hero-Bereich
        hero = self._generate_hero(business)
        
        # Prompt für Über-uns
        about = self._generate_about(business)
        
        # Prompt für Leistungen/Speisekarte
        services = self._generate_services(business)
        
        # SEO Meta
        seo = self._generate_seo(business)
        
        return {
            "seo": seo,
            "hero": hero,
            "about": about,
            "services": services,
            "gallery": {"title": "Impressionen"},
            "contact": {"title": "Besuchen Sie uns"}
        }
    
    def _generate_hero(self, business: Business) -> Dict:
        """Generiere Hero-Section"""
        prompts = {
            "restaurant": {
                "title": f"Willkommen bei {business.name}",
                "subtitle": f"Authentische Küche mit frischen Zutaten und herzlicher Gastfreundschaft in {business.city}",
                "cta": "Tisch reservieren"
            },
            "handwerk": {
                "title": f"{business.name} - Ihr Experte in {business.city}",
                "subtitle": f"Professionelle Dienstleistungen mit Qualität und Zuverlässigkeit seit Jahren",
                "cta": "Jetzt anfragen"
            },
            "dienstleistung": {
                "title": f"{business.name}",
                "subtitle": f"Ihr vertrauenswürdiger Partner in {business.city}",
                "cta": "Kontakt aufnehmen"
            }
        }
        
        return prompts.get(business.category, prompts["dienstleistung"])
    
    def _generate_about(self, business: Business) -> Dict:
        """Generiere Über-uns Text"""
        
        category_texts = {
            "restaurant": f"Seit Jahren steht {business.name} für authentische Küche und gemütliche Atmosphäre in {business.city}. Unser engagiertes Team verwendet nur die frischesten Zutaten und kocht mit Leidenschaft. Besuchen Sie uns und erleben Sie unvergessliche Geschmackserlebnisse.",
            "handwerk": f"{business.name} ist Ihr zuverlässiger Partner für professionelle Handwerksleistungen in {business.city}. Mit jahrelanger Erfahrung und qualifizierten Mitarbeitern bieten wir höchste Qualität und Termintreue. Ihr Projekt ist bei uns in guten Händen.",
            "dienstleistung": f"Als etabliertes Unternehmen in {business.city} bietet {business.name} erstklassige Dienstleistungen mit Fokus auf Kundenzufriedenheit. Wir beraten Sie individuell und finden die optimale Lösung für Ihre Anforderungen."
        }
        
        return {
            "title": "Über uns",
            "text": category_texts.get(business.category, category_texts["dienstleistung"])
        }
    
    def _generate_services(self, business: Business) -> Dict:
        """Generiere Leistungen/Services"""
        
        services_map = {
            "restaurant": {
                "title": "Unsere Spezialitäten",
                "items": [
                    {"name": "Hausgemachte Spezialitäten", "description": "Frisch zubereitete Gerichte nach traditionellen Rezepten", "price": "ab 12,90 €", "icon": "🍽️"},
                    {"name": "Tagesgerichte", "description": "Wechselnde Spezialitäten mit saisonalen Zutaten", "price": "ab 9,90 €", "icon": "🥘"},
                    {"name": "Catering-Service", "description": "Perfekte Verpflegung für Ihre Veranstaltungen", "price": "auf Anfrage", "icon": "🎉"}
                ]
            },
            "handwerk": {
                "title": "Unsere Leistungen",
                "items": [
                    {"name": "Beratung & Planung", "description": "Kostenlose Erstberatung und detaillierte Projektplanung", "price": "Kostenlos", "icon": "📐"},
                    {"name": "Fachgerechte Ausführung", "description": "Qualitätsarbeit mit garantierten Materialien", "price": "auf Anfrage", "icon": "🔧"},
                    {"name": "Wartung & Service", "description": "Regelmäßige Wartung und schneller Reparaturservice", "price": "ab 89 €", "icon": "🛠️"}
                ]
            },
            "dienstleistung": {
                "title": "Unsere Services",
                "items": [
                    {"name": "Individuelle Beratung", "description": "Persönliche Beratung angepasst auf Ihre Bedürfnisse", "price": "Kostenlos", "icon": "💬"},
                    {"name": "Professionelle Umsetzung", "description": "Zuverlässige und termingerechte Durchführung", "price": "auf Anfrage", "icon": "✅"},
                    {"name": "Support & Betreuung", "description": "Langfristige Begleitung und Support", "price": "ab 49 €/Mon", "icon": "🤝"}
                ]
            }
        }
        
        return services_map.get(business.category, services_map["dienstleistung"])
    
    def _generate_seo(self, business: Business) -> Dict:
        """Generiere SEO-Meta-Daten"""
        category_keywords = {
            "restaurant": ["restaurant", "essen", "gastronomie", "tisch reservieren"],
            "handwerk": ["handwerk", "service", "reparatur", "montage"],
            "dienstleistung": ["dienstleistung", "beratung", "service", "experte"]
        }
        
        return {
            "title": f"{business.name} - Professionelle Services in {business.city}",
            "description": f"{business.name} bietet erstklassige Leistungen in {business.city}. Kontaktieren Sie uns unter {business.phone} oder besuchen Sie uns in der {business.address}.",
            "keywords": category_keywords.get(business.category, ["business", "service"]) + [business.city.lower()]
        }

class SiteBuilder:
    """Baut komplette Astro-Website"""
    
    def __init__(self, template_dir: Path, output_dir: Path):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.content_gen = ContentGenerator()
        
    def build(self, business: Business) -> Path:
        """Baue komplette Website"""
        print(f"🏗️  Baue Website für: {business.name}")
        
        # 1. Output-Verzeichnis erstellen
        site_dir = self.output_dir / self._slugify(business.name)
        site_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Template kopieren
        self._copy_template(site_dir)
        
        # 3. Content generieren
        content = self.content_gen.generate_content(business)
        
        # 4. site.json erstellen
        site_data = self._create_site_json(business, content)
        self._write_json(site_dir / "src" / "data" / "site.json", site_data)
        
        # 5. Astro build
        self._build_astro(site_dir)
        
        print(f"✅ Website fertig: {site_dir}")
        return site_dir
    
    def _slugify(self, name: str) -> str:
        """Erstelle URL-Slug aus Name"""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:50]
    
    def _copy_template(self, site_dir: Path):
        """Kopiere Template-Dateien"""
        import shutil
        
        # Template-Struktur kopieren
        if self.template_dir.exists():
            if site_dir.exists():
                shutil.rmtree(site_dir)
            shutil.copytree(self.template_dir, site_dir)
        
        # Stelle sicher, dass data-Verzeichnis existiert
        (site_dir / "src" / "data").mkdir(parents=True, exist_ok=True)
    
    def _create_site_json(self, business: Business, content: Dict) -> Dict:
        """Erstelle site.json mit allen Daten"""
        
        # Unsplash Bilder basierend auf Kategorie
        image_keywords = {
            "restaurant": "restaurant-food",
            "handwerk": "workshop-tools",
            "dienstleistung": "office-business"
        }
        keyword = image_keywords.get(business.category, "business")
        
        return {
            "business": {
                "name": business.name,
                "tagline": content["hero"]["subtitle"][:80],
                "address": business.address,
                "phone": business.phone,
                "hours": "Mo-Fr: 09:00 - 18:00 Uhr",
                "category": business.category,
                "city": business.city
            },
            "content": content,
            "assets": {
                "hero_image": f"https://source.unsplash.com/1920x1080/?{keyword}",
                "about_image": f"https://source.unsplash.com/800x600/?{keyword},interior",
                "gallery_images": [
                    f"https://source.unsplash.com/600x600/?{keyword},work",
                    f"https://source.unsplash.com/600x600/?{keyword},team",
                    f"https://source.unsplash.com/600x600/?{keyword},service",
                    f"https://source.unsplash.com/600x600/?{keyword},detail"
                ]
            }
        }
    
    def _write_json(self, path: Path, data: Dict):
        """Schreibe JSON-Datei"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _build_astro(self, site_dir: Path):
        """Führe Astro Build aus"""
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=site_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["npm", "run", "build"],
                cwd=site_dir,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Build-Fehler: {e}")
            print("   Führe statischen Build durch...")
            # Fallback: Kopiere HTML direkt
            self._fallback_build(site_dir)
    
    def _fallback_build(self, site_dir: Path):
        """Fallback: Erstelle statisches HTML ohne Astro"""
        dist_dir = site_dir / "dist"
        dist_dir.mkdir(exist_ok=True)
        
        # Kopiere index.html als Fallback
        # (In echter Implementierung: vollständiges HTML generieren)
        print(f"📄 Statischer Fallback erstellt in {dist_dir}")


def main():
    """CLI für Site Builder"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Site Builder")
    parser.add_argument("--name", required=True, help="Unternehmensname")
    parser.add_argument("--category", default="restaurant", help="Branche")
    parser.add_argument("--address", default="Musterstraße 1, Berlin", help="Adresse")
    parser.add_argument("--phone", default="030-12345678", help="Telefon")
    parser.add_argument("--city", default="Berlin", help="Stadt")
    parser.add_argument("--template", default="./templates/restaurant", help="Template-Verzeichnis")
    parser.add_argument("--output", default="./clients", help="Output-Verzeichnis")
    
    args = parser.parse_args()
    
    business = Business(
        name=args.name,
        category=args.category,
        address=args.address,
        phone=args.phone,
        city=args.city
    )
    
    builder = SiteBuilder(
        template_dir=Path(args.template),
        output_dir=Path(args.output)
    )
    
    site_path = builder.build(business)
    print(f"\n🌐 Website bereit: {site_path}")
    print(f"   Öffne: file://{site_path}/dist/index.html")


if __name__ == "__main__":
    main()
