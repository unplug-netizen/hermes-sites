# 🤖 Hermes Autonomous Webdesign Business

Vollautomatisierte Pipeline von Lead-Generierung bis Live-Website.

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
python scripts/lead_scout.py --city Berlin --category restaurant
```

### 2. Site Builder (`scripts/build_site.py`)
- Generiert Content mit LLM (Kimi 2.6)
- Baut Astro + Tailwind Website
- Erstellt SEO-optimierte Meta-Daten

**Usage:**
```bash
python scripts/build_site.py --name "Trattoria Bella Vista" --category restaurant
```

### 3. Pipeline (`scripts/pipeline.py`)
- End-to-End Automation
- Verbindet Scout → Builder → Deploy
- Täglicher Cron-Job ready

**Usage:**
```bash
python scripts/pipeline.py
```

## Templates

| Branche | Status | Pfad |
|---------|--------|------|
| Restaurant | ✅ Ready | `templates/restaurant/` |
| Handwerk | 🚧 Phase 2 | `templates/handwerk/` |
| Dienstleistung | 🚧 Phase 2 | `templates/dienstleistung/` |

## GitHub Actions

- **Daily Pipeline** (`.github/workflows/daily-pipeline.yml`): Täglich 06:00 UTC
- **Manual Trigger** (`.github/workflows/generate-site.yml`): Workflow Dispatch

## Erste Website

**Trattoria Bella Vista** - Restaurant in Berlin
- Score: 100/100 (Keine Website, 127 Bewertungen, 4.5★)
- Live-Demo: `clients/trattoria-bella-vista/dist/index.html`

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Frontend | Astro + Tailwind CSS |
| Content | LLM (Kimi 2.6) |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages / Netlify |
| Bilder | Unsplash API |

## Roadmap

- [x] Phase 1: MVP (Lead-Scout + Restaurant-Template)
- [ ] Phase 2: Multi-Branchen + GitHub Actions
- [ ] Phase 3: Auto-Deployment + Outreach
- [ ] Phase 4: Stripe + Kunden-Dashboard

## Repo
https://github.com/unplug-netizen/hermes-sites
