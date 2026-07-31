# Cursor Handoff — Nefalix

**Tarih:** 2026-07-31

## Acil — kartvizit QR 404

- QR decode: `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` (+ `/k/abdulkadir`)
- **Tüm nefalix.com** şu an Vercel `NOT_FOUND` (homepage + `/k/*` + `shared.css`)
- Bu PR: dijital kart sayfaları `nefalix-landing/k/*` + Mac deploy script
- **Canlıya almak (Mac):** `bash execution/deploy-kartvizit-cards.sh`
- SOP: `directives/kartvizit_qr.md` · smoke: `python3 execution/smoke-kartvizit.py`
- Cloud’da Vercel token / `~/nefalix-landing` yok → prod deploy Mac’te

## Önceki
- Site stil kırığı SOP: `directives/site_assets.md` (`fix-landing-shared-assets.sh`)
- 10 Geo SEO paket canlıydı; domain şimdi tamamen 404 — tam landing redeploy gerekebilir

## Sonraki
1. Mac: `deploy-kartvizit-cards.sh` (landing doluysa kartlar + prod)
2. Hâlâ tüm site 404 ise: `~/nefalix-landing` tam içerik + `vercel --prod`
3. Smoke: `smoke-kartvizit.py` + `smoke-site-assets.py`
