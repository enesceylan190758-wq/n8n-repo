# Hasta CRM P0 Backlog (daily cutover)

**Implementer:** `2d764466-f680-4413-9d44-bd2cb04b2ccb`  
**Coding slice:** **DONE** (p0-01…p0-06 director verified)  
**Live:** **LIVE** (2026-07-28) — VPS apply + pack + `vercel --prod`; smoke `/hasta-crm` HTTP 200

| # | ID | Durum |
|---|-----|-------|
| 1–6 | lead → pack/notes | **done** + live |

**Mac DONE:**
1. `bash execution/apply-crm-offers-payments-vps.sh` — OK
2. `python3 execution/pack-nefalix-hasta-crm.py` + `vercel --prod --yes` — OK
3. Smoke: `https://nefalix.com/hasta-crm` HTTP 200 (UI checklist manuel)
