# Hasta CRM UI patch (n8n-repo → nefalix-landing)

Cloud/extract kaynaklı P0 değişiklikler. Mac'te:

```bash
cp hasta-crm-app/* ~/nefalix-landing/nefalix-hasta-crm-app/
cd ~/n8n-repo && python3 execution/pack-nefalix-hasta-crm.py
# veya: bash execution/deploy-hasta-crm-from-extract.sh
cd ~/nefalix-landing && vercel --prod --yes
```

Değişiklikler: teklif otel/transfer, kasa EUR/yöntem/işlem tipi, store addKasa contact_id,
HastaKarti not+segment (dinamik), RandevuListe/kart geldi-gelmedi durum select + renk.

## VPS: offers/payments 502

```bash
bash execution/apply-crm-offers-payments-vps.sh
# sonra Mac: bash execution/deploy-hasta-crm-from-extract.sh
```
