# Cursor Handoff — Nefalix

**Tarih:** 2026-07-31 (cloud restore)

## Durum — ÇÖZÜLDÜ
- `nefalix.com` + `/k/enes` + `/k/abdulkadir` + `/k/medident` → **200**
- Smoke: `bash execution/smoke-nefalix-public.sh` → OK
- Vercel proje **Ignored Build Step = `exit 0`** (n8n-repo Git push prod ezmesin)
- Hâlâ önerilen: Dashboard → Git → `n8n-repo` **Disconnect**

## MediDent kartvizit
- URL: `https://nefalix.com/k/medident?utm_source=kartvizit&utm_medium=qr`
- Baskı PNG: `assets/brand/qr-kartvizit-medident.png` (+ `-plain`)

## Ofis dışı kurtarma
```bash
npx vercel login
bash execution/restore-nefalix-prod-from-vercel.sh
```

## Mac (tam landing)
```bash
cd ~/nefalix-landing && npx vercel --prod --yes
cd ~/n8n-repo && git pull
bash execution/deploy-kartvizit-cards.sh
```
