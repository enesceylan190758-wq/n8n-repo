# Hasta CRM UI patch (n8n-repo → nefalix-landing)

Cloud/extract kaynaklı P0 değişiklikler (Onat + teklif/kasa). Mac'te:

```bash
cd ~/n8n-repo && git pull
bash execution/apply-crm-offers-payments-vps.sh   # VPS crm_offers/payments 502
bash execution/deploy-hasta-crm-from-extract.sh   # rsync extract → landing + vercel --prod
```

Alternatif manuel:

```bash
cp hasta-crm-app/* ~/nefalix-landing/nefalix-hasta-crm-app/
cd ~/n8n-repo && python3 execution/pack-nefalix-hasta-crm.py
cd ~/nefalix-landing && vercel --prod --yes
```

## Patch özeti

- Teklif: otel/transfer (`YeniTeklif` → `clinic-offers`)
- Kasa: Kur EUR varsayılan, yöntem, işlem tipi, bilgi (`YeniSatis` → `clinic-payments`)
- HastaKarti not+segment; RandevuListe geldi/gelmedi

## Smoke (deploy sonrası)

1. Yeni Teklif — EUR + otel/transfer kaydet
2. Yeni Satış — kur/yöntem/bilgi → Kasa listesi
3. Lead filtresi + Hasta kartı regression
