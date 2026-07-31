# Kartvizit QR — dijital kartlar (`/k/*`)

## Belirti

Basılı kartvizit QR’ı açılmıyor:

- `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` → **404**
- `https://nefalix.com/k/abdulkadir?...` → **404**

QR içeriği (decode): aynı URL’ler; baskıyı yeniden basmaya gerek yok — **sayfayı geri getir**.

## Kök neden (tekrarlayan — kritik)

1. Canlı site private **`~/nefalix-landing`** → sadece Mac’te `vercel --prod` (CLI).
2. **`n8n-repo` içindeki `nefalix-landing/` bir patch kit’tir** — tam site değil.
3. Vercel projesi GitHub `n8n-repo`’ya bağlıysa `main` push **eksik kit’i production’a basar** → tüm domain `NOT_FOUND` (QR dahil).
4. Koruma: `vercel.json` → `"git": { "deploymentEnabled": false }` + Dashboard’da Production Git bağlantısını kapat / Ignored Build Step.

## Acil düzeltme (Mac)

Site yine 404 ise (GitHub merge sonrası sık olur):

```bash
cd ~/nefalix-landing && npx vercel --prod --yes
# veya tam sync:
cd ~/n8n-repo && git pull
bash execution/deploy-kartvizit-cards.sh
```

Normal kart sync:

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
bash execution/smoke-nefalix-public.sh
# veya: python3 execution/smoke-kartvizit.py
```

## Deploy kuralı (tekrar kırılmasın)

1. `vercel --prod` **öncesi** preflight: `k/enes.html` + `shared.css` zorunlu (`assert-landing-preflight.sh`).
2. Landing’den `k/` silme yasak; CRM-only deploy bile tüm siteyi publish eder.
3. `deploy-kartvizit-cards.sh`, `fix-landing-shared-assets.sh`, `update-vercel-vps-urls.sh` preflight’ı otomatik çalıştırır.
4. Deploy sonrası: `bash execution/smoke-nefalix-public.sh`

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
| `execution/lib/assert-landing-preflight.sh` | Deploy öncesi /k + CSS kilidi |
| `execution/smoke-nefalix-public.sh` | Asset + kartvizit smoke |
| `execution/smoke-kartvizit.py` | Canlı /k 404 kontrolü |
| `execution/generate-brand-qr.py` | Baskı QR PNG |
