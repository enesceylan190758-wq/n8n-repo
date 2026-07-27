# Nefalix İletişim / Mail Sistemi

Saha satış için kartvizit + mesaj kalıpları + **CRM Toplu Mail** (Hostinger SMTP).

## Canlı (CRM oturumu zorunlu)

Bu sayfalar dışarıya açık değil — `nefalix_crm` cookie yoksa giriş ekranı gelir:

| Ne | URL |
|----|-----|
| **Toplu Mail** | https://nefalix.com/toplu-mail |
| **İletişim / Ayarlar** | https://nefalix.com/mail → `#ayarlar` / `#kaliplar` |
| İmza | https://nefalix.com/iletisim/imza?kart=enes\|kadir |
| CRM giriş | https://nefalix.com/nefalix-crm |

Gate: `api/blog?action=crm-page&page=…` + `vercel.json` rewrite.

## Yanıtlar nereye düşer? (Gelen kutusu)

CRM içinde IMAP yok. Cevaplar **Reply-To** profiline gider:

| Profil | Giriş | Nereden bak |
|--------|--------|-------------|
| Enes | `enes@nefalix.com` | [Hostinger Webmail](https://webmail.hostinger.com/) veya Gmail |
| Kadir | `abdulkadir@nefalix.com` | aynı |

Toplu Mail sayfasında **Gelen kutusu** kartı / üst menü → Hostinger Webmail linki var.

- **From (gönderim):** `info@nefalix.com` (SMTP) veya kişisel stilinde profil maili
- **Reply-To:** seçilen profil

## Toplu Mail kuralları

1. **Yetkili adı + firma adı zorunlu** (elle mail veya kurum). Boşsa gönderilmez; `[İsim]` / `[Firma]` dolu gider.
2. **HTML imza** varsayılan açık: markalı teal kart + imza tablosu; metindeki kişi satırları “Saygılarımla,” sonrası kırpılır (çift imza yok).
3. Şablon konu/gövde UI’da düzenlenebilir (`customSubject` / `customBody`).

## Hostinger akış

```
CRM /toplu-mail → Vercel crm-outreach → VPS outreach-mail job
  → send-crm-outreach.py → smtp.hostinger.com
```

Limit: max 50 alıcı; saatte ~20; arada ~1 sn.

### Deploy

```bash
scp execution/send-crm-outreach.py execution/outreach-templates.json \
    execution/social-publish-webhook.py root@VPS:/opt/nefalix/execution/
ssh root@VPS 'docker restart nefalix-social-webhook'
cd nefalix-landing && vercel --prod --yes
```

### Env

VPS: `BLOG_SMTP_*`, `NEFALIX_INTERNAL_KEY`  
Vercel: `NEFALIX_INTERNAL_KEY` (+ `DASHBOARD_SESSION_SECRET` tercih)
