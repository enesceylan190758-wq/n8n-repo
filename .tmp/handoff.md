# Cursor Handoff — Nefalix

**Tarih:** 2026-09-28 (otonom ajan)

## Canlı smoke (bu oturum)

| URL | Durum |
|-----|--------|
| `https://nefalix.com/` | 200 — `shared.css` / `shared.js` 200 (stil kırığı yok) |
| `/k/enes` `/k/abdulkadir` | 200 |
| `/k/medident` | **404** — kart `nefalix-landing/k/`’ye eklendi; **Mac `vercel --prod` şart** |
| `/geo` `/blog` `/geo-sitemap.xml` | **502** `fetch failed` — `api.nefalix.com` TLS SAN ≠ hostname |
| `/geo/klinik-itibar-yonetimi-yazilimi` (pillar) | 200 |
| `api.nefalix.com` cert | CN=`srv1975784.hstgr.cloud` |

## Bu PR’de

- MediDent kart + `/k/medident` rewrite (`nefalix-landing`)
- `/geo` `/blog` indeks 502 → HTML fallback (statik sağlık pillar)
- `research/oto-sektoru-arastirma.md` (günlük otomasyon döngüsünü keser)
- SOP: oto dosyası varsa tekrar yazma; sıradaki iş otel GEO

## Mac / VPS (ajan yapamaz)

```bash
# 1) Landing CLI (Git deploy kapalı kalsın)
cd ~/nefalix-landing && npx vercel --prod --yes
# veya n8n-repo sync:
bash execution/deploy-kartvizit-cards.sh
bash execution/smoke-nefalix-public.sh

# 2) VPS TLS: api.nefalix.com + api.nefalixai.com Let’s Encrypt SAN
```

## Sonraki strateji

Otel GEO seti (`geo/*.md` + landing pillars). Oto GEO sonra.

## Eski not (2026-07-31)

- Eski QR `https://qrco.de/bcOVp0` → hesap kapalı
- Yeni: `https://nefalix.com/k/medident?utm_source=kartvizit&utm_medium=qr`
- Baskı PNG: `assets/brand/qr-kartvizit-medident.png`
