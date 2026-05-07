# HERMES Sites — Autonomes Webdesign Business

Vollautomatisierte Pipeline von Lead-Generierung bis Live-Website. Keine manuelle Intervention nötig.

## Status

| Komponente | Status | URL |
|------------|--------|-----|
| Dashboard | Live | https://unplug-netizen.github.io/hermes-sites/ |
| Trattoria Bella Vista | Live | /trattoria-bella-vista/ |
| Curry House | Live | /curry-house/ |
| Müller Elektro | Live | /mueller-elektro/ |

## Autonome Pipeline

```
Lead Scout (6:00) → Build (4h) → Deploy (6h) → Monitor (stündlich) → Outreach (Mo 9:00)
```

## Workspace UI Cron Jobs

| Job | Schedule | Nächster Lauf |
|-----|----------|---------------|
| `hermes-lead-scout` | `0 6 * * *` | Morgen 06:00 |
| `hermes-build-queue` | `0 */4 * * *` | Heute 08:00 |
| `hermes-deploy` | `0 */6 * * *` | Heute 12:00 |
| `hermes-outreach` | `0 9 * * 1` | Montag 09:00 |
| `hermes-monitor` | `0 * * * *` | Heute 08:00 |

## Tech Stack

| Layer | Technologie |
|-------|-------------|
| Orchestration | Hermes Agent + Cron Jobs |
| CI/CD | GitHub Actions |
| Frontend | Astro + Tailwind CSS |
| Hosting | GitHub Pages |
| Content | Kimi 2.6 (LLM) |
| Monitoring | Lighthouse CI + curl |

## Repository

https://github.com/unplug-netizen/hermes-sites

## Schnellstart

```bash
# Manueller Durchlauf
cd /root/hermes-sites
python scripts/lead_scout.py
python scripts/build_site.py --queue
python scripts/deploy.py --github-pages
python scripts/monitor.py --all
```

## Lizenz

MIT — Autonomes Business unter voller Kontrolle des Agenten.
