# ⛔ BU KLASÖR CANLI SITE DEĞİL

`landing-kit/` = patch / sync kaynağı (kartvizit, SEO fragment).

**Kaynak (git):** `n8n-repo/nefalix-landing/` — Arif / ekip buradan.

**Canlı deploy:** Mac’te `~/nefalix-landing` → sadece CLI:

```bash
cd ~/nefalix-landing && npx vercel --prod --yes
```

## Neden site bozuluyordu?

Vercel projesi GitHub `n8n-repo` + Root Directory `nefalix-landing` (eski ad) ile bağlıydı.  
`main`’e her merge → **eksik kit production’a basılıyordu** → `nefalix.com` tamamen `NOT_FOUND`.

## Yasak

- Bu klasörü Vercel’e Git ile bağlama
- Bu klasörden `vercel --prod` çalıştırma
- Root Directory = `landing-kit` veya `nefalix-landing` yapma

## Doğru akış

```bash
bash execution/deploy-kartvizit-cards.sh   # kit → ~/nefalix-landing + CLI prod
bash execution/smoke-nefalix-public.sh
```

SOP: `directives/vercel_prod_safety.md`
