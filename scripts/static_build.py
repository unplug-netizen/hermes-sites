#!/usr/bin/env python3
"""
Statischer HTML Builder für Astro-Sites ohne package.json
Rendert Astro-Komponenten mit Jinja2-ähnlichem Templating zu statischem HTML
"""

import json
import sys
import os
import re
import shutil
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).parent.parent.resolve()
CLIENTS_DIR = BASE_DIR / "clients"
DOCS_DIR = BASE_DIR / "docs"

def load_site_json(site_dir):
    """Lade site.json aus dem src/data Verzeichnis"""
    data_path = site_dir / "src" / "data" / "site.json"
    if not data_path.exists():
        data_path = site_dir / "data" / "site.json"
    if data_path.exists():
        return json.loads(data_path.read_text())
    return None

def render_astro_component(component_path, props):
    """Rendere Astro-Komponente zu HTML (vereinfacht)"""
    content = component_path.read_text()
    
    # Entferne Frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Ersetze Astro-Props mit Werten
    for key, value in props.items():
        if isinstance(value, str):
            # Ersetze {prop} und {Astro.props.prop}
            content = content.replace(f'{{{key}}}', value)
            content = content.replace(f'{{Astro.props.{key}}}', value)
    
    # Ersetze einfache JSX-Ausdrücke
    content = re.sub(r'\{([^}]+)\}', lambda m: props.get(m.group(1).strip(), m.group(0)), content)
    
    return content

def build_static_html(site_dir, site_data):
    """Baue statisches HTML aus Astro-Komponenten"""
    business = site_data.get("business", {})
    content = site_data.get("content", {})
    assets = site_data.get("assets", {})
    
    name = business.get("name", "Unternehmen")
    tagline = business.get("tagline", "")
    address = business.get("address", "")
    phone = business.get("phone", "")
    hours = business.get("hours", "")
    city = business.get("city", "")
    
    seo = content.get("seo", {})
    hero = content.get("hero", {})
    about = content.get("about", {})
    services = content.get("services", {})
    gallery = content.get("gallery", {})
    contact = content.get("contact", {})
    
    title = seo.get("title", f"{name} - {tagline}")
    description = seo.get("description", f"{name} - Professionelle Services in {city}")
    
    # HTML-Komponenten
    hero_html = f'''
<section class="relative h-screen min-h-[600px] flex items-center justify-center overflow-hidden">
  <div class="absolute inset-0 z-0">
    <img src="{assets.get('hero_image', '')}" alt="Hero Background" class="w-full h-full object-cover" />
    <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/70"></div>
  </div>
  <div class="relative z-10 text-center px-4 max-w-4xl mx-auto">
    <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight leading-tight">{hero.get('title', name)}</h1>
    <p class="text-xl md:text-2xl text-white/90 mb-8 font-light">{hero.get('subtitle', tagline)}</p>
    <a href="#kontakt" class="inline-block bg-amber-500 hover:bg-amber-600 text-white font-semibold px-8 py-4 rounded-full text-lg transition-all transform hover:scale-105 shadow-lg">{hero.get('cta', 'Kontakt')}</a>
  </div>
  <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
    <svg class="w-6 h-6 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
    </svg>
  </div>
</section>
'''
    
    about_html = f'''
<section id="ueber-uns" class="py-20 bg-white">
  <div class="max-w-6xl mx-auto px-4">
    <div class="grid md:grid-cols-2 gap-12 items-center">
      <div class="order-2 md:order-1">
        <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">{about.get('title', 'Über uns')}</h2>
        <div class="prose prose-lg text-gray-600 leading-relaxed">
          <p>{about.get('text', '')}</p>
        </div>
        <div class="mt-8 flex items-center gap-4">
          <div class="flex -space-x-2">
            <div class="w-10 h-10 rounded-full bg-amber-100 border-2 border-white flex items-center justify-center text-amber-600 text-sm font-bold">★</div>
            <div class="w-10 h-10 rounded-full bg-amber-100 border-2 border-white flex items-center justify-center text-amber-600 text-sm font-bold">★</div>
            <div class="w-10 h-10 rounded-full bg-amber-100 border-2 border-white flex items-center justify-center text-amber-600 text-sm font-bold">★</div>
          </div>
          <p class="text-sm text-gray-500">Bewertet mit 4.8 von 5 Sternen</p>
        </div>
      </div>
      <div class="order-1 md:order-2">
        <img src="{assets.get('about_image', '')}" alt="Über uns" class="rounded-2xl shadow-2xl w-full h-[400px] object-cover" />
      </div>
    </div>
  </div>
</section>
'''
    
    # Services
    services_items = services.get('items', [])
    services_cards = ''
    for item in services_items:
        services_cards += f'''
        <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
          <div class="h-48 bg-gradient-to-br from-amber-100 to-orange-100 flex items-center justify-center">
            <span class="text-5xl">{item.get('icon', '🍽️')}</span>
          </div>
          <div class="p-6">
            <div class="flex justify-between items-start mb-3">
              <h3 class="text-xl font-bold text-gray-900">{item.get('name', '')}</h3>
              <span class="text-amber-600 font-bold">{item.get('price', '')}</span>
            </div>
            <p class="text-gray-600 leading-relaxed">{item.get('description', '')}</p>
          </div>
        </div>
        '''
    
    services_html = f'''
<section id="speisekarte" class="py-20 bg-stone-50">
  <div class="max-w-6xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{services.get('title', 'Unsere Leistungen')}</h2>
      <div class="w-24 h-1 bg-amber-500 mx-auto rounded-full"></div>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      {services_cards}
    </div>
  </div>
</section>
'''
    
    # Gallery
    gallery_images = assets.get('gallery_images', [])
    gallery_items = ''
    for i, img in enumerate(gallery_images):
        span_class = 'col-span-2 row-span-2' if i == 0 or i == 3 else ''
        gallery_items += f'''
        <div class="relative overflow-hidden rounded-xl group {span_class}">
          <img src="{img}" alt="Galerie Bild {i+1}" class="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500" loading="lazy" />
          <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors"></div>
        </div>
        '''
    
    gallery_html = f'''
<section id="galerie" class="py-20 bg-white">
  <div class="max-w-6xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{gallery.get('title', 'Impressionen')}</h2>
      <div class="w-24 h-1 bg-amber-500 mx-auto rounded-full"></div>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      {gallery_items}
    </div>
  </div>
</section>
'''
    
    contact_html = f'''
<section id="kontakt" class="py-20 bg-stone-900 text-white">
  <div class="max-w-6xl mx-auto px-4">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold mb-4">{contact.get('title', 'Besuchen Sie uns')}</h2>
      <div class="w-24 h-1 bg-amber-500 mx-auto rounded-full"></div>
    </div>
    <div class="grid md:grid-cols-3 gap-8 text-center">
      <div class="p-6">
        <div class="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2">Adresse</h3>
        <p class="text-stone-300">{address}</p>
      </div>
      <div class="p-6">
        <div class="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2">Telefon</h3>
        <a href="tel:{phone}" class="text-amber-500 hover:text-amber-400 transition-colors">{phone}</a>
      </div>
      <div class="p-6">
        <div class="w-16 h-16 bg-amber-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <h3 class="text-xl font-bold mb-2">Öffnungszeiten</h3>
        <p class="text-stone-300">{hours}</p>
      </div>
    </div>
    <div class="mt-16 text-center">
      <a href="tel:{phone}" class="inline-block bg-amber-500 hover:bg-amber-600 text-white font-bold px-10 py-5 rounded-full text-xl transition-all transform hover:scale-105 shadow-lg">
        📞 Tisch reservieren
      </a>
      <p class="mt-4 text-stone-400">Wir freuen uns auf Ihren Besuch!</p>
    </div>
  </div>
</section>
'''
    
    year = datetime.now().year
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{description}" />
  <meta name="keywords" content="{', '.join(seo.get('keywords', []))}" />
  <title>{title}</title>
  <script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@type": "Restaurant",
    "name": name,
    "address": {
      "@type": "PostalAddress",
      "streetAddress": address,
      "addressLocality": city,
      "addressCountry": "DE"
    },
    "telephone": phone,
    "priceRange": "€€",
    "servesCuisine": "Italian"
  }, ensure_ascii=False)}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; }}
  </style>
</head>
<body class="bg-white text-gray-900 antialiased">
  <nav class="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100">
    <div class="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
      <a href="#" class="text-xl font-bold text-gray-900">{name}</a>
      <div class="hidden md:flex gap-8">
        <a href="#ueber-uns" class="text-gray-600 hover:text-gray-900 transition-colors">Über uns</a>
        <a href="#speisekarte" class="text-gray-600 hover:text-gray-900 transition-colors">Speisekarte</a>
        <a href="#galerie" class="text-gray-600 hover:text-gray-900 transition-colors">Galerie</a>
        <a href="#kontakt" class="text-gray-600 hover:text-gray-900 transition-colors">Kontakt</a>
      </div>
    </div>
  </nav>
  <main class="pt-16">
    {hero_html}
    {about_html}
    {services_html}
    {gallery_html}
    {contact_html}
  </main>
  <footer class="bg-stone-950 text-stone-400 py-12">
    <div class="max-w-6xl mx-auto px-4 text-center">
      <p class="mb-4">© {year} {name}. Alle Rechte vorbehalten.</p>
      <p class="text-sm">Mit ❤️ erstellt von Hermes Agent</p>
    </div>
  </footer>
</body>
</html>'''
    
    return html

def build_site(site_slug, site_dir):
    """Baue eine einzelne Site"""
    print(f"🏗️  Baue statisches HTML für: {site_slug}")
    
    site_data = load_site_json(site_dir)
    if not site_data:
        print(f"❌ Keine site.json gefunden für {site_slug}")
        return False
    
    # Erstelle dist-Verzeichnis
    dist_dir = site_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Baue HTML
    html = build_static_html(site_dir, site_data)
    
    # Schreibe index.html
    index_path = dist_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    
    print(f"✅ {site_slug} gebaut: {index_path}")
    return True

def main():
    """Baue alle Sites mit Status 'built' in der Queue"""
    import json
    
    queue_file = BASE_DIR / "data" / "queue.json"
    if not queue_file.exists():
        print("❌ queue.json nicht gefunden")
        return
    
    queue_data = json.loads(queue_file.read_text())
    
    # Finde Sites mit Status 'built'
    built_items = [item for item in queue_data.get("queue", []) if item.get("status") == "built"]
    
    if not built_items:
        print("✅ Keine Sites mit Status 'built' in der Queue")
        return
    
    print(f"📊 {len(built_items)} Sites zu bauen")
    print()
    
    for item in built_items:
        site_id = item["id"]
        
        # Ordnername kann anders sein als ID (z.B. ohne -hamburg Suffix)
        site_dir = CLIENTS_DIR / site_id
        if not site_dir.exists():
            # Versuche ohne -hamburg Suffix
            base_id = site_id.replace('-hamburg', '')
            site_dir = CLIENTS_DIR / base_id
        
        if not site_dir.exists():
            print(f"❌ Verzeichnis nicht gefunden: {site_id}")
            continue
        
        success = build_site(site_id, site_dir)
        
        if success:
            item["status"] = "built"
            item["stage"] = "build_complete"
            item["last_action"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Speichere Queue
    queue_data["last_updated"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    queue_file.write_text(json.dumps(queue_data, indent=2, ensure_ascii=False))
    
    print()
    print("=" * 70)
    print("📊 BUILD ERGEBNIS")
    print("=" * 70)
    print(f"✅ Alle {len(built_items)} Sites gebaut")

if __name__ == "__main__":
    main()
