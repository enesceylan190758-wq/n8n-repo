# Cursor Handoff — Nefalix

**Tarih:** 2026-07-31

## MediDent kartvizit
- Eski QR `https://qrco.de/bcOVp0` → hesap kapalı (kurtarılamaz)
- Yeni: `https://nefalix.com/k/medident?utm_source=kartvizit&utm_medium=qr`
- Baskı PNG: `assets/brand/qr-kartvizit-medident.png` (+ `-plain`)

## ACİL — nefalix.com hâlâ 404 olabilir
```bash
cd ~/nefalix-landing && npx vercel --prod --yes
cd ~/n8n-repo && git checkout main && git pull
bash execution/deploy-kartvizit-cards.sh
```

Vercel Git: n8n-repo Production disconnect (`directives/vercel_prod_safety.md`)
