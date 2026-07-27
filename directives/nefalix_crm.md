# Nefalix CRM (ana ürün)

> Ana CRM: **https://nefalix.com/nefalix-crm**  
> App kaynak: `nefalix-landing/nefalix-crm-app/` · pack: seed+store HTML  
> Eski CRM’ler de açık: `/crm` · `/saha` (Saha) · `/klinik-crm` (Klinik)  
> Hasta CRM (klinik DC UI): **https://nefalix.com/hasta-crm** ← `nefalix-landing/nefalix-hasta-crm.html` (Drive: CRM ÇALIŞMASI)

## Canlı

| Ne | URL |
|----|-----|
| Kurum CRM (ana) | https://nefalix.com/nefalix-crm |
| Hasta CRM (klinik UI) | https://nefalix.com/hasta-crm |
| Saha CRM | https://nefalix.com/crm · https://nefalix.com/saha |
| Klinik CRM | https://nefalix.com/klinik-crm |
| Dashboard | https://nefalix.com/nefalix-crm#Dashboard |
| Dinamik | https://nefalix.com/nefalix-crm#DinamikArama |

## Saha CRM operasyon

- State: VPS Supabase `nefalix_state` **id=1** (`clinics` / `notes` / `appts`) — cloud id=2 değil
- Dinamik → Havuz (herkes):  
  `ssh root@93.127.186.45 'cd /opt/nefalix && SUPABASE_URL=http://127.0.0.1:54321 python3 execution/saha-crm-dinamik-to-havuz.py --all'`
- Tek kullanıcı: `--user en|ak|kd` · dry-run: `--dry-run`
- Anadolu Yakası diş import:  
  `scp ...xlsx root@...:/tmp/ && ssh ... 'SUPABASE_URL=http://127.0.0.1:54321 python3 execution/import-saha-crm-excel.py /tmp/Nefalix_ICP_Anadolu_Yakasi_Dis_Klinikleri.xlsx'`
- UI filtre: Klinik Havuzu + Arama Ekranı → **Yaka** (Avrupa / Anadolu)

## Giriş

`enes` / `kader` / `abdulkadir` (veya `admin`) · şifre gerekmez  
Oturum **90 gün** (cookie + localStorage). Son sayfa `nfx_last_route` ile hatırlanır — siteye dönünce kaldığınız ekrandan devam.

## Operasyon (bu turda)

- Excel (89 kurum) seed’e gömüldü + Dinamik nextCall=bugün (temsilcili)
- store: ortak sync API `/api/nefalix-crm` → `nefalix_state` id=2 (Vercel proxy)
- Takvim müsaitlik + randevu mail notify
- WhatsApp: hazır **@ivanamato/whatsapp-inbox** — `evo.nefalix.com/wa-inbox` (SSO iframe)
- Instance `nefalix-crm` · `crm-whatsapp` `inbox-sso`

## Scriptler

```bash
python3 execution/unpack-nefalix-crm.py
# düzenle nefalix-landing/nefalix-crm-app/
python3 execution/pack-nefalix-crm.py
NEFALIX_CRM_FORCE_PROXY=1 python3 execution/import-nefalix-crm-excel.py  # NEFALIX_INTERNAL_KEY lazım
cd nefalix-landing && vercel --prod --yes
```
