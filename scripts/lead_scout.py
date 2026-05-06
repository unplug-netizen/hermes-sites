#!/usr/bin/env python3
"""
Hermes Lead Scout - Lead-Generierung für lokale Unternehmen
Phase 1 MVP: Restaurants ohne Website in einer Stadt
"""

import json
import re
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional

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

class GooglePlacesScraper:
    """Scraper für Google Places API (kostenlos via SerpAPI oder direkt)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
    def search_places(self, query: str, city: str, max_results: int = 20) -> List[Lead]:
        """Suche Unternehmen nach Branche und Stadt"""
        search_query = f"{query} in {city}"
        print(f"🔍 Suche: {search_query}")
        
        # Fallback: HTML-Scraping wenn kein API Key
        if not self.api_key:
            return self._scrape_via_html(search_query, city, max_results)
        
        return self._search_via_api(search_query, city, max_results)
    
    def _scrape_via_html(self, query: str, city: str, max_results: int) -> List[Lead]:
        """Fallback: HTML-Scraping von Google Maps (basic)"""
        # Für MVP: Wir simulieren Daten für den ersten Test
        # In Produktion: Playwright/Scrapy für echtes Scraping
        print("⚠️  Kein API Key - verwende Demo-Daten für ersten Test")
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
                phone=None,  # Benötigt Details API
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
        """Demo-Daten für ersten MVP-Test"""
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
        
        # Keine Website = höchste Priorität (40 Punkte)
        if not lead.has_website and not lead.website:
            score += 40
            
        # Aktive Social Media / viele Bewertungen = engagiert (20 Punkte)
        if lead.review_count and lead.review_count > 50:
            score += 20
        elif lead.review_count and lead.review_count > 20:
            score += 10
            
        # Gute Bewertungen = Qualität (15 Punkte)
        if lead.rating and lead.rating >= 4.5:
            score += 15
        elif lead.rating and lead.rating >= 4.0:
            score += 10
            
        # Telefon vorhanden = erreichbar (10 Punkte)
        if lead.phone:
            score += 10
            
        # Adresse vorhanden (5 Punkte)
        if lead.address:
            score += 5
            
        # Restaurant-Branche = guter Template-Fit (10 Punkte)
        if lead.category in ["restaurant", "food", "meal_takeaway"]:
            score += 10
            
        lead.score = min(score, 100)
        return lead
    
    def filter_qualified(self, leads: List[Lead], min_score: int = 70) -> List[Lead]:
        """Filtere nur qualifizierte Leads"""
        scored = [self.score(lead) for lead in leads]
        qualified = [l for l in scored if l.score >= min_score]
        return sorted(qualified, key=lambda x: x.score, reverse=True)


def save_leads(leads: List[Lead], output_dir: Path):
    """Speichere Leads als JSON"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Alle Leads
    all_path = output_dir / "all_leads.json"
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump([asdict(l) for l in leads], f, indent=2, ensure_ascii=False)
    
    # Nur qualifizierte
    scorer = LeadScorer()
    qualified = scorer.filter_qualified(leads)
    
    qualified_path = output_dir / "qualified_leads.json"
    with open(qualified_path, "w", encoding="utf-8") as f:
        json.dump([asdict(l) for l in qualified], f, indent=2, ensure_ascii=False)
    
    print(f"💾 Gespeichert: {len(leads)} total, {len(qualified)} qualifiziert (Score ≥70)")
    return qualified


def main():
    """Hauptfunktion: Scrape → Score → Speichern"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Lead Scout")
    parser.add_argument("--city", default="Berlin", help="Stadt für Suche")
    parser.add_argument("--category", default="restaurant", help="Branche")
    parser.add_argument("--api-key", help="Google Places API Key (optional)")
    parser.add_argument("--output", default="./leads", help="Output-Verzeichnis")
    parser.add_argument("--min-score", type=int, default=70, help="Mindest-Score")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 HERMES LEAD SCOUT")
    print("=" * 60)
    
    # 1. Scrape
    scraper = GooglePlacesScraper(api_key=args.api_key)
    leads = scraper.search_places(args.category, args.city)
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
    
    # 3. Speichern
    output_path = Path(args.output)
    save_leads(leads, output_path)
    
    # 4. Für Pipeline bereitstellen
    pipeline_dir = Path("./pipeline")
    pipeline_dir.mkdir(exist_ok=True)
    
    # Ersten qualifizierten Lead als nächsten Job markieren
    if qualified:
        next_lead = qualified[0]
        job_file = pipeline_dir / "next_build.json"
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(asdict(next_lead), f, indent=2, ensure_ascii=False)
        print(f"\n🎯 Nächster Build: {next_lead.name}")
        print(f"   Job-Datei: {job_file}")
    
    print("\n✅ Lead-Scouting abgeschlossen")
    return qualified


if __name__ == "__main__":
    main()
