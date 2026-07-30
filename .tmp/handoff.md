# Cursor Handoff — Nefalix

**Tarih:** 2026-07-30

## Acil — site stil kırığı

- **Belirti:** nefalix.com düz HTML (CSS yok)
- **Kök neden:** `https://nefalix.com/shared.css` + `/shared.js` → **404** (HTML hâlâ bunları linkliyor)
- **Kaynak:** private `~/nefalix-landing` (cloud agent’ta yok; Vercel token/SSH yok)
- **Düzeltme (Mac):** `bash execution/fix-landing-shared-assets.sh`
- **SOP:** `directives/site_assets.md`
- **Smoke:** `python3 execution/smoke-site-assets.py`
- `nefalix-site-v2/shared.css` canlıyı kurtarmaz (home-refresh CSS yok)

## Önceki
- 10 Geo SEO kapak + paket canlı (`/geo/2026-07-28` … `/geo/2026-08-06`)
- Branch notu: `cursor/geo-seo-10-packs-c5e3` merge edilmişti

## Sonraki
1. Mac’te `fix-landing-shared-assets.sh` → smoke OK
2. Landing’de `shared.css`/`shared.js` silinmeden deploy kuralı
3. İsteğe bağlı: `nefalix-landing` GitHub remote (yedek)
