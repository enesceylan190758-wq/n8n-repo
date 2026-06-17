# Nefalix n8n + n8n-mcp Kurulum

## A) Cursor ile n8n Cloud (üretim — şu an kullandığımız)

1. **n8n API key al**
   - https://enkahealthisterr.app.n8n.cloud
   - Settings → API → Create API Key

2. **Cursor MCP config**
   ```bash
   cd n8n-repo
   cp .cursor/mcp.json.example .cursor/mcp.json
   ```
   `N8N_API_KEY` değerini yapıştır.

3. **Cursor'da**
   - Bu klasörü workspace olarak aç
   - Settings → MCP → `n8n-mcp` aktif olsun
   - Chat: *"Diş kliniği için WhatsApp review daveti workflow'u oluştur"*

4. **n8n-mcp ne yapar?**
   - 1800+ node dokümantasyonu
   - Workflow oluşturma / güncelleme / validate
   - Template arama (Zie619 tarzı şablon mantığı MCP içinde)

Kaynak: https://github.com/czlonkowski/n8n-mcp

---

## B) Yerel Docker (geliştirme)

```bash
cp .env.example .env
```

`.env` doldur:
```bash
openssl rand -hex 32   # N8N_ENCRYPTION_KEY
openssl rand -hex 32   # MCP_AUTH_TOKEN (min 32 karakter)
```

```bash
docker compose pull
docker compose up -d
```

İlk giriş: http://localhost:5678 (admin / .env şifresi)

Local n8n API key → `.env` içine `N8N_API_KEY=` → `docker compose restart n8n-mcp`

---

## C) Workflow'ları içe aktarma

1. n8n → Import → `workflows/nefalix-web-chatbot.json`
2. OpenAI credential bağla
3. Publish / Activate
4. Embedded chat için Web Chat node → Chat URL'yi kopyala → site `nefalix-chat.js`

---

## D) Site chatbot bağlantısı

Repo: `nefalix-landing` (ayrı proje)

```
nefalixai.com → nefalix-chat.js → n8n webhook → AI Agent
```

Webhook (production):
```
https://enkahealthisterr.app.n8n.cloud/webhook/c1a80f17-6651-41fd-9a9e-716711162c04/chat
```

---

## E) Modal.com (ileride)

Chatbot **Modal'da çalışmaz** — n8n'de kalır.

Modal, `AJAN SISTEMLERI.zip` içindeki gibi **otomasyon üreten ajan** için (directive + Python + webhook).

Sıra: önce n8n chatbot stabil → sonra Modal ajan.
