# Workflow Import

## Hedef
`workflows/` altındaki JSON'ları yerel n8n'e import et ve aktifleştir.

## Araç
```bash
python3 execution/import-workflows.py
```

## Ortam değişkenleri (opsiyonel)
- `N8N_URL` — default `http://localhost:5678`
- `N8N_EMAIL` / `N8N_PASSWORD` — `.env` veya default pilot cred
- `N8N_OPENAI_CRED_ID` — OpenAI credential id

## Atlanan dosyalar
- `nefalix-web-chatbot.json` (zaten var)
- `nefalix-telegram-chatbot.json`

## Sonrası
Workflow değişikliği yaptıysan bu script'i tekrar çalıştır — PATCH + activate yapar.

## Edge Cases

| Sorun | Çözüm |
|-------|--------|
| Login fail | `.env` içinde N8N_PASSWORD kontrol |
| OpenAI node boş | Script `gpt-4o-mini` ve cred id enjekte eder |
| Webhook 404 | Workflow active değil — script activate çağırır |

## Self-anneal notları
- Supabase node'ları `patch-supabase-workflows.py` ile eklenir (ayrı script)
- WhatsApp credential yoksa HTTP node yerine **Set log stub** kullan (01 Feedback, 05 Recall)
