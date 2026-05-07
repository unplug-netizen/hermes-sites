# HERMES Sites — Status Report

**Generiert:** 2026-05-07 18:30 UTC
**System:** Autonomes Webdesign Business
**Status:** ✅ OPERATIONAL

---

## Live Sites (3)

| # | Site | Branche | Ort | Score | Lighthouse | URL |
|---|------|---------|-----|-------|------------|-----|
| 1 | Trattoria Bella Vista | Restaurant | Berlin | 100 | 97 | https://unplug-netizen.github.io/hermes-sites/trattoria-bella-vista/ |
| 2 | Curry House | Restaurant | Berlin | 95 | 97 | https://unplug-netizen.github.io/hermes-sites/curry-house/ |
| 3 | Müller Elektro GmbH | Handwerk | München | 90 | 95 | https://unplug-netizen.github.io/hermes-sites/mueller-elektro/ |

---

## Cron Jobs (5)

Alle Jobs sind im Hermes Workspace UI sichtbar (deliver=origin).

| Job ID | Name | Schedule | Nächster Lauf | Status |
|--------|------|----------|---------------|--------|
| ba78f09de31b | hermes-lead-scout | 0 6 * * * | 2026-05-08 06:00 | ✅ Scheduled |
| bdedad48fbca | hermes-build-queue | 0 */4 * * * | 2026-05-07 20:00 | ✅ Scheduled |
| bda08ca30a3f | hermes-deploy | 0 */6 * * * | 2026-05-07 18:00 | ✅ Scheduled |
| e6519d6272ac | hermes-outreach | 0 9 * * 1 | 2026-05-11 09:00 | ✅ Scheduled |
| 96094a7992af | hermes-monitor | 0 * * * * | 2026-05-07 19:00 | ✅ Scheduled |

---

## GitHub Actions Workflows (5)

| Workflow | Trigger | Status |
|----------|---------|--------|
| lead-scout.yml | Cron + Manual | ✅ |
| build-site.yml | Queue + Manual | ✅ |
| deploy.yml | Push clients/ + Manual | ✅ |
| monitor.yml | Cron + Manual | ✅ |
| pipeline.yml | Cron alle 6h | ✅ |

---

## State Database

| Datei | Einträge | Letztes Update |
|-------|----------|----------------|
| data/leads.json | 3 Leads | 2026-05-07 06:00 |
| data/queue.json | 3 Einträge | 2026-05-07 06:00 |
| data/metrics.json | 3 Sites | 2026-05-07 06:00 |

---

## Pipeline Durchsatz

| Metrik | Wert |
|--------|------|
| Leads/Tag | 3 (Demo) |
| Builds/Tag | 3 (Demo) |
| Deploys/Tag | 3 (Demo) |
| Avg Buildzeit | ~5 Minuten |
| Avg Deployzeit | ~2 Minuten |

---

## Nächste Aktionen (Autonom)

1. **2026-05-07 19:00** — hermes-monitor: Lighthouse Check
2. **2026-05-07 20:00** — hermes-build-queue: Queue prüfen
3. **2026-05-08 06:00** — hermes-lead-scout: Neue Leads
4. **2026-05-11 09:00** — hermes-outreach: E-Mails generieren

---

## Repository

https://github.com/unplug-netizen/hermes-sites

## Dashboard

https://unplug-netizen.github.io/hermes-sites/

---

*HERMES Autonomous Webdesign Business — Powered by Hermes Agent + Kimi 2.6*
