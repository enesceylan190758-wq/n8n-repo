# Hasta CRM UI patch (n8n-repo → nefalix-landing)

## Mac tek komut (extract gerekmez)

```bash
cd ~/n8n-repo && git pull
bash execution/apply-crm-offers-payments-vps.sh   # clinic-offers 502 → 200
bash execution/deploy-hasta-crm-from-extract.sh   # overlay + pack + vercel
```

Extract yoksa script `~/nefalix-landing` + `hasta-crm-app/` ile devam eder.
Sadece pack (vercel yok): `SKIP_VERCEL=1 bash execution/deploy-hasta-crm-from-extract.sh`

## Patch özeti

- Teklif: otel/transfer (`YeniTeklif` → `clinic-offers`)
- Kasa: Kur EUR, yöntem, işlem tipi (`YeniSatis` → `clinic-payments`)
- HastaKarti not+segment; RandevuListe geldi/gelmedi

## Smoke

1. Yeni Teklif — EUR + otel/transfer
2. Yeni Satış — kur/yöntem → Kasa
3. Login sonrası `clinic-offers` / `clinic-payments` → **200** (401=oturum, 502=VPS SQL)
