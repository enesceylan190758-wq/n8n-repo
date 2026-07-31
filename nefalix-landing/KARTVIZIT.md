# Kartvizit dijital kartlar (`/k/*`)

Basılı QR’lar şu URL’lere gider (utm korunur):

| QR | URL |
|----|-----|
| Enes | `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` |
| Abdülkadir | `https://nefalix.com/k/abdulkadir?utm_source=kartvizit&utm_medium=qr` |

## Dosyalar

| Dosya | Rol |
|-------|-----|
| `k/enes.html` | Enes dijital kart |
| `k/abdulkadir.html` | Abdülkadir dijital kart |
| `k/card.css` | Ortak stil (self-contained) |
| `k/*.vcf` | Rehbere ekle |
| `public/nefalix-logo-512.png` | Logo |
| `vercel.json` | `/k/enes` → `enes.html` rewrite |

Bu klasör **patch kit**; tek başına tüm siteyi replace etme. Private `~/nefalix-landing` içine sync + `vercel --prod`.

## Deploy (Mac)

```bash
cd ~/n8n-repo && git pull
bash execution/deploy-kartvizit-cards.sh
```

## Smoke

```bash
python3 execution/smoke-kartvizit.py
```
