# nefalix-landing SERP patch kit

Private `~/nefalix-landing` repo’ya merge edilecek dosyalar. Bu klasör tek başına prod deploy **etmez** (blog/geo/api eksik).

## Hızlı sync (Mac/VPS)

```bash
bash execution/sync-serp-to-landing.sh
cd ~/nefalix-landing && npx vercel --prod
```

## Manuel merge

| Bu repodan | Private landing’de |
|------------|-------------------|
| `vercel.json` | Kök — host 301 + geo-sitemap rewrite |
| `api/geo-sitemap.js` | `api/geo-sitemap.js` (future date filtre + HEAD 200) |
| `patches/index-seo-head.html` | `index.html` içinde `nefalix-seo-start` bloğunu değiştir + `<title>` |
| `patches/urunler-seo-head.html` | `urunler.html` SEO + H1 |
| `../nefalix-site-v2/klinik-itibar-yonetimi.html` | `klinik-itibar-yonetimi.html` (yeni sayfa) |
| `public/robots.txt` | `public/robots.txt` (sitemap satırları aynı) |

## vercel.json ek rewrite (yeni sayfa)

```json
{ "source": "/klinik-itibar-yonetimi", "destination": "/klinik-itibar-yonetimi.html" }
```

## Ana sitemap

`https://nefalix.com/sitemap.xml` içine ekle:

```xml
<url>
  <loc>https://nefalix.com/klinik-itibar-yonetimi</loc>
  <lastmod>2026-07-29</lastmod>
  <changefreq>monthly</changefreq>
  <priority>0.95</priority>
</url>
```

## Deploy sonrası smoke

```bash
python3 execution/smoke-serp-public.py
python3 execution/smoke-serp-public.py --check-redirects
```

## GSC (manuel)

- Property: `nefalix.com`
- Sitemap yeniden gönder
- Preferred domain: non-www
