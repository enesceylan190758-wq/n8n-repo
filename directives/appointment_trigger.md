# Randevu Tetikleme — HBYS / CRM Agnostik

## Sorun
Her klinik farklı yazılım kullanıyor (Medicasimple, özel CRM, Excel, vb.). HBYS entegrasyonu tek tip değil; randevu “bitti” olayı her yerde aynı formatta gelmiyor.

## Çözüm: Nefalix webhook (yazılımdan bağımsız)

Tek giriş noktası:

```
POST https://api.nefalixai.com/webhook/nefalix/hbys/appointment-completed
```

**Minimum gövde:**
```json
{
  "clinic_id": "51738ea8-c12e-40ce-a0e2-42869496d76b",
  "patientName": "Ayşe Yılmaz",
  "patientPhone": "+905551234567",
  "clinicName": "Medident İstanbul",
  "doctorName": "Dr. X",
  "treatment": "implant kontrol",
  "googleReviewUrl": "https://maps.google.com/...",
  "complaintFormUrl": "https://www.sikayetvar.com/...",
  "appointmentId": "crm-12345"
}
```

**Akış:** Webhook → AI NPS anketi metni → WhatsApp (Evolution) → hasta 1–10 yanıtlar → promoter ise Google linki / detractor ise yönetici alarmı.

## Entegrasyon seçenekleri (firmaya göre)

| Yöntem | Ne zaman |
|--------|----------|
| **CRM webhook** | Yazılım “randevu tamamlandı” webhook destekliyorsa → doğrudan Nefalix URL |
| **Zapier / Make** | CRM’de trigger yoksa; günlük export veya status değişimi |
| **Manuel panel** | Pilot: resepsiyon günde 1 kez “tamamlanan randevular” listesini CSV veya form |
| **n8n Schedule + Sheets** | Google Sheet’e CRM export; n8n okur ve webhook çağırır |
| **API ara katman** | İleride: Medicasimple / özel HBYS adapter workflow’ları |

## HBYS nedir?
**Hastane Bilgi Yönetim Sistemi** — Türkiye’de kliniklerin hasta/randevu/fatura kayıtlarını tuttuğu yazılım (Medicasimple, Dentsoft, vb. genel adı HBYS/PMS/EMR). Nefalix HBYS’in yerine geçmez; **randevu bitti** sinyalini alır.

## Pilot (Medident)
1. CRM’de randevu ekranı kullanılıyor → CRM’den webhook veya günlük export netleştir
2. Geçici: `curl` veya n8n manuel test ile `appointment-completed` çağrısı
3. `CLINIC_MANAGER_WHATSAPP` .env — düşük NPS’te yönetici alarmı

## Başarı kriteri
- Randevu bitince hasta WhatsApp’ta NPS sorusu alır
- 8–10 → Google yorum daveti
- 7 ve altı → yönetici WhatsApp + şikayet formu; Google istenmez
