# Workflow Smoke Test

## Hedef
7 modül + chatbot'un webhook → n8n → Supabase zincirini doğrula.

## Araç
```bash
WAIT_AI=12 bash execution/test-all-workflows.sh
```

## Önkoşul
- `directives/start_stack.md` tamamlanmış
- `directives/import_workflows.md` tamamlanmış

## Test edilen endpoint'ler

| Modül | Webhook path |
|-------|----------------|
| NPS | `nefalix/nps/response` |
| HBYS | `nefalix/hbys/appointment-completed` |
| Google | `nefalix/google/new-review` |
| eNPS | `nefalix/enps/response` |
| Sentinel | `nefalix/sentinel/mention` |
| Recall | `nefalix/recall/check-patients` |
| Inbox | `nefalix/inbox/incoming` |
| Chat | `/webhook/8bb40d02-.../chat` |

## Başarı kriteri
Script sonu: `❌ 0 başarısız`

Manuel kontrol:
```bash
curl -s http://127.0.0.1:54321/rest/v1/nps_responses?select=count \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## Edge Cases

| Sorun | Çözüm |
|-------|--------|
| `clinic_id` FK hatası | MediDent UUID sabit olmalı: `51738ea8-c12e-40ce-a0e2-42869496d76b` |
| Sentinel `content` null | Webhook'ta `text` alanı gönder; normalize `body.text` okur |
| Recall integer hatası | `months_since_visit` Math.round ile kaydet |
| HBYS WhatsApp fail | WhatsApp → log stub (01 Feedback) |

## Çıktı
Supabase tablolarında yeni satırlar.
