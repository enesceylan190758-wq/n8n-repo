# Cursor Handoff — Nefalix

**Tarih:** 2026-07-31

## ACİL — site 404

Kök neden: Vercel ← GitHub `n8n-repo` auto-deploy eksik kit’i basıyor.

**Mac şimdi:**
```bash
cd ~/nefalix-landing && npx vercel --prod --yes
cd ~/n8n-repo && git checkout main && git pull
bash execution/deploy-kartvizit-cards.sh
```

**Kalıcı (bir kez):** Vercel Dashboard → nefalix-landing → Settings → Git → Disconnect / Ignored Build Step `exit 0`

## Repo koruması
- `nefalix-landing/` → `landing-kit/` (yanlış Root Directory artık fail eder)
- Kit’te deployable `vercel.json` yok
- SOP: `directives/vercel_prod_safety.md`
