# Site Chat Tunnel

## Hedef
nefalixai.com chatbot'unun yerel n8n'e bağlanması (VPS olmadan geçici çözüm).

## Akış
```
nefalixai.com (Vercel) → cloudflared tunnel → localhost:5678 → Web Chatbot workflow
```

## Adımlar

1. Stack çalışıyor olmalı (`directives/start_stack.md`)

2. Tunnel başlat:
   ```bash
   cloudflared tunnel --url http://localhost:5678
   ```
   Çıkan URL örn: `https://xxxx.trycloudflare.com`

3. Landing'de webhook güncelle:
   - Dosya: `~/nefalix-landing/nefalix-chat.js`
   - `WEBHOOK_URL` → `https://xxxx.trycloudflare.com/webhook/8bb40d02-5ff5-4262-bfda-ebc6ea458a22/chat`

4. Vercel deploy:
   ```bash
   cd ~/nefalix-landing
   vercel --prod --yes
   ```

## Doğrula
```bash
curl -s -X POST "https://TUNNEL_URL/webhook/8bb40d02-5ff5-4262-bfda-ebc6ea458a22/chat" \
  -H "Content-Type: application/json" \
  -d '{"action":"sendMessage","sessionId":"test","chatInput":"Merhaba"}'
```
Yanıtta `"output"` olmalı.

## Edge Cases

| Sorun | Çözüm |
|-------|--------|
| Tunnel URL her restart'ta değişir | nefalix-chat.js + Vercel redeploy |
| Mac kapalı | Chat durur → VPS gerekli |
| CORS | Chat trigger allowedOrigins nefalixai.com içerir |

## Kalıcı çözüm
VPS (Hostinger KVM 2) + sabit domain — bu directive güncellenecek.
