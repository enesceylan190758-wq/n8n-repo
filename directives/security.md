# Güvenlik SOP — Nefalix

## Acil durum (sızdırma / ban / şüpheli erişim)

1. **VPS sıkılaştır:** `bash execution/security-harden-vps.sh`
2. **NPS / toplu WA kapat:** wf-01, wf-12, wf-13 deactivate (n8n UI veya import script)
3. **Aşağıdaki rotasyon listesini uygula** (öncelik sırasıyla)
4. **Supabase anon erişim:** Dış port kapalı olsa bile JWT secret'ı production'da **varsayılan demo key olmamalı**

## Bilinen riskler (Haz 2026 denetimi)

| Risk | Etki | Durum |
|------|------|--------|
| Supabase `54321` internete açık | Hasta ad/telefon (KVKK) anon key ile okunabilirdi | `security-harden-vps` ile DROP |
| Postgres `54322` açık | DB brute-force | Aynı script |
| Evolution `8080` açık | API saldırı yüzeyi | localhost + Caddy TLS |
| n8n-mcp `3000` açık | MCP metadata sızıntısı | localhost bind |
| Caddy `:80` → tüm IP'de n8n | Editor/webhook IP üzerinden | Caddyfile kaldırıldı |
| Script'lerde varsayılan `Nefalix2026!` | Repo klonlayan herkes bilir | Kaldırıldı — sadece `.env` |
| Sohbet / transcript'te paylaşılan şifreler | Estesoft, n8n, API key | **Rotasyon zorunlu** |
| n8n webhook'ları auth'suz | Herkes poll/NPS tetikleyebilir | NPS kapalı; ileride header secret |
| Evolution = resmi WA değil | Ban, İYS riski | Pilot; üretimde Meta WABA |
| `anon_read_*` RLS politikaları | Anon key ile tüm tablolar SELECT | Production'da kaldırılacak migration |

## VPS sıkılaştırma

```bash
bash execution/security-harden-vps.sh
# veya uzak: bash execution/security-harden-vps.sh root@VPS_IP
```

Yapılanlar:
- `chmod 600 /opt/nefalix/.env`
- `iptables DOCKER-USER` — 54321–54327, 8080, 3000 dışarıdan DROP
- `docker-compose.prod.yml` — Evolution/MCP `127.0.0.1` bind
- Caddy — ham IP ile n8n proxy kaldırıldı

**Doğrulama (Mac'ten, VPS dışı):**
```bash
curl -sf --max-time 3 http://VPS_IP:54321/ && echo ACIK || echo KAPALI
```

## Secret rotasyon checklist

Sızdıysa veya sohbette paylaştıysanız **hepsini** yenileyin:

| Secret | Nerede değiştirilir |
|--------|---------------------|
| n8n owner şifresi | n8n UI → Settings + VPS `.env` `N8N_PASSWORD` |
| `N8N_BASIC_AUTH_PASSWORD` | `.env` + `docker compose up -d n8n` |
| `N8N_ENCRYPTION_KEY` | ⚠️ Credential şifreleri — sadece yedek + planlı migration |
| `EVOLUTION_API_KEY` | `.env` + Evolution container recreate |
| `ESTESOFT_API_PASSWORD` / API key | Estesoft panel + `.env` |
| `SUPABASE_SERVICE_ROLE_KEY` | `supabase stop` → JWT rotate (ileri seviye) veya yeni VPS |
| `GOOGLE_PLACES_API_KEY` | GCP Console → kısıtla (IP/ref) |
| `GCP` service account | GCP IAM → yeni key, eskiyi sil |
| `DASHBOARD_SESSION_SECRET` | Vercel env + tüm kullanıcılar yeniden login |
| `DASHBOARD_USERS` şifreleri | Vercel env (hash yeniden üret) |
| `MCP_AUTH_TOKEN` | `.env` openssl rand -hex 32 |

**Estesoft:** Panelden API şifresini sıfırla; eski key'i revoke et.

**Vercel:** `vercel env rm` / `add` — `N8N_DASHBOARD_URL` secret değil ama dashboard user hash'leri secret.

## Güvenli operasyon kuralları

1. **Asla** gerçek şifreyi commit etme, directive'e yazma, sohbete yapıştırma
2. Pilot WhatsApp = **iş hattı**, kişisel numara bağlama
3. Poll / NPS ilk çalıştırmada **sadece son X saat** randevular (geçmişe toplu mesaj yok)
4. Rate limit: WA outbound max 1–2/dk
5. SSH: key-only, `PasswordAuthentication no` (VPS)
6. n8n editor: güçlü şifre + mümkünse IP allowlist (Caddy `remote_ip` matcher)

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| iptables reboot sonrası silindi | `netfilter-persistent` veya script'i cron @reboot |
| n8n import "N8N_PASSWORD gerekli" | Mac `.env` veya `export` ile çalıştır |
| Dashboard 401 | `DASHBOARD_SESSION_SECRET` rotasyonu sonrası yeniden login |
| Caddy sertifika yenileme | Port 80 açık kalmalı (sadece ACME + host redirect) |

## WhatsApp rate limit (wf-00 gateway)

Tüm Evolution `sendText` çağrıları tek kapıdan geçer: `POST /webhook/nefalix/whatsapp/send`

| Env | Varsayılan | Anlam |
|-----|------------|--------|
| `WHATSAPP_SEND_ENABLED` | `false` (VPS örnek) | `false` = hiç gönderme, sadece log |
| `WHATSAPP_MIN_INTERVAL_SEC` | 45 | İki mesaj arası min süre |
| `WHATSAPP_MAX_PER_HOUR` | 20 | Saatlik tavan |
| `WHATSAPP_MAX_BURST_5MIN` | 3 | 5 dk içinde max |

Log: `whatsapp_send_log`. Patch: `python3 execution/patch-whatsapp-rate-limit.py`

Mesaj gönderen WF: wf-01 NPS, wf-04 Sentinel (yalnız kritik), wf-05 Recall, wf-08 Inbox.

Sentinel: WA sadece `alert_urgent`; Google ≤4★ yeni yorumlar wf-09 → Sentinel.
