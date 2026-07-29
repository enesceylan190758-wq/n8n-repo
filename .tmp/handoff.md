# Cursor Handoff — Nefalix

**Tarih:** 2026-07-29

## Bu oturum (SERP — 3 ajan implementasyon)

Branch: `cursor/nefalix-serp-gorunurluk-5b76`  
PR: https://github.com/enesceylan190758-wq/n8n-repo/pull/12

### Ajan çıktıları (uygulandı)

| Ajan | Yapılan |
|------|---------|
| A Teknik | `nefalix-landing/vercel.json` (301), `api/geo-sitemap.js`, `publish-geo-seo-10.py --start today`, `smoke-serp-public.py` |
| B Intent | `nefalix-site-v2/klinik-itibar-yonetimi.html` (yeni landing) |
| C Meta | Tüm v2 sayfalar title=Nefalix + `sitemap.xml` |

### Patch kit (canlı deploy)

```bash
bash execution/sync-serp-to-landing.sh   # ~/nefalix-landing gerekli
# Manuel: nefalix-landing/patches/*.html → index/urunler SEO blokları
cd ~/nefalix-landing && npx vercel --prod
python3 execution/smoke-serp-public.py --check-redirects
```

### Canlı smoke (deploy öncesi — hâlâ kırmızı)

- title: `NefalixAI — …` (patch deploy edilmedi)
- geo-sitemap: 8 future URL + HEAD 405
- www → 301 yok

### GSC (manuel)

`nefalix.com` sitemap + `/klinik-itibar-yonetimi` URL ekle
