# Klinik CRM — Düzenleme ve Bakım (Abdülkadir / Medident)

## Hedef

Medident pilotunda **Klinik CRM** (`/klinik-crm`) günlük operasyon aracıdır: lead → atama → not/segment → **Dinamik Arama** → randevu.

Abdülkadir bu modülde **panel kullanımı** ve **Cursor ile düzenleme** (UI, iş kuralı, segment) devam edebilir.

## İki CRM — karıştırma

| Ürün | URL | Kim | Veri |
|------|-----|-----|------|
| **Klinik CRM** | `https://nefalixai.com/klinik-crm` | Medident ekibi | Supabase `crm_*` tabloları |
| **Saha CRM** | `https://nefalixai.com/crm` | Nefalix iç satış | `nefalix_state` JSON blob |

Bu directive **Klinik CRM** içindir. Saha CRM ayrı üründür (`nefalix-landing/crm.html`).

## Canlı giriş (Abdülkadir)

1. `https://nefalixai.com/klinik-crm`
2. Kullanıcı kodu: `abdulkadir` (şifre yok — kod Supabase `crm_users` ile eşleşir)
3. Diğer kodlar: `enes`, `kader` (temsilci/yönetici rolleri `crm_users.rol` alanından)

Rol `yonetici` ise tüm dinamik arama listesini `?all=1` ile görür; `temsilci` yalnızca kendine atananları görür.

## Düzenleme nerede?

| Ne düzenlenir | Dosya / yer |
|---------------|-------------|
| Arayüz (ekran, buton, liste) | `nefalix-landing/klinik-crm.html` |
| API + iş kuralları | `nefalix-landing/api/_lib/clinic-crm.js` |
| URL rewrite | `nefalix-landing/vercel.json` (`/api/clinic/*`) |
| Segment etiketleri, gün offset | Supabase `crm_segments` |
| Kullanıcı ekleme / rol | Supabase `crm_users` |
| Ürün spec (iş kuralı referans) | `docs/Nefalix_Urun_ve_Mimari_Aktarim.md` §4.1 |
| Estesoft → NPS (HBYS) | `directives/estesoft_integration.md` |

**Repo:** UI/API değişikliği **`nefalix-landing`** workspace'inde yapılır. Bu repo (`n8n-repo`) spec + n8n + migration içindir.

## Kritik iş kuralları (değiştirmeden önce oku)

### Dinamik Arama

- Cron yok. Liste tamamen `crm_contacts.next_call_date` alanına dayanır.
- Not kaydında segment seçilince:  
  `next_call_date = (not_tarihi || bugün) + segment.gun_offset` (`gun_offset` min 1)
- **Dinamik segment** (`show_in_dynamic=true`): Ulaşılamadı (+1), Teklif Verildi (+1), Takip (+2), Orta Vadede (+7)…
- **Kapanış segmenti** (`show_in_dynamic=false`): Satıldı, Süreci Biten, Tedaviye Uygun Değil → `next_call_date=null`; bu üçünde `status=arsiv`
- Sorgu: `status=aktif AND next_call_date <= bugün`

### Atama

- `assign` → `stage=danisan`, `assigned_to=user_id`, `next_call_date=bugün` (hemen arama listesine düşer)

### Danışan düzenleme (panel)

- Danışan kartında **✏️ Düzenle** → ad, telefon, kaynak vb. güncellenir (`POST /api/clinic/contact`)

Kod referansı: `clinic-crm.js` → `noteSave`, `dynamicList`, `assign`, `contact`.

## Segment / kullanıcı düzenleme (Supabase)

Tablolar canlı Supabase'te; migration henüz `n8n-repo/supabase/migrations/` altında olmayabilir — değişiklik önce staging veya Enes onayı ile.

**Segment örneği:**
```sql
-- Etiket veya offset değiştir
UPDATE crm_segments
SET label = 'Teklif Verildi', gun_offset = 1, show_in_dynamic = true
WHERE code = 'teklif_verildi';
```

**Yeni temsilci:**
```sql
INSERT INTO crm_users (kod, ad, rol, aktif)
VALUES ('yeni_kod', 'Ad Soyad', 'temsilci', true);
```

Roller: `temsilci` | `yonetici`

## Deploy (UI/API değişikliği sonrası)

```bash
cd /Users/enesceylan/nefalix-landing
vercel --prod --yes
```

Deploy öncesi mobil (390px) ve giriş akışını kontrol et. `.env` / secret commit etme.

## Henüz yapılmayan (P1/P2)

P0 canlı: lead, atama, dinamik arama, not, randevu, danışan düzenleme.

Planlanan ama kod yok:
- Kasa / ödeme takibi
- Teklif PDF
- Raporlar
- WhatsApp panel entegrasyonu (wf-06 lead upsert kısmen var)

Abdülkadir öncelikle **P0 akışını Medident operasyonuna göre ince ayar** (segment isimleri, offset, UI metinleri) yapabilir.

## Cursor — Abdülkadir ilk prompt

```text
Proje: nefalix-landing (Klinik CRM) + n8n-repo (spec)
Önce oku: n8n-repo/.tmp/handoff.md, directives/clinic_crm.md, docs/Nefalix_Urun_ve_Mimari_Aktarim.md §4.1
Canlı: https://nefalixai.com/klinik-crm — giriş kodu abdulkadir
Düzenlenecek dosyalar: klinik-crm.html, api/_lib/clinic-crm.js
Kurallar: Dinamik Arama next_call_date mantığını bozma; .env commit etme; deploy için onay iste.
Görev: [buraya Medident'ten gelen düzenleme isteğini yaz]
```

## Edge cases

| Durum | Çözüm |
|-------|--------|
| Giriş "kullanıcı adı hatalı" | `crm_users` tablosunda `kod=abdulkadir` ve `aktif=true` kontrol |
| Dinamik listede kayıt yok | `next_call_date` bugün veya geçmiş mi; `status=aktif` mi; atama var mı |
| Segment değişti ama liste güncellenmedi | Yeni not kaydı gerekir; eski `next_call_date` otomatik silinmez |
| Estesoft NPS çift mesaj | Estesoft kendi anketini kapat — `directives/estesoft_integration.md` |
