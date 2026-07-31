# Site asset'leri (CSS/JS) — stil kırığı

## Belirti

`nefalix.com` düz HTML gibi: Times font, mavi linkler, menü dikey liste. **CSS yüklenmiyor.**

## Kök neden (tekrarlayan)

Canlı HTML `shared.css` / `shared.js` ister; Vercel deploy'unda dosya yok → **404**.

```bash
curl -sI https://nefalix.com/shared.css   # 404 = bu SOP
curl -sL https://nefalix.com/ | grep stylesheet
```

| Yanlış varsayım | Gerçek |
|-----------------|--------|
| `nefalix-site-v2/shared.css` canlı kaynak | Hayır — **eski/eksik kopya**; home-refresh sınıfları yok |
| `styles.css` yeterli | Hayır — eski navy/gold tema; HTML `shared.css` (purple + refresh) bekliyor |
| Bu repodan Vercel deploy | Hayır — private **`~/nefalix-landing`** → `vercel --prod` |

Canlı kaynak: `/Users/enesceylan/nefalix-landing` (`shared.css`, `shared.js`, `index.html`).

## Acil düzeltme (Mac)

```bash
cd ~/n8n-repo && git pull
bash execution/fix-landing-shared-assets.sh
```

Elle:

```bash
cd ~/nefalix-landing
ls -la shared.css shared.js
# eksikse:
git checkout HEAD -- shared.css shared.js
# veya bilinen iyi commit:
# git log --oneline -- shared.css | head
# git checkout <commit> -- shared.css shared.js

npx vercel --prod --yes
python3 ~/n8n-repo/execution/smoke-site-assets.py
```

Telefon/browser: hard refresh.

## Deploy kuralı (tekrar kırılmasın)

1. `vercel --prod` **önce** `ls shared.css shared.js` — ikisi de kökte olmalı.
2. Landing'den dosya silme / “temizlik” deploy'u yasak; CRM-only değişiklik bile tüm projeyi publish eder.
3. `nefalix-site-v2/` → landing'e **kör kopyalama** yapma (refresh CSS ezilir).
4. Guardian / smoke: `python3 execution/smoke-site-assets.py` (blog/GEO smoke'a ekle).

## Edge case

| Durum | Ne yap |
|-------|--------|
| Mac'te de `shared.css` yok | `git log -- shared.css` → eski commit'ten checkout |
| 200 ama stil bozuk | Yanlış CSS deploy (site-v2 kopyası); Mac landing git history |
| Sadece `/blog/slug` bozuk | Relative `shared.css` — absolute `/shared.css` kullan |
| `/nefalix-chat.css` 404 | Chat stili ikincil; asıl kırık `shared.css` |

## Araçlar

| Dosya | Rol |
|-------|-----|
| `execution/fix-landing-shared-assets.sh` | Mac hotfix + deploy + smoke |
| `execution/smoke-site-assets.py` | Canlı 404 kontrolü |
| `execution/update-vercel-vps-urls.sh` | Env + `vercel --prod` (CSS'i taşımaz; deploy öncesi asset kontrol et) |
