# Site Chat (Sabit VPS URL)

## Hedef
nefalixai.com chatbot → `api.nefalixai.com` üzerinden n8n Web Chatbot workflow.

## Akış
```
nefalixai.com (Vercel) → api.nefalixai.com/webhook/{id}/chat → Nefalix AI - Web Chatbot
```

## Kurulum

1. Web chatbot'u VPS'e import et:
   ```bash
   python3 execution/import-web-chatbot.py
   ```
   Çıktıdaki `CHAT_WEBHOOK_URL=` satırını kopyala.

2. Landing + Vercel:
   ```bash
   export N8N_CHAT_WEBHOOK_URL='https://api.nefalixai.com/webhook/....../chat'
   bash execution/update-vercel-vps-urls.sh
   ```

   Veya `nefalix-landing/nefalix-chat.js` içinde `WEBHOOK_URL` doğrudan güncelle + `vercel --prod`.

## Doğrula
```bash
curl -s -X POST "$N8N_CHAT_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"sendMessage","sessionId":"test","chatInput":"Merhaba"}'
```
Yanıtta `"output"` olmalı.

## Edge Cases

| Sorun | Çözüm |
|-------|--------|
| 404 webhook not registered | `import-web-chatbot.py` + workflow active |
| CORS | Chat trigger `allowedOrigins` nefalixai.com içerir |
| Model hatası | Vertex credential + `GCP_PROJECT_ID` VPS .env |

## Eski (tunnel) — kullanmayın
`trycloudflare.com` geçici çözümdü; Mac kapalıyken chat dururdu.
