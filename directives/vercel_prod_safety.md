# Vercel production güvenliği — site bir daha silinmesin

## Belirti

`nefalix.com` arada bir tamamen gider: homepage, `/k/enes`, `shared.css` → Vercel `NOT_FOUND`.

## Kök neden (tek cümle)

**GitHub `n8n-repo` push’u, eksik patch kit’i Vercel Production’a basıyor** ve dolu siteyi eziyor.

| Kaynak | Ne |
|--------|----|
| Canlı site | Mac `~/nefalix-landing` (tam proje) — **sadece CLI** `vercel --prod` |
| `n8n-repo/nefalix-landing/` | Tam site kaynağı (Arif / git) — **Git deploy yok** |
| `n8n-repo/landing-kit/` | Patch kit (kartvizit vb.) — **deploy etme** |
| Bozan şey | Vercel ↔ GitHub bağlantısı + Root Directory eski `nefalix-landing` |

## Kalıcı ayar (Mac, bir kez)

### 1) Vercel Dashboard (zorunlu)

1. https://vercel.com → proje **nefalix-landing**
2. **Settings → Git**
3. Connected repo `n8n-repo` ise:
   - **Disconnect** et **veya**
   - Ignored Build Step: `exit 0` (tüm Git build’leri atla)
4. Production Branch Git deploy kapalı olsun
5. Deploy yöntemi: **yalnızca lokal CLI**

### 2) Private landing `vercel.json`

```bash
cd ~/nefalix-landing
# git.deploymentEnabled false olduğundan emin ol:
grep deploymentEnabled vercel.json || echo 'EKLE: "git":{"deploymentEnabled":false}'
```

`bash execution/deploy-kartvizit-cards.sh` bunu otomatik yazar.

### 3) n8n-repo tarafı (yapıldı)

- Klasör adı: `landing-kit/` (eski `nefalix-landing/` değil → yanlış Root Directory build **fail** eder, prod’u ezmez)
- Kit içinde deployable `vercel.json` yok → `vercel.fragments.json`
- Preflight: `/k` + `shared.css` yoksa deploy iptal
- Smoke: `bash execution/smoke-nefalix-public.sh`

## Site düştüyse (acil Mac)

```bash
cd ~/nefalix-landing && npx vercel --prod --yes
cd ~/n8n-repo && git checkout main && git pull
bash execution/deploy-kartvizit-cards.sh
bash execution/smoke-nefalix-public.sh
```

Beklenen: home + `/k/enes` + `shared.css` → 200.

## Deploy kuralı

| Yap | Yapma |
|-----|-------|
| `cd ~/nefalix-landing && npx vercel --prod` | `n8n-repo` veya `landing-kit` içinden prod |
| Kart sync: `deploy-kartvizit-cards.sh` | Vercel’i `n8n-repo`’ya Production Git bağla |
| Smoke sonrası kontrol | “Temizlik” diye `k/` veya `shared.css` silip deploy |

## Araçlar

| Dosya | Rol |
|-------|-----|
| `landing-kit/` | Patch kaynağı |
| `execution/deploy-kartvizit-cards.sh` | Sync + CLI prod |
| `execution/lib/assert-landing-preflight.sh` | Deploy kilidi |
| `execution/smoke-nefalix-public.sh` | Canlı smoke |
| `directives/kartvizit_qr.md` | QR /k |
| `directives/site_assets.md` | CSS kırığı |
