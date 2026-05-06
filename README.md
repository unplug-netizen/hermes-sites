# 🤖 Hermes Autonomous Webdesign Business

Vollautomatisierte Pipeline von Lead-Generierung bis Live-Website.

## 🌐 Live Sites

| Site | Branche | Status | Link |
|------|---------|--------|------|
| Trattoria Bella Vista | Restaurant | ✅ Live | [Demo](https://unplug-netizen.github.io/hermes-sites/trattoria-bella-vista/) |
| Curry House | Restaurant | ✅ Live | [Demo](https://unplug-netizen.github.io/hermes-sites/curry-house/) |

## Systemarchitektur

```
Lead Scout → Site Builder → GitHub CI/CD → Deployment
     ↓            ↓              ↓              ↓
  Scoring    Asset-Gen     Repo + Pages   Netlify/Vercel
```

## Komponenten

### 1. Lead Scout (`scripts/lead_scout.py`)
- Scrapt lokale Unternehmen (Google Places API / HTML-Scraper)
- Bewertet Leads nach Qualifizierungskriterien (0-100 Punkte)
- Filtert nur qualifizierte Leads (Score ≥70)

**Usage:**
```bash
python3 scripts/lead_scout.py --city Berlin --category restaurant
```

### 2. Site Builder (`scripts/build_site.py`)
- Generiert Content mit LLM (Kimi 2.6)
- Baut Astro + Tailwind Website
- Erstellt SEO-optimierte Meta-Daten

**Usage:**
```bash
python3 scripts/build_site.py --name "Trattoria Bella Vista" --category restaurant
```

### 3. Outreach (`scripts/outreach.py`)
- Generiert professionelle Outreach-E-Mails
- Inkl. Demo-Link, Preisgestaltung, Stripe-CTA

**Usage:**
```bash
python3 scripts/outreach.py --lead "Trattoria Bella Vista" --site-url "https://..."
```

### 4. Stripe Integration (`scripts/stripe_integration.py`)
- Zahlungsseiten für Website-Pakete
- Basic (499€), Business (99€/Mon), Premium (199€/Mon)

**Usage:**
```bash
python3 scripts/stripe_integration.py --business "Trattoria Bella Vista" --site-url "https://..."
```

### 5. Lighthouse CI (`scripts/lighthouse_monitor.py`)
- Performance-Monitoring
- Ziel: Score > 90

**Usage:**
```bash
python3 scripts/lighthouse_monitor.py --site clients/trattoria-bella-vista/dist
```

### 6. Pipeline (`scripts/pipeline.py`)
- End-to-End Automation
- Verbindet Scout → Builder → Deploy → Outreach

**Usage:**
```bash
python3 scripts/pipeline.py
```

## Templates

| Branche | Status | Pfad |
|---------|--------|------|
| Restaurant | ✅ Ready | `templates/restaurant/` |
| Handwerk | ✅ Ready | `templates/handwerk/` |
| Dienstleistung | 🚧 Phase 2 | `templates/dienstleistung/` |

## GitHub Actions

- **Daily Pipeline** (`.github/workflows/daily-pipeline.yml`): Täglich 06:00 UTC
- **Manual Trigger** (`.github/workflows/generate-site.yml`): Workflow Dispatch

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Frontend | Astro + Tailwind CSS |
| Content | LLM (Kimi 2.6) |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages |
| Bilder | Unsplash API |
| Payments | Stripe (simuliert) |
| Monitoring | Lighthouse CI |

## Performance

| Site | Performance | Accessibility | Best Practices | SEO | Overall |
|------|-------------|---------------|----------------|-----|---------|
| trattoria-bella-vista | 94 | 96 | 100 | 98 | 94 ✅ |
| curry-house | 94 | 96 | 100 | 98 | 94 ✅ |

## Repo
https://github.com/unplug-netizen/hermes-sites

## Dashboard
https://unplug-netizen.github.io/hermes-sites/
