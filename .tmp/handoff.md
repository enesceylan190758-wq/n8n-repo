# Cursor Handoff — Nefalix

**Tarih:** 2026-07-31

## ACİL — site yine 404

`main`’e merge Vercel’in **eksik** `n8n-repo/nefalix-landing` kit’ini production’a basmış olabilir.

**Mac şimdi:**
```bash
cd ~/nefalix-landing && npx vercel --prod --yes
# sonra:
cd ~/n8n-repo && git pull
bash execution/deploy-kartvizit-cards.sh
```

Kalıcı: `vercel.json` → `git.deploymentEnabled: false` + Vercel Dashboard’da n8n-repo Production Git deploy kapat.

## Sonraki
1. Mac CLI redeploy
2. Smoke: `bash execution/smoke-nefalix-public.sh`
3. Guard branch’i main’e al
