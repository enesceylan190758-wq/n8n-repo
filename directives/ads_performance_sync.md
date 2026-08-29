# Reklam Performans Senkronu (Meta Graph API + Google Ads API)

## Hedef
Klinik başına bağlı Meta (Facebook/Instagram) ve Google Ads hesaplarının günlük
kampanya metriklerini (harcama, gösterim, tıklama, lead) Supabase'e çekip
Dashboard panelinde tek yerden göstermek — reklam yönetimini de Nefalix üzerinden
takip edebilmek için.

## Araçlar
| Araç | Rol |
|------|-----|
| `execution/sync-ads-performance.py` | CLI / VPS cron senkronu |
| `workflows/nefalix-20-ads-performance-sync.json` | n8n: 12 saatte bir + manuel webhook |
| `workflows/nefalix-07-dashboard-api.json` | Panel `adAccounts` + `adInsights` alanlarını döner |
| Meta Graph API (Marketing API, `/insights`) | Facebook + Instagram kampanya verisi |
| Google Ads API (GAQL, `searchStream`) | Google Ads kampanya verisi |

## Veri modeli
| Tablo | Amaç |
|-------|------|
| `ad_accounts` | Klinik ↔ platform (`meta`/`google`) ↔ hesap ID eşlemesi, `status` (`active`/`paused`/`token_expired`) |
| `ad_insights_daily` | Günlük kampanya metrikleri — unique `(clinic_id, platform, campaign_id, date)` |

Migration: `supabase/migrations/20260829120000_ads_performance.sql`

## Önkoşul — Meta (Facebook/Instagram)

1. [Meta for Developers](https://developers.facebook.com/) → uygulama oluştur (Business tipi)
2. Uygulamaya **Marketing API** ürünü ekle
3. İzin: **ads_read** (kampanya okuma yeterli, ads_management gerekmez)
4. **Access token:**
   - Graph API Explorer'dan kısa ömürlü token al → `ads_read` izniyle
   - Uzun ömürlü token'a çevir (60 gün):
     ```
     GET https://graph.facebook.com/v21.0/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id={app-id}&client_secret={app-secret}
       &fb_exchange_token={short-lived-token}
     ```
   - **Sistem kullanıcısı (system user) token'ı önerilir** — süresi dolmaz, Business Manager → Sistem Kullanıcıları'ndan üretilir
5. `.env`:
   ```
   META_ACCESS_TOKEN=EAAxxxxx...
   ```
6. `ad_accounts` tablosuna kayıt ekle:
   ```sql
   INSERT INTO ad_accounts (clinic_id, platform, account_id, account_name)
   VALUES ('51738ea8-c12e-40ce-a0e2-42869496d76b', 'meta', 'act_1234567890', 'MediDent Kartal - Meta');
   ```
   `account_id` formatı: `act_<ad_account_id>` (Business Manager → Reklam Hesapları'ndan).

## Önkoşul — Google Ads

1. [Google Ads API Center](https://ads.google.com/aw/apicenter) → **developer token** al (yeni token'lar "test" seviyesinde başlar, yalnızca kendi test hesabına erişir — prod erişim için Google onayı gerekir)
2. Google Cloud Console → OAuth 2.0 client (Desktop/Web) oluştur, **Google Ads API** kapsamı ekle
3. OAuth flow ile **refresh token** üret (bir kere yapılır, kalıcıdır)
4. Refresh token'dan **access token** üret (kısa ömürlü, ~1 saat — cron ile yenilenmeli):
   ```
   POST https://oauth2.googleapis.com/token
     client_id={client-id}&client_secret={client-secret}
     &refresh_token={refresh-token}&grant_type=refresh_token
   ```
5. `.env`:
   ```
   GOOGLE_ADS_DEVELOPER_TOKEN=...
   GOOGLE_ADS_ACCESS_TOKEN=...        # kısa ömürlü — periyodik yenilenmeli
   GOOGLE_ADS_LOGIN_CUSTOMER_ID=...   # yalnızca MCC (manager hesabı) üzerinden erişiliyorsa
   ```
6. `ad_accounts` tablosuna kayıt ekle, `account_id` = müşteri ID (`123-456-7890` formatında da olur, script `-` karakterlerini temizler).

**Not:** `GOOGLE_ADS_ACCESS_TOKEN` kısa ömürlü olduğu için otomatik yenileme henüz kurulmadı —
şimdilik manuel/cron ile `refresh_token` üzerinden yenilenip `.env`'e yazılmalı. İleride
`execution/refresh-gcp-access-token.py` benzeri bir `refresh-google-ads-token.py` eklenebilir.

## Migration uygula

```bash
npx supabase migration up
# VPS: cd /opt/nefalix && npx supabase migration up
```

## Çalıştırma

**Tek sefer (tüm hesaplar, son 7 gün):**
```bash
python3 execution/sync-ads-performance.py
```

**Tek platform / klinik / gün aralığı:**
```bash
python3 execution/sync-ads-performance.py --platform meta --clinic-id 51738ea8-c12e-40ce-a0e2-42869496d76b --days 30
```

**n8n manuel webhook:**
```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/ads/sync
```

**VPS cron (önerilen yedek, 12 saatte bir):**
```cron
0 */12 * * * cd /opt/nefalix && set -a && source .env && python3 execution/sync-ads-performance.py >> /var/log/nefalix-ads-sync.log 2>&1
```

## Panelde gösterim

`nefalix-07-dashboard-api.json` artık `adAccounts` ve `adInsights` alanlarını döner
(`GET /webhook/nefalix/dashboard/data`). Panel tarafında klinik bazlı grafik (harcama,
lead, CPC trend) bu iki alandan türetilir — henüz frontend grafiği eklenmedi, veri
katmanı hazır.

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| `META_ACCESS_TOKEN eksik/geçersiz` | Yeni token üret (sistem kullanıcısı token'ı önerilir, süresi dolmaz) |
| Meta `OAuthException` (code 190) | Token süresi dolmuş — `ad_accounts.status` otomatik `token_expired` olur, yeni token gerekir |
| Google Ads `UNAUTHENTICATED` | `GOOGLE_ADS_ACCESS_TOKEN` süresi dolmuş (kısa ömürlü) — refresh token'dan yenile |
| Google Ads developer token "test" seviyesinde | Yalnızca kendi test hesabına erişir — prod klinik hesapları için Google onayı (basic access) gerekir |
| `ad_accounts` kaydı yok | Script/workflow sessizce hiçbir şey yapmaz — önce klinik↔hesap eşlemesi eklenmeli |
| Meta `spend` para birimi | Reklam hesabının kendi para birimi döner; `currency` alanı şimdilik sabit `TRY` yazılıyor — çoklu para birimi gerekirse Meta `account_currency` alanı eklenmeli |

## Self-anneal notları
- İlk kurulumda Meta/Google token'ı alınmış ama süresi dolmuş — bir dahaki sefere
  **sistem kullanıcısı token'ı (Meta)** ve **kalıcı refresh token (Google)** kullanılarak
  tekrar tekrar süresi dolma sorunu önlenmeli.
- `ad_insights_daily` upsert anahtarı `(clinic_id, platform, campaign_id, date)` —
  google_reviews senkron desenindeki gibi var/yok kontrolü ile GET+PATCH/POST yapılıyor.
