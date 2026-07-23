# Cursor Handoff — Nefalix

**Tarih:** 2026-07-23

## Bu oturum (GEO sistem yükseltme)

Branch: `cursor/geo-sistem-upgrade-c5e3`

- `execution/lib/content_quality.py` — GEO + blog kalite kapıları
- `execution/lib/topic_picker.py` — son N gün / bucket dengesi
- `geo_citation_scores` + `geo_daily_runs.cover_image_url` migration
- `record-geo-citation.py` / `report-geo-citation.py` / reminder DB eksik satır
- `rewrite-geo-seo-blogs.py` — 10 blog playbook standardı
- `smoke-geo-public.py` + `directives/geo.md` / `daily_blog.md` tek otomasyon yolu

## Sonraki (canlı)

1. Prod SQL: iki migration (`cover_image_url`, `geo_citation_scores`)
2. `NEFALIX_INTERNAL_KEY` ile `rewrite-geo-seo-blogs.py` (isteğe bağlı yeniden yazım)
3. VPS: cron **veya** n8n — ikisi birden değil
4. `python3 execution/smoke-geo-public.py`
