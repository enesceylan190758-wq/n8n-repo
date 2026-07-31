# Kartvizit QR — dijital kartlar (`/k/*`)

## Belirti

Basılı kartvizit QR’ı açılmıyor:

- `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` → **404**
- `https://nefalix.com/k/abdulkadir?...` → **404**

QR içeriği (decode): aynı URL’ler; baskıyı yeniden basmaya gerek yok — **sayfayı geri getir**.

## Kök neden

1. Canlı site private **`~/nefalix-landing`** → `vercel --prod`.
2. `/k/enes` + `/k/abdulkadir` o projede yoksa veya son deploy boş/kırık ise Vercel `NOT_FOUND`.
3. Cloud agent’ta landing + Vercel token yok; prod deploy **Mac’te**.

Tüm `nefalix.com` 404 ise (homepage dahil) önce tam landing deploy, sonra kartlar — veya tek seferde `deploy-kartvizit-cards.sh` (landing doluysa).

## Acil düzeltme (Mac)

```bash
cd ~/n8n-repo && git pull
bash execution/deploy-kartvizit-cards.sh
```

Script: `nefalix-landing/k/*` → `~/nefalix-landing/k/` kopyalar, `vercel.json` rewrite merge, `vercel --prod`, smoke.

Elle:

```bash
cp -R ~/n8n-repo/nefalix-landing/k ~/nefalix-landing/
# vercel.json içinde:
# { "source": "/k/enes", "destination": "/k/enes.html" }
# { "source": "/k/abdulkadir", "destination": "/k/abdulkadir.html" }
cd ~/nefalix-landing && npx vercel --prod --yes
python3 ~/n8n-repo/execution/smoke-kartvizit.py
```

## Smoke

```bash
python3 execution/smoke-kartvizit.py
# beklenen: /k/enes, /k/abdulkadir, /k/card.css, /k/enes.vcf → 200
```

## QR URL’leri (değiştirme)

| Kişi | URL |
|------|-----|
| Enes Ceylan | `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` |
| Abdülkadir Yaşar | `https://nefalix.com/k/abdulkadir?utm_source=kartvizit&utm_medium=qr` |

Yeniden PNG üretmek için: `python3 execution/generate-brand-qr.py --preset enes` (logo opsiyonel `--plain`).

## Edge case

| Durum | Ne yap |
|-------|--------|
| Script “landing bulunamadı” | `NEFALIX_LANDING_DIR` ile private repo yolunu ver |
| Kart 200 ama logo kırık | `public/nefalix-logo-512.png` sync; hard refresh |
| Tüm site 404 | Önce `shared.css`/`index.html` dolu landing deploy (`directives/site_assets.md`) |
| E-posta yanlış | HTML + `.vcf` güncelle → yeniden deploy |

## Araçlar

| Dosya | Rol |
|-------|-----|
| `nefalix-landing/k/*.html` | Dijital kart sayfaları |
| `execution/deploy-kartvizit-cards.sh` | Sync + Vercel prod |
| `execution/smoke-kartvizit.py` | Canlı 404 kontrolü |
| `execution/generate-brand-qr.py` | Baskı QR PNG |
