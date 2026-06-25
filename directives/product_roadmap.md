# Ürün Yol Haritası (notlardan türetildi)

> Tek kaynak — eski serbest notlara dönülmez; güncelleme burada yapılır.

## Durum özeti

| Özellik | Durum | Nerede |
|---------|--------|--------|
| WhatsApp AI bot prompt | ✅ | `execution/nefalix_prompts.py` → wf-06 |
| Duygu analizi prompt + yönetici WA | ✅ | wf-04 + `CLINIC_MANAGER_WHATSAPP` |
| NPS anket → Google / yönetici alarm | ✅ | wf-01 (8+ promoter, 7- detractor) |
| Google yorum sync + onay | ✅ | wf-09/10/11, Places API |
| Demo otel/oto kartları (sunum) | ✅ | migration `20260624140000` |
| Cloudbeds / TheClico entegrasyon planı | 📋 | `directives/integrations_hotels.md` |
| HBYS/CRM randevu tetikleme | 📋 SOP | `directives/appointment_trigger.md` |
| CRM’ye özel adapter | ⏳ | Firmaya göre (Medicasimple vb.) |

## NPS iş kuralı (hasta)
1. Randevu biter → WhatsApp’ta **1–10 puan** sorulur
2. **8–10 (promoter):** Google yorum linki gönderilir
3. **7 ve altı (detractor):** Google istenmez; şikayet formu + **yönetici WhatsApp alarmı** (görüşüp gönül al)

## Sentinel iş kuralı
Her mention analizi sonrası yöneticiye WhatsApp özeti: duygu, risk, özet, link. Kritik olanlar ek olarak `alert_urgent` işaretlenir.

## Ortam değişkenleri
```bash
CLINIC_MANAGER_WHATSAPP=905491190819   # + olmadan, Medident pilot
```

## Deploy
```bash
python3 execution/patch-product-prompts.py
python3 execution/import-workflows.py
```
