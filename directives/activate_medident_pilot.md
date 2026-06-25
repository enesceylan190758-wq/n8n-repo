# Medident Pilot — Dashboard Otomasyonlarını Çalıştır

## Hedef
Medident İstanbul (`clinic_id`: `51738ea8-c12e-40ce-a0e2-42869496d76b`) için dashboard'a bağlı tüm n8n modüllerini aktif et ve doğrula.

## Önkoşul
- VPS veya Mac'te stack ayakta (`directives/start_stack.md` veya `directives/vps_setup.md`)
- `.env` içinde `OPENAI_API_KEY` (AI taslak / yorum analizi için)
- Vercel dashboard proxy VPS webhook'una işaret ediyor (`execution/update-vercel-vps-urls.sh`)

## Tek komut

**VPS üzerinde:**
```bash
cd /opt/nefalix
# .env'e OPENAI_API_KEY=sk-... ekleyin
bash execution/activate-medident-pilot.sh
```

**Mac'ten uzaktan (VPS açıkken):**
```bash
bash execution/activate-medident-pilot.sh root@2.27.101.119
```

## Script ne yapar?

1. Docker stack + Supabase kontrol / başlat
2. `setup-n8n-credentials.py` — Supabase + Vertex Gemini credential
3. `import-workflows.py` — 11 workflow import + activate
4. Evolution → Inbox webhook (`configure-evolution-webhook.sh`)
5. `sync-clinic-profile.py` — medidentistanbul.com profil verisi
6. `sync-google-reviews.py` — Places API (GOOGLE_PLACES_API_KEY varsa)
7. `test-all-workflows.sh` — webhook + Supabase smoke test

## Dashboard modülleri

| Modül | Webhook | Dashboard sekmesi |
|-------|---------|-------------------|
| Dashboard API | `GET nefalix/dashboard/data` | Tüm veri |
| NPS / Feedback | `nefalix/nps/response` | NPS |
| Google Review AI | `nefalix/google/new-review` | Google yorumları |
| eNPS | `nefalix/enps/response` | eNPS |
| Sentinel | `nefalix/sentinel/mention` | İtibar |
| Recall | `nefalix/recall/check-patients` | Recall |
| Inbox gelen | `nefalix/inbox/incoming` | Gelen kutusu |
| Inbox gönder | `POST nefalix/inbox/send` | Yanıt gönder |
| Google sync | `POST nefalix/google/sync-reviews` | Google yorumları (Places) |
| Google taslak AI | cron / manuel | Taslak yanıtlar |
| Google onay | `POST nefalix/google/review-approve` | Yönetici onayı |

## WhatsApp (Evolution)

QR henüz taranmadıysa:
```bash
bash execution/reset-evolution-qr.sh
# WhatsApp → Bağlı cihazlar → Cihaz bağla
```

## Başarı kriteri
- Script sonu: `✓ Tüm smoke testler geçti`
- https://nefalixai.com/dashboard — Medident verileri görünür
- Manager giriş: `akadirysr@gmail.com`

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| VPS SSH/HTTP timeout | Sunucumburada panel → VPS'i başlat / reboot |
| AI testleri fail | `.env` → `OPENAI_API_KEY` ekle, script'i tekrar çalıştır |
| Inbox send fail | Evolution QR tara; `configure-evolution-webhook.sh` |
| Dashboard boş | `sync-clinic-profile.py`; migration uygulandı mı kontrol et |
| Credential ID uyumsuz | `activate-medident-pilot.sh` credential'ları yeniden oluşturur |
| Supabase node "Empty JWT" | `setup-n8n-credentials.py` Supabase cred'i sil+yeniden oluşturur |
