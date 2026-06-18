# VPS Kurulum — Nefalix Production (Türkiye / KVKK)

## Hedef
Mac + geçici Cloudflare tunnel yerine **7/24 Türkiye lokasyonlu sunucu**: n8n, Evolution (WhatsApp), **Supabase (self-host)** — hasta verisi Türkiye'de kalır.

Dashboard arayüzü (`nefalixai.com`) Vercel'de kalabilir; **kişisel veri Supabase Postgres'te TR sunucusunda** tutulur. Vercel yalnızca oturum + API proxy (JSON geçişi); asıl veri katmanı TR.

## Mimari (veri Türkiye'de)

```
nefalixai.com (Vercel — sadece UI + auth proxy)
    └── /api/dashboard → https://api.nefalixai.com/webhook/...  (VPS TR)

VPS — İstanbul veri merkezi (Docker)
    ├── Caddy/Nginx (TLS, api.nefalixai.com)
    ├── n8n
    ├── Evolution API (WhatsApp)
    └── Supabase self-host (Postgres + Kong REST)
            └── patients, inbox, nps, google_reviews, …
```

**Neden Supabase Cloud (Frankfurt) değil?**  
Yönetilen Supabase'in TR bölgesi yok. KVKK açısından hasta/ad/telefon/yorum verisi için **self-host Supabase aynı TR VPS'te** (veya ikinci TR VPS'te) tercih edilir. Hukuki metin (Aydınlatma / açık rıza) ayrıca güncellenmeli.

## Türkiye sağlayıcı karşılaştırması (pilot)

| Sağlayıcı | Paket | RAM | Lokasyon | Yaklaşık fiyat | Not |
|-----------|-------|-----|----------|----------------|-----|
| [Sunucumburada](https://sunucumburada.com/vps-server-kirala/) | VPS-TR 12 GB | 12 GB / 4 CPU | İstanbul Datacasa Tier III | ~170 ₺/ay | Uygun fiyat, pilot için iyi |
| [VPS.TC](https://www.vps.tc/tr/vps) | NVMe #6 | 8 GB / 6 CPU | İstanbul | fiyat sitede | NVMe, limitsiz trafik seçenekleri |
| [BurtiNET](https://www.burtinet.com/sanal-sunucu) | VPS-3 | 8 GB | İstanbul, 3 ISP | fiyat sitede | Kurumsal ağ |
| [Turhost](https://www.turhost.com/sunucu/vps-server/) | VDS 8 | 8 GB ECC / 4 vCPU | Türk Telekom Gayrettepe Tier III | ~1.420 ₺/ay (KDV hariç) | Kurumsal, yedekleme, destek |
| [Radore](https://www.radore.com) | VDS | 8 GB+ | İstanbul | teklif | Finans/sağlık sektöründe yaygın |

**Pilot öneri (tek sunucu):** Sunucumburada **VPS-TR 12 GB** veya Turhost **VDS 8** (bütçe kurumsalsa).

**Ölçek büyüyünce:** n8n+Evolution bir VPS, Supabase ayrı VPS (her ikisi de TR).

## Minimum kaynak (self-host Supabase dahil)

| Kaynak | Tek VPS (pilot) | İki VPS (ayrılmış) |
|--------|-----------------|---------------------|
| RAM | **12–16 GB** | 8 GB (n8n+evo) + 8 GB (DB) |
| vCPU | 4–6 | 4 + 4 |
| Disk | 80–160 GB NVMe | 60 + 100 GB |
| OS | Ubuntu 24.04 LTS | aynı |

## Satın alma checklist

1. **Lokasyon: İstanbul / Türkiye** seç (Almanya/ABD seçme)
2. Ubuntu 24.04, SSH key
3. Sabit IPv4 → DNS: `api.nefalixai.com` A kaydı
4. Sağlayıcıdan **veri merkezinin Türkiye sınırları içinde** olduğunu teyit et (sözleşme / teknik doküman)

## Kurulum (tek komut — Mac'ten)

1. VPS satın al (Ubuntu 24.04, İstanbul, 12 GB RAM önerilir)
2. SSH key ekle
3. DNS (VPS IP alındıktan sonra):
   - `api.nefalixai.com` → A → VPS IP
   - `evo.nefalixai.com` → A → VPS IP
4. Mac'ten deploy:
   ```bash
   cd ~/n8n-repo
   cp .env.vps.example .env   # N8N_PUBLIC_HOST, ACME_EMAIL düzenle
   bash execution/deploy-to-vps.sh root@VPS_IP
   ```
5. Vercel bağla:
   ```bash
   bash execution/update-vercel-vps-urls.sh
   ```

Sunucuda manuel:
```bash
cd /opt/nefalix && bash execution/setup-vps.sh
```

## Workflow Supabase URL

- Mac: `http://host.docker.internal:54321`
- TR VPS: `http://kong:8000` (Docker network) veya `https://db.nefalixai.com` (internal)

`execution/patch-supabase-workflows.py` ile güncelle.

## Vercel (tunnel kalkar)

```env
N8N_DASHBOARD_URL=https://api.nefalixai.com/webhook/nefalix/dashboard/data
N8N_INBOX_SEND_URL=https://api.nefalixai.com/webhook/nefalix/inbox/send
```

`execution/setup-dashboard-tunnel.sh` artık gerekmez.

## KVKK notları (özet — hukuk danışmanı onayı)

- Hasta verisi TR Postgres'te; yedekler de TR'de (farklı DC veya aynı sağlayıcı TR lokasyonu).
- OpenAI / harici AI: prompt'ta kişisel veri minimizasyonu; gerekirse TR veya EU işleme sözleşmesi.
- Vercel (ABD): yalnızca panel oturumu; hasta tabloları Vercel Postgres'te **tutulmaz**.

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| 8 GB RAM yetmez | 12 GB'ye yükselt veya Supabase ayrı VPS |
| WhatsApp QR | `execution/reset-evolution-qr.sh` (sunucuda) |
| Mac kapanınca panel durur | VPS geçişi sonrası çözülür |

## Self-anneal

- **2026-06-18:** Mac + trycloudflare sık kopuyor → TR VPS hedefi.
- **2026-06-18:** KVKK — veri TR'de kalsın → Supabase self-host TR, sağlayıcı listesi eklendi.
