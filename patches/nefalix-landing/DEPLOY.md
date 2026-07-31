# Saha CRM deploy (onaylı)

## Mac'te (önerilen — güvenli)

```bash
cd /Users/enesceylan/nefalix-landing

# 1) Yedek
cp crm.html crm.html.bak-$(date +%Y%m%d-%H%M%S)

# 2) Yeni dosya (PR #11 / patches)
# Bu cloud run'daki dosyayı indir:
curl -fsSL -o crm.html \
  "https://raw.githubusercontent.com/enesceylan190758-wq/n8n-repo/cursor/saha-crm-takvim-klinik-kart-da66/patches/nefalix-landing/crm.html"

# 3) Commit + push (Vercel otomatik) veya:
vercel --prod --yes
```

## Geri alma
```bash
cd /Users/enesceylan/nefalix-landing
cp crm.html.bak-XXXXXXXX ./crm.html
vercel --prod --yes
# veya Vercel Dashboard → Deployments → önceki → Promote
```
