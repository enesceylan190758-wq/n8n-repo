# Nefalix Otomasyon Mimarisi (PDF v4 → n8n)

PDF'deki Swell CX mantığının n8n karşılığı. **MVP Aşama 1–2** workflow'ları kuruldu.

## Modül Haritası

| PDF Modülü | n8n Workflow | Durum |
|------------|--------------|-------|
| **1. Feedback & Reviews Loop** | `nefalix-01-feedback-reviews-loop` | ✅ Kuruldu |
| **2. Inbox (Team Inbox)** | `nefalix-06-inbox-routing` + Web Chatbot | ✅ Kısmi |
| **3. AI Agent (Google yorum)** | `nefalix-02-google-review-ai-agent` | ✅ Kuruldu |
| **4. Inside (eNPS)** | `nefalix-03-inside-enps` | ✅ Kuruldu |
| **Add-on Sentinel** | `nefalix-04-sentinel-reputation` | ✅ Kuruldu |
| **Add-on Recall** | `nefalix-05-recall-patient` | ✅ Kuruldu |
| Web Chatbot | `nefalix-web-chatbot` | ✅ Çalışıyor |

## Kurulum

```bash
cd /Users/enesceylan/n8n-repo
python3 scripts/import-workflows.py
```

n8n: http://localhost:5678

## Webhook URL'leri (local)

| Akış | Method | Path |
|------|--------|------|
| HBYS randevu bitti | POST | `/webhook/nefalix/hbys/appointment-completed` |
| NPS yanıtı | POST | `/webhook/nefalix/nps/response` |
| Google yeni yorum | POST | `/webhook/nefalix/google/new-review` |
| eNPS yanıt | POST | `/webhook/nefalix/enps/response` |
| Sentinel mention | POST | `/webhook/nefalix/sentinel/mention` |
| Recall hasta listesi | POST | `/webhook/nefalix/recall/check-patients` |
| Inbox mesaj | POST | `/webhook/nefalix/inbox/incoming` |

Tam URL: `http://localhost:5678/webhook/...`

## Test Örnekleri

### NPS Promoter (8-10)
```bash
curl -X POST http://localhost:5678/webhook/nefalix/nps/response \
  -H "Content-Type: application/json" \
  -d '{"score":9,"patientName":"Ayşe","googleReviewUrl":"https://g.page/r/example/review","complaintFormUrl":"https://nefalixai.com/sikayet"}'
```

### NPS Detractor (1-7)
```bash
curl -X POST http://localhost:5678/webhook/nefalix/nps/response \
  -H "Content-Type: application/json" \
  -d '{"score":4,"patientName":"Ayşe","complaintFormUrl":"https://nefalixai.com/sikayet"}'
```

### HBYS tetikleme
```bash
curl -X POST http://localhost:5678/webhook/nefalix/hbys/appointment-completed \
  -H "Content-Type: application/json" \
  -d '{"patientName":"Ayşe Yılmaz","patientPhone":"905551234567","clinicName":"MediDent","doctorName":"Dr. Kaya","treatment":"implant","googleReviewUrl":"https://g.page/r/example/review","complaintFormUrl":"https://nefalixai.com/sikayet"}'
```

## Bağlanması Gereken Credential'lar

| Credential | Modüller |
|------------|----------|
| **OpenAI** | Tüm AI node'ları (✅ bağlı) |
| **WhatsApp Business API** | Feedback, Recall |
| **Slack** | Feedback alarm, Google onay, Sentinel, Inbox |
| **Google Business Profile** | Google yorum yayınlama (Aşama 3) |
| **İYS API** | Ticari WhatsApp öncesi izin kontrolü |

## PDF MVP Aşamaları

### Aşama 1 (şimdi) ✅
- Google yorum analizi + taslak yanıt
- Sentinel mention analizi
- Web chatbot

### Aşama 2 (credential sonrası)
- WhatsApp NPS gönderimi
- Promoter/Detractor yönlendirme canlı
- Slack alarmları

### Aşama 3 (SaaS)
- Dashboard
- Çok lokasyon
- HBYS native entegrasyon
- Google yorum otomatik yayınlama

## KVKK / İYS Notu

WhatsApp ticari mesajlarından önce **İYS izin kontrolü** node'u eklenmeli. Pilot için MediDent hasta onay formu ile manuel izin listesi (Google Sheet) kullanılabilir.
