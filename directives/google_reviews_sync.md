# Google Yorum Senkronu (Places API)

## Hedef
Tüm kliniklerin Google Maps yorumlarını doğrudan Google'dan çekip Supabase'e yazmak.

## Araçlar
| Araç | Rol |
|------|-----|
| `execution/sync-google-reviews.py` | CLI / VPS cron senkronu |
| `workflows/nefalix-09-google-reviews-sync.json` | n8n: 6 saatte bir + manuel webhook |
| Google Places API (New) | Text Search + Place Details (`reviews`) |

## Önkoşul

1. [Google Cloud Console](https://console.cloud.google.com/) → **Places API (New)** etkin
2. API key oluştur (HTTP referrer veya IP kısıtlı)
3. `.env` / VPS `.env`:
   ```
   GOOGLE_PLACES_API_KEY=AIza...
   ```

4. Migration uygula:
   ```bash
   npx supabase migration up
   # VPS: cd /opt/nefalix && npx supabase migration up
   ```

5. n8n env (docker-compose):
   - `GOOGLE_PLACES_API_KEY`
   - `SUPABASE_URL=http://host.docker.internal:54321`
   - `SUPABASE_SERVICE_ROLE_KEY=...`

## Çalıştırma

**Tek sefer (tüm klinikler):**
```bash
python3 execution/sync-google-reviews.py
```

**Tek klinik:**
```bash
python3 execution/sync-google-reviews.py --clinic-id 51738ea8-c12e-40ce-a0e2-42869496d76b
```

**n8n manuel webhook:**
```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/google/sync-reviews
```

**VPS cron (önerilen yedek):**
```cron
0 */6 * * * cd /opt/nefalix && set -a && source .env && python3 execution/sync-google-reviews.py >> /var/log/nefalix-google-sync.log 2>&1
```

## Veri modeli

| Alan | Kaynak |
|------|--------|
| `clinics.google_rating` | Places API |
| `clinics.google_review_count` | Places API (toplam) |
| `clinics.google_place_id` | Text Search veya mevcut URL |
| `google_reviews` | Son 5 yorum (API limiti) |

## AI taslak + yönetici onay

1. Senkron sonrası `draft-google-reviews.py` veya workflow `nefalix-10` → `draft_reply`
2. **Yeni düşük puan (≤4)** yorumlar otomatik **Sentinel** (`wf-04`) duygu analizine gider
3. Panel **Google** → **Yanıtla** → düzenle → **Onayla ve yanıtla**
3. `nefalix-11` webhook → `status=published`
4. Yanıt panoya kopyalanır + Google Haritalar açılır (GBP API ile otomatik yayın sonra)

Vercel: `N8N_GOOGLE_REVIEW_APPROVE_URL=https://api.nefalixai.com/webhook/nefalix/google/review-approve`

## Yeni klinik ekleme

`clinics` tablosuna kayıt eklerken en az biri gerekli:
- `google_place_id` (tercih)
- `google_maps_url` (ChIJ içeren tam link)
- `name` + `address` (Text Search ile çözülür)

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| `GOOGLE_PLACES_API_KEY eksik` | .env + docker compose restart n8n |
| `place_id bulunamadı` | Klinik adı/adres veya Maps URL düzelt |
| `REQUEST_DENIED` | Places API (New) billing etkin mi kontrol et |
| Panelde 5'ten fazla yorum yok | Normal — API max 5 döner; toplam KPI'da `google_review_count` |
| Tam yorum geçmişi | İleride Google Business Profile API (klinik OAuth) |

## Self-anneal notları
- Places API **eski** Places API değil — **Places API (New)** gerekli
- `google_reviews` upsert: `(clinic_id, external_review_id)` unique index
