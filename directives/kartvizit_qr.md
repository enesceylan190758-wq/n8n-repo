# Kartvizit QR — dijital kartlar (`/k/*`)

## Belirti

Basılı kartvizit QR’ı açılmıyor:

- `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` → **404**
- `https://nefalix.com/k/abdulkadir?...` → **404**

QR içeriği (decode): aynı URL’ler; baskıyı yeniden basmaya gerek yok — **sayfayı geri getir**.

## Kök neden

Bkz. **`directives/vercel_prod_safety.md`** — GitHub `n8n-repo` push’u eksik kit’i Vercel Production’a basıyor.

| Kaynak | Rol |
|--------|-----|
| `~/nefalix-landing` | Canlı tam site — sadece Mac CLI `vercel --prod` |
| `n8n-repo/landing-kit/` | Patch kit (kartlar) — **asla doğrudan deploy etme** |

## Acil düzeltme (Mac)

```bash
cd ~/nefalix-landing && npx vercel --prod --yes
cd ~/n8n-repo && git checkout main && git pull
bash execution/deploy-kartvizit-cards.sh
bash execution/smoke-nefalix-public.sh
```

Elle sync:

```bash
cp -R ~/n8n-repo/landing-kit/k ~/nefalix-landing/
cd ~/nefalix-landing && npx vercel --prod --yes
```

## Smoke

```bash
bash execution/smoke-nefalix-public.sh
```

## Deploy kuralı

1. Production **sadece** `~/nefalix-landing` CLI.
2. Preflight: `k/enes.html` + `shared.css` zorunlu.
3. Vercel Dashboard’da `n8n-repo` Git Production bağlantısını kapat.

## QR URL’leri (değiştirme)

| Kişi | URL |
|------|-----|
| Enes Ceylan | `https://nefalix.com/k/enes?utm_source=kartvizit&utm_medium=qr` |
| Abdülkadir Yaşar | `https://nefalix.com/k/abdulkadir?utm_source=kartvizit&utm_medium=qr` |
| MediDent İstanbul | `https://nefalix.com/k/medident?utm_source=kartvizit&utm_medium=qr` |

Eski `qrco.de/...` (üçüncü parti) baskılar **kurtarılamaz** — yeni QR bas / etiket yapıştır.

## Araçlar

| Dosya | Rol |
|-------|-----|
| `landing-kit/k/*.html` | Dijital kart sayfaları |
| `landing-kit/vercel.fragments.json` | Rewrite fragment (kit’te deployable vercel.json yok) |
| `execution/deploy-kartvizit-cards.sh` | Sync + Vercel CLI prod |
| `execution/smoke-nefalix-public.sh` | Canlı smoke |
| `directives/vercel_prod_safety.md` | Site silinmesin SOP |
