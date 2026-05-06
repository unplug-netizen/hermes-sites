#!/usr/bin/env python3
"""
Hermes Outreach - Automatisierte Kundenansprache
Sendet professionelle E-Mails mit Demo-Link und Angebot
"""

import json
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class OutreachConfig:
    sender_name: str = "Hermes Webdesign"
    sender_email: str = "hello@hermes-agent.dev"
    stripe_basic_link: str = "https://buy.stripe.com/test_basic"
    stripe_business_link: str = "https://buy.stripe.com/test_business"
    stripe_premium_link: str = "https://buy.stripe.com/test_premium"

class OutreachGenerator:
    """Generiert Outreach-E-Mails für qualifizierte Leads"""
    
    def __init__(self, config: OutreachConfig = None):
        self.config = config or OutreachConfig()
    
    def generate_email(self, lead: dict, site_url: str) -> dict:
        """Generiere komplette Outreach-E-Mail"""
        
        name = lead.get("name", "")
        category = lead.get("category", "business")
        city = lead.get("city", "Berlin")
        score = lead.get("score", 0)
        
        # Branchenspezifische Anpassung
        category_benefits = {
            "restaurant": [
                "Online-Tischreservierung direkt auf der Website",
                "Digitale Speisekarte mit aktuellen Preisen",
                "Google Maps-Integration für einfache Navigation"
            ],
            "handwerk": [
                "Online-Terminbuchung für Beratungsgespräche",
                "Vorher-Nachher Galerie Ihrer Projekte",
                "Anfrageformular für Kostenschätzungen"
            ],
            "dienstleistung": [
                "Online-Terminvereinbarung rund um die Uhr",
                "Kundenbewertungen direkt auf Ihrer Seite",
                "Kontaktformular für schnelle Anfragen"
            ]
        }
        
        benefits = category_benefits.get(category, category_benefits["dienstleistung"])
        
        subject = f"Ihre neue Website für {name} – Live in 48 Stunden"
        
        body = f"""Sehr geehrte Damen und Herren,

ich habe für **{name}** in {city} eine professionelle Website erstellt – 
als kostenlose Demo, damit Sie sich von der Qualität überzeugen können.

🔗 **Ihre Live-Demo:** {site_url}

**Was Sie auf der Demo sehen:**
• Responsive Design (Mobile, Tablet, Desktop)
• Schnelle Ladezeiten (optimiert für Google)
• Professionelle Texte und Bilder
• SEO-optimiert für lokale Suche
• {benefits[0]}
• {benefits[1]}

**Warum eine Website wichtig ist:**
85% der Kunden suchen online nach lokalen Unternehmen. 
Ohne Website verpassen Sie potenzielle Kunden jeden Tag.

**Unsere Pakete:**

| Paket | Preis | Enthalten |
|-------|-------|-----------|
| **Basic** | 499 € einmalig | 5-Seiten-Website, 1 Jahr Hosting |
| **Business** | 99 €/Monat | Updates, SEO-Optimierung, Support |
| **Premium** | 199 €/Monat | Custom Domain, Blog, Analytics |

**Sonderangebot:** Wenn Sie innerhalb von 7 Tagen bestellen, 
erhalten Sie 20% Rabatt auf das Basic-Paket (nur 399 €).

**Wie es weitergeht:**
1. Demo ansehen und überzeugen
2. Paket auswählen und bestellen
3. Wir passen Inhalte an (Name, Adresse, Fotos)
4. Website geht live – inkl. Domain und SSL

Bei Fragen antworten Sie einfach auf diese E-Mail 
oder rufen Sie uns an: 030-12345678

Mit freundlichen Grüßen,
{self.config.sender_name}
Team Hermes Webdesign

---
*Diese E-Mail wurde basierend auf öffentlich verfügbaren 
Geschäftsdaten versendet. Wenn Sie keine Angebote wünschen, 
antworten Sie mit "ABMELDEN".*
"""
        
        return {
            "to": lead.get("email", f"info@{name.lower().replace(' ', '-').replace('.', '')}.de"),
            "subject": subject,
            "body": body,
            "html": self._generate_html_version(lead, site_url, benefits),
            "lead_name": name,
            "site_url": site_url,
            "score": score
        }
    
    def _generate_html_version(self, lead: dict, site_url: str, benefits: list) -> str:
        """Generiere HTML-Version der E-Mail"""
        name = lead.get("name", "")
        city = lead.get("city", "Berlin")
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #1a1a2e; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; }}
        .cta {{ background: #e94560; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
        .pricing {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .pricing table {{ width: 100%; border-collapse: collapse; }}
        .pricing th, .pricing td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .pricing th {{ background: #1a1a2e; color: white; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Ihre neue Website für {name}</h1>
            <p>Professionell. Schnell. Bezahlbar.</p>
        </div>
        <div class="content">
            <p>Sehr geehrte Damen und Herren,</p>
            <p>ich habe für <strong>{name}</strong> in {city} eine professionelle Website erstellt – als kostenlose Demo.</p>
            
            <div style="text-align: center;">
                <a href="{site_url}" class="cta">🔍 Demo ansehen</a>
            </div>
            
            <h3>Ihre Vorteile:</h3>
            <ul>
                <li>✅ Responsive Design für alle Geräte</li>
                <li>✅ Schnelle Ladezeiten (Google-optimiert)</li>
                <li>✅ {benefits[0]}</li>
                <li>✅ {benefits[1]}</li>
                <li>✅ {benefits[2]}</li>
            </ul>
            
            <div class="pricing">
                <h3>Unsere Pakete:</h3>
                <table>
                    <tr><th>Paket</th><th>Preis</th><th>Enthalten</th></tr>
                    <tr><td><strong>Basic</strong></td><td>499 €</td><td>5 Seiten, 1 Jahr Hosting</td></tr>
                    <tr><td><strong>Business</strong></td><td>99 €/Mon</td><td>Updates, SEO, Support</td></tr>
                    <tr><td><strong>Premium</strong></td><td>199 €/Mon</td><td>Custom Domain, Blog</td></tr>
                </table>
            </div>
            
            <p><strong>Sonderangebot:</strong> 20% Rabatt bei Bestellung innerhalb von 7 Tagen!</p>
            
            <div style="text-align: center;">
                <a href="{self.config.stripe_basic_link}" class="cta">🛒 Basic-Paket bestellen (399 €)</a>
            </div>
        </div>
        <div class="footer">
            <p>Mit freundlichen Grüßen,<br>{self.config.sender_name}</p>
            <p>---<br>Diese E-Mail basiert auf öffentlich verfügbaren Daten.<br>ABMELDEN? Antworten Sie mit "ABMELDEN".</p>
        </div>
    </div>
</body>
</html>"""
    
    def save_outreach(self, email: dict, output_dir: Path):
        """Speichere Outreach-E-Mail"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        lead_name = email.get("lead_name", "unknown")
        slug = lead_name.lower().replace(" ", "-").replace(".", "")[:30]
        email_file = output_dir / f"{slug}_outreach.json"
        
        with open(email_file, "w", encoding="utf-8") as f:
            json.dump(email, f, indent=2, ensure_ascii=False)
        
        # Also save HTML version
        html_file = output_dir / f"{slug}_outreach.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(email["html"])
        
        print(f"📧 Outreach gespeichert: {email_file}")
        return email_file


def main():
    """CLI für Outreach"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Outreach Generator")
    parser.add_argument("--lead", required=True, help="Lead JSON file or name")
    parser.add_argument("--site-url", required=True, help="URL der generierten Website")
    parser.add_argument("--output", default="./outreach", help="Output-Verzeichnis")
    
    args = parser.parse_args()
    
    # Lade Lead
    lead_file = Path(args.lead)
    if lead_file.exists():
        with open(lead_file, "r", encoding="utf-8") as f:
            lead = json.load(f)
    else:
        # Demo-Lead
        lead = {
            "name": args.lead,
            "category": "restaurant",
            "city": "Berlin",
            "score": 100,
            "email": f"info@{args.lead.lower().replace(' ', '-').replace('.', '')}.de"
        }
    
    # Generiere Outreach
    generator = OutreachGenerator()
    email = generator.generate_email(lead, args.site_url)
    
    # Speichern
    output_path = Path(args.output)
    generator.save_outreach(email, output_path)
    
    print(f"\n📨 E-Mail generiert für: {lead.get('name')}")
    print(f"   Betreff: {email['subject']}")
    print(f"   Demo-Link: {email['site_url']}")


if __name__ == "__main__":
    main()
