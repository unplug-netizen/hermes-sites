#!/usr/bin/env python3
"""
Hermes Lead Scout - Lead-Generierung für lokale Unternehmen
Integriert mit data/leads.json (Pipeline)
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Set

@dataclass
class Lead:
    name: str
    category: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    place_id: Optional[str]
    source: str
    city: str
    score: int = 0
    has_website: bool = False


def slugify(text: str) -> str:
    """Erstelle einen URL-freundlichen Slug aus Text."""
    text = text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


class GooglePlacesScraper:
    """Scraper für Google Places API (kostenlos via SerpAPI oder direkt)"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    def search_places(self, query: str, city: str, max_results: int = 20) -> List[Lead]:
        """Suche Unternehmen nach Branche und Stadt"""
        search_query = f"{query} in {city}"
        print(f"🔍 Suche: {search_query}")

        if not self.api_key:
            return self._scrape_via_html(search_query, city, max_results)

        return self._search_via_api(search_query, city, max_results)

    def _scrape_via_html(self, query: str, city: str, max_results: int) -> List[Lead]:
        """Fallback: Demo-Daten für MVP-Test"""
        print("⚠️  Kein API Key - verwende Demo-Daten")
        return self._get_demo_data(city)

    def _search_via_api(self, query: str, city: str, max_results: int) -> List[Lead]:
        """Google Places API via textsearch"""
        url = f"{self.base_url}/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key,
            "type": "restaurant"
        }

        req_url = f"{url}?{urllib.parse.urlencode(params)}"

        try:
            with urllib.request.urlopen(req_url, timeout=30) as response:
                data = json.loads(response.read().decode())
                return self._parse_api_results(data, city)
        except Exception as e:
            print(f"❌ API Fehler: {e}")
            return self._get_demo_data(city)

    def _parse_api_results(self, data: dict, city: str) -> List[Lead]:
        """Parse Google Places API Response"""
        leads = []
        for result in data.get("results", []):
            lead = Lead(
                name=result.get("name", ""),
                category=result.get("types", ["restaurant"])[0],
                address=result.get("formatted_address", ""),
                phone=None,
                website=result.get("website"),
                rating=result.get("rating"),
                review_count=result.get("user_ratings_total"),
                place_id=result.get("place_id"),
                source="google_places",
                city=city,
                has_website=bool(result.get("website"))
            )
            leads.append(lead)
        return leads

    def _get_demo_data(self, city: str) -> List[Lead]:
        """Demo-Daten für MVP-Test"""
        demos = [
            Lead(
                name="Trattoria Bella Vista",
                category="restaurant",
                address=f"Hauptstraße 42, {city}",
                phone="030-12345678",
                website=None,
                rating=4.5,
                review_count=127,
                place_id="demo_1",
                source="demo",
                city=city,
                has_website=False
            ),
            Lead(
                name="Pizza Roma",
                category="restaurant",
                address=f"Karl-Marx-Straße 15, {city}",
                phone="030-87654321",
                website=None,
                rating=4.2,
                review_count=89,
                place_id="demo_2",
                source="demo",
                city=city,
                has_website=False
            ),
            Lead(
                name="Sushi Palace",
                category="restaurant",
                address=f"Friedrichstraße 88, {city}",
                phone="030-55599988",
                website="https://sushi-palace.example.com",
                rating=4.7,
                review_count=234,
                place_id="demo_3",
                source="demo",
                city=city,
                has_website=True
            ),
            Lead(
                name="Curry House",
                category="restaurant",
                address=f"Oranienburger Straße 3, {city}",
                phone="030-11122233",
                website=None,
                rating=4.8,
                review_count=56,
                place_id="demo_4",
                source="demo",
                city=city,
                has_website=False
            )
        ]
        return demos


class LeadScorer:
    """Bewertet Leads nach Qualifizierungskriterien"""

    def score(self, lead: Lead) -> Lead:
        """Berechne Lead-Score (0-100)"""
        score = 0

        if not lead.has_website and not lead.website:
            score += 40

        if lead.review_count and lead.review_count > 50:
            score += 20
        elif lead.review_count and lead.review_count > 20:
            score += 10

        if lead.rating and lead.rating >= 4.5:
            score += 15
        elif lead.rating and lead.rating >= 4.0:
            score += 10

        if lead.phone:
            score += 10

        if lead.address:
            score += 5

        if lead.category in ["restaurant", "food", "meal_takeaway"]:
            score += 10

        lead.score = min(score, 100)
        return lead

    def filter_qualified(self, leads: List[Lead], min_score: int = 70) -> List[Lead]:
        """Filtere nur qualifizierte Leads"""
        scored = [self.score(lead) for lead in leads]
        qualified = [l for l in scored if l.score >= min_score]
        return sorted(qualified, key=lambda x: x.score, reverse=True)


def load_existing_leads(leads_path: Path) -> tuple:
    """Lade bestehende Leads aus data/leads.json."""
    if not leads_path.exists():
        return {"version": "1.0", "last_updated": None, "leads": [], "stats": {}}, []

    with open(leads_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data, data.get("leads", [])


def existing_key(name: str, ort: str) -> str:
    """Eindeutiger Schlüssel für Duplikat-Prüfung."""
    return f"{name.strip().lower()}|{ort.strip().lower()}"


def lead_to_pipeline(lead: Lead) -> dict:
    """Konvertiere Lead in das data/leads.json Pipeline-Format."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    city_slug = slugify(lead.city)
    name_slug = slugify(lead.name)
    lead_id = f"{name_slug}-{city_slug}"

    return {
        "id": lead_id,
        "name": lead.name,
        "branche": lead.category,
        "ort": lead.city,
        "score": lead.score,
        "has_website": lead.has_website,
        "website_age": None,
        "mobile_friendly": None,
        "has_ssl": None,
        "social_active": True,
        "status": "approved",
        "created_at": now,
        "built_at": None,
        "deployed_at": None,
        "outreach_sent": False,
        "url": None
    }


def save_pipeline(leads_path: Path, data: dict, existing: List[dict], new_leads: List[Lead]) -> List[dict]:
    """Füge neue Leads zur Pipeline hinzu und speichere data/leads.json."""
    existing_keys = {existing_key(l["name"], l["ort"]) for l in existing}
    added = []

    for lead in new_leads:
        key = existing_key(lead.name, lead.city)
        if key in existing_keys:
            print(f"⏭️  Duplikat übersprungen: {lead.name} in {lead.city}")
            continue

        pipeline_lead = lead_to_pipeline(lead)
        existing.append(pipeline_lead)
        existing_keys.add(key)
        added.append(pipeline_lead)

    total = len(existing)
    built = sum(1 for l in existing if l.get("status") == "live")
    live = sum(1 for l in existing if l.get("status") == "live")
    approved = sum(1 for l in existing if l.get("status") == "approved")
    outreach_pending = sum(1 for l in existing if not l.get("outreach_sent", False))

    data["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    data["leads"] = existing
    data["stats"] = {
        "total_leads": total,
        "approved": approved,
        "built": built,
        "live": live,
        "outreach_pending": outreach_pending
    }

    leads_path.parent.mkdir(parents=True, exist_ok=True)
    with open(leads_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return added


def suggest_city(existing: List[dict]) -> str:
    """Schlage eine Stadt vor, die noch nicht im Bestand ist."""
    used_cities = {l.get("ort", "").lower() for l in existing}
    candidates = ["Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig", "Dresden", "Hannover", "Nürnberg"]
    for city in candidates:
        if city.lower() not in used_cities:
            return city
    return "Frankfurt"


def main():
    """Hauptfunktion: Scrape → Score → Pipeline speichern"""
    import argparse

    parser = argparse.ArgumentParser(description="Hermes Lead Scout")
    parser.add_argument("--city", default=None, help="Stadt für Suche")
    parser.add_argument("--category", default="restaurant", help="Branche")
    parser.add_argument("--api-key", help="Google Places API Key (optional)")
    parser.add_argument("--output", default="./data/leads.json", help="Pfad zur Pipeline-JSON")
    parser.add_argument("--min-score", type=int, default=70, help="Mindest-Score")

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 HERMES LEAD SCOUT")
    print("=" * 60)

    leads_path = Path(args.output)
    data, existing = load_existing_leads(leads_path)
    print(f"📂 Bestehende Leads geladen: {len(existing)}")

    city = args.city or suggest_city(existing)
    print(f"🌍 Ziel-Stadt: {city}")

    # 1. Scrape
    scraper = GooglePlacesScraper(api_key=args.api_key)
    leads = scraper.search_places(args.category, city)
    print(f"📊 {len(leads)} Leads gefunden")

    # 2. Score
    scorer = LeadScorer()
    qualified = scorer.filter_qualified(leads, min_score=args.min_score)

    print(f"\n⭐ QUALIFIZIERTE LEADS (Score ≥{args.min_score}):")
    print("-" * 60)
    for lead in qualified:
        status = "❌ Keine Website" if not lead.has_website else "✅ Hat Website"
        print(f"  {lead.name}")
        print(f"     Score: {lead.score}/100 | Bewertung: {lead.rating}⭐ ({lead.review_count})")
        print(f"     {status} | {lead.address}")
        print()

    # 3. In Pipeline speichern
    added = save_pipeline(leads_path, data, existing, qualified)

    print(f"💾 Pipeline gespeichert: {len(added)} neue Leads hinzugefügt")
    for lead in added:
        print(f"   ✅ {lead['name']} ({lead['ort']}) - Score: {lead['score']}")

    # 4. Neue Leads für externe Prozesse ausgeben
    new_leads_dir = Path("./scout_output")
    new_leads_dir.mkdir(parents=True, exist_ok=True)
    new_leads_path = new_leads_dir / "new_leads.json"
    with open(new_leads_path, "w", encoding="utf-8") as f:
        json.dump(added, f, indent=2, ensure_ascii=False)
    print(f"📄 Neue Leads exportiert: {new_leads_path}")

    print("\n✅ Lead-Scouting abgeschlossen")
    return added


if __name__ == "__main__":
    main()
