# Chatwoot (hazır WhatsApp inbox)

Evolution Manager yerine **Chatwoot** — isim, numara, sohbet.

| Ne | URL |
|----|-----|
| Chatwoot UI | https://evo.nefalix.com:8443/app |
| CRM gömülü | https://nefalix.com/nefalix-crm#WhatsappPanel |
| Giriş | `enes@nefalix.com` / `CHATWOOT_ADMIN_PASSWORD` (.env) |

## Kurulum (VPS)

```bash
cd /opt/nefalix
bash execution/setup-chatwoot.sh
```

Compose: `docker-compose.chatwoot.yml`. Evolution: `CHATWOOT_ENABLED=true`, set URL `http://chatwoot-rails:3000` (internal).

Inbox adı: **Nefalix CRM WhatsApp**.

## DNS (opsiyonel)

`chat.nefalix.com` A → VPS eklenince Caddy TLS + FRONTEND_URL güncelle; şimdilik `:8443`.

## Not

HTTP/2 underscore header sorunundan Evolution Chatwoot URL’si **internal** `http://chatwoot-rails:3000` olmalı.
