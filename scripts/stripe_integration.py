#!/usr/bin/env python3
"""
Hermes Stripe Integration - Zahlungsabwicklung
Erstellt Stripe Checkout Sessions für Website-Pakete
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass

@dataclass
class PricingPackage:
    name: str
    price_eur: int
    description: str
    features: list
    stripe_price_id: str = ""

class StripeIntegration:
    """Stripe Payment Integration für Hermes Sites"""
    
    PACKAGES = {
        "basic": PricingPackage(
            name="Basic",
            price_eur=499,
            description="5-Seiten-Website inkl. 1 Jahr Hosting",
            features=[
                "5 professionelle Seiten",
                "Mobile-optimiertes Design",
                "SEO-Grundoptimierung",
                "Kontaktformular",
                "1 Jahr Hosting inklusive",
                "SSL-Zertifikat"
            ],
            stripe_price_id="price_basic_499"
        ),
        "business": PricingPackage(
            name="Business",
            price_eur=99,
            description="Monatliches Abo mit Updates & Support",
            features=[
                "Alles aus Basic",
                "Monatliche Content-Updates",
                "SEO-Optimierung",
                "Performance-Monitoring",
                "E-Mail-Support",
                "Backup & Wartung"
            ],
            stripe_price_id="price_business_99"
        ),
        "premium": PricingPackage(
            name="Premium",
            price_eur=199,
            description="Custom Domain, Blog, Analytics",
            features=[
                "Alles aus Business",
                "Eigene Domain (.de / .com)",
                "Blog-Funktion",
                "Google Analytics",
                "Erweitertes SEO",
                "Prioritätssupport"
            ],
            stripe_price_id="price_premium_199"
        )
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "sk_test_placeholder"
    
    def generate_checkout_link(self, package: str, business_name: str) -> str:
        """Generiere Stripe Checkout Link"""
        pkg = self.PACKAGES.get(package, self.PACKAGES["basic"])
        
        # In Produktion: Stripe API Call
        # Für Demo: Simulierter Link
        slug = business_name.lower().replace(" ", "-").replace(".", "")[:30]
        
        return {
            "url": f"https://checkout.stripe.com/pay/{pkg.stripe_price_id}_{slug}",
            "package": pkg.name,
            "price": pkg.price_eur,
            "business": business_name,
            "test_mode": True
        }
    
    def generate_payment_page(self, business_name: str, site_url: str) -> str:
        """Generiere HTML-Zahlungsseite"""
        slug = business_name.lower().replace(" ", "-").replace(".", "")[:30]
        
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website bestellen - {business_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="max-w-4xl mx-auto p-8">
        <header class="text-center py-8">
            <h1 class="text-3xl font-bold mb-2">🚀 Ihre Website für {business_name}</h1>
            <p class="text-gray-600">Wählen Sie Ihr Paket und gehen Sie live</p>
        </header>
        
        <div class="grid md:grid-cols-3 gap-6 mb-12">
"""
        
        for key, pkg in self.PACKAGES.items():
            features_html = "\n".join([f'<li class="flex items-center gap-2"><span class="text-green-500">✓</span>{f}</li>' for f in pkg.features[:4]])
            
            html += f"""
            <div class="bg-white rounded-xl shadow-lg p-6 {'border-2 border-blue-500' if key == 'business' else ''}">
                <h2 class="text-xl font-bold mb-2">{pkg.name}</h2>
                <div class="text-3xl font-bold text-blue-600 mb-4">
                    {pkg.price_eur}€
                    {'<span class="text-sm text-gray-500">/Monat</span>' if key != 'basic' else '<span class="text-sm text-gray-500">einmalig</span>'}
                </div>
                <p class="text-gray-600 mb-4">{pkg.description}</p>
                <ul class="space-y-2 text-sm mb-6">
                    {features_html}
                </ul>
                <button class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors">
                    {pkg.name} auswählen
                </button>
            </div>
"""
        
        html += f"""
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-8 text-center">
            <h2 class="text-2xl font-bold mb-4">Ihre Demo-Website</h2>
            <p class="text-gray-600 mb-4">Sehen Sie sich die kostenlose Demo an, bevor Sie bestellen:</p>
            <a href="{site_url}" target="_blank" class="inline-block bg-gray-800 hover:bg-gray-900 text-white px-8 py-3 rounded-lg transition-colors">
                🔍 Demo ansehen
            </a>
        </div>
        
        <footer class="text-center py-8 text-gray-500 text-sm">
            <p>Powered by Hermes Agent • Sichere Zahlung via Stripe</p>
        </footer>
    </div>
</body>
</html>
"""
        return html
    
    def save_payment_page(self, business_name: str, site_url: str, output_dir: Path):
        """Speichere Zahlungsseite"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        slug = business_name.lower().replace(" ", "-").replace(".", "")[:30]
        html = self.generate_payment_page(business_name, site_url)
        
        html_file = output_dir / f"{slug}_payment.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        # Save package info as JSON
        packages_json = {
            "business": business_name,
            "site_url": site_url,
            "packages": {
                k: {
                    "name": v.name,
                    "price": v.price_eur,
                    "description": v.description,
                    "features": v.features
                }
                for k, v in self.PACKAGES.items()
            }
        }
        
        json_file = output_dir / f"{slug}_packages.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(packages_json, f, indent=2, ensure_ascii=False)
        
        print(f"💳 Zahlungsseite: {html_file}")
        return html_file


def main():
    """CLI für Stripe Integration"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Hermes Stripe Integration")
    parser.add_argument("--business", required=True, help="Unternehmensname")
    parser.add_argument("--site-url", required=True, help="Website URL")
    parser.add_argument("--package", default="basic", choices=["basic", "business", "premium"])
    parser.add_argument("--output", default="./payments", help="Output-Verzeichnis")
    
    args = parser.parse_args()
    
    stripe = StripeIntegration()
    
    # Generiere Checkout-Link
    checkout = stripe.generate_checkout_link(args.package, args.business)
    print(f"🔗 Checkout-Link: {checkout['url']}")
    
    # Generiere Zahlungsseite
    payment_page = stripe.save_payment_page(args.business, args.site_url, Path(args.output))
    
    print(f"\n✅ Stripe-Integration fertig für: {args.business}")
    print(f"   Paket: {checkout['package']} ({checkout['price']}€)")


if __name__ == "__main__":
    main()
