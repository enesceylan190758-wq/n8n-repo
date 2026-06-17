# Nefalix n8n Repo

Nefalix AI otomasyon altyapısı: **n8n workflow'ları** + **[n8n-mcp](https://github.com/czlonkowski/n8n-mcp)** (Cursor/Claude ile workflow üretimi).

## Ne var?

| Klasör / dosya | Açıklama |
|----------------|----------|
| `docker-compose.yml` | Yerel n8n + n8n-mcp (czlonkowski image) |
| `.cursor/mcp.json.example` | Cursor'da n8n-mcp bağlantısı |
| `workflows/` | Import edilebilir workflow şablonları |
| `workflow-sdk/` | Workflow SDK kaynak kodları (Cursor ile güncelleme) |
| `docs/SETUP.md` | Adım adım kurulum |

## Canlı ortam (şu an)

- **n8n Cloud:** https://enkahealthisterr.app.n8n.cloud
- **Web chatbot workflow:** `Nefalix AI - Web Chatbot` (aktif)
- **Site embed:** https://nefalixai.com → sağ alttaki chat balonu
- **Webhook:** `.../webhook/c1a80f17-6651-41fd-9a9e-716711162c04/chat`

## Hızlı başlangıç

### 1) Cursor + n8n-mcp (önerilen)

```bash
cp .cursor/mcp.json.example .cursor/mcp.json
```

n8n Cloud → **Settings → API** → API key oluştur → `mcp.json` içine yapıştır.

Cursor'da bu repo klasörünü aç → MCP'yi etkinleştir → chat'te workflow iste.

Kaynak: [czlonkowski/n8n-mcp — Cursor Setup](https://github.com/czlonkowski/n8n-mcp/blob/main/docs/CURSOR_SETUP.md)

### 2) Yerel Docker (n8n + n8n-mcp)

```bash
cp .env.example .env
# .env içinde N8N_ENCRYPTION_KEY ve MCP_AUTH_TOKEN doldur
docker compose pull
docker compose up -d
```

- n8n: http://localhost:5678
- n8n-mcp health: http://localhost:3000/health

### 3) Workflow import

n8n UI → **Workflows → Import from file** → `workflows/*.json`

Import sonrası **OpenAI** ve **Telegram** credential'larını bağlayın.

## Referans repolar

- [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) — MCP sunucusu (bu repoda Docker + Cursor config)
- [Zie619/n8n-workflows](https://github.com/Zie619/n8n-workflows) — Hazır workflow şablon kütüphanesi
- [n8n-io/n8n](https://github.com/n8n-io/n8n) — n8n kaynak kodu

## Nefalix workflow'ları

| Workflow | Kanal | Durum |
|----------|-------|-------|
| Nefalix AI - Web Chatbot | nefalixai.com embed | Aktif (cloud) |
| Nefalix AI - Telegram Chatbot | Telegram bot | Credential gerekli |

## Güvenlik

- `.env` ve API key'leri commit etmeyin
- Production workflow'ları AI ile düzenlemeden önce kopyalayın ([n8n-mcp uyarısı](https://github.com/czlonkowski/n8n-mcp#important-safety-warning))
