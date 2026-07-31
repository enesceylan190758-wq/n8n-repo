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

1. Production deploy **sadece** Mac CLI: `cd ~/nefalix-landing && npx vercel --prod` — GitHub `n8n-repo` push asla prod basmamalı.
2. `vercel.json` → `"git": { "deploymentEnabled": false }` (kit + private landing).
3. `vercel --prod` **önce** preflight: `shared.css` + `k/enes.html`.
4. Guardian / smoke: `bash execution/smoke-nefalix-public.sh`.

## Edge case

| Durum | Ne yap |
|-------|--------|
| Mac'te de `shared.css` yok | `git log -- shared.css` → eski commit'ten checkout |
| 200 ama stil bozuk | Yanlış CSS deploy (site-v2 kopyası); Mac landing git history |
| Sadece `/blog/slug` bozuk | Relative `shared.css` — absolute `/shared.css` kullan |
| `/nefalix-chat.css` 404 | Chat stili ikincil; asıl kırık `shared.css` |
| `/k/enes` 404 | `directives/kartvizit_qr.md` — `deploy-kartvizit-cards.sh` |

## Araçlar

| Dosya | Rol |
|-------|-----|
| `execution/fix-landing-shared-assets.sh` | Mac hotfix + deploy + smoke |
| `execution/lib/assert-landing-preflight.sh` | Deploy öncesi kilit |
| `execution/smoke-nefalix-public.sh` | CSS + kartvizit smoke |
| `execution/smoke-site-assets.py` | Canlı CSS/JS 404 kontrolü |
| `execution/update-vercel-vps-urls.sh` | Env + `vercel --prod` (preflight + smoke) |
