# Klinik CRM — Düzenleme ve Bakım (Abdülkadir / Medident)

## Hedef

Medident pilotunda **Klinik CRM** (`/klinik-crm`) günlük operasyon aracıdır: lead → atama → not/segment → **Dinamik Arama** → randevu.

Abdülkadir bu modülde **panel kullanımı** ve **Cursor ile düzenleme** (UI, iş kuralı, segment) devam edebilir.

## İki CRM — karıştırma

| Ürün | URL | Kim | Veri |
|------|-----|-----|------|
| **Klinik CRM** | `https://nefalix.com/klinik-crm` | Medident ekibi | Supabase `crm_*` tabloları |
| **Saha CRM** | `https://nefalix.com/crm` · `/saha` | Nefalix iç satış | `nefalix_state` JSON blob |
| **Kurum CRM (ana)** | `https://nefalix.com/nefalix-crm` | Nefalix ekip | `nefalix_state` id=2 |

Bu directive **Klinik CRM** içindir. Saha CRM ayrı üründür (`nefalix-landing/crm.html`).

## Canlı giriş (Abdülkadir)

1. `https://nefalix.com/klinik-crm` veya `https://nefalix.com/hasta-crm` (Stella UI)
2. Kullanıcı kodu: `abdulkadir` (şifre yok — kod Supabase `crm_users` ile eşleşir)
3. Diğer kodlar: `enes`, `kader` (temsilci/yönetici rolleri `crm_users.rol` alanından)

Rol `yonetici` ise tüm dinamik arama listesini `?all=1` ile görür; `temsilci` yalnızca kendine atananları görür.

## Düzenleme nerede?

| Ne düzenlenir | Dosya / yer |
|---------------|-------------|
| Arayüz (ekran, buton, liste) | `nefalix-landing/klinik-crm.html` veya `nefalix-hasta-crm-app/*.dc.html` |
| Hasta CRM store (API) | `nefalix-landing/nefalix-hasta-crm-app/store.js` |
| Pack hasta CRM | `execution/pack-nefalix-hasta-crm.py` |
| API + iş kuralları | `nefalix-landing/api/_lib/clinic-crm.js` |
| URL rewrite | `nefalix-landing/vercel.json` (`/api/clinic/*`, `/hasta-crm`) |
| Segment etiketleri, gün offset | Supabase `crm_segments` — `docs/stella_segments.csv` |
| Referans kaynakları | Supabase `crm_reference_sources` — `docs/stella_reference_sources.csv` |
| Stella geçiş SOP | `directives/stella_migration.md` |
| Migration | `supabase/migrations/20260727120000_crm_stella_phase1.sql` |
| Kullanıcı ekleme / rol | Supabase `crm_users` |
| Ürün spec (iş kuralı referans) | `docs/Nefalix_Urun_Mimarisi.md` §4.1 |
| Estesoft → NPS (HBYS) | `directives/estesoft_integration.md` |

**Repo:** UI/API değişikliği **`nefalix-landing`** workspace'inde yapılır. Bu repo (`n8n-repo`) spec + n8n + migration içindir.

## Kritik iş kuralları (değiştirmeden önce oku)

### Dinamik Arama

- Cron yok. Liste tamamen `crm_contacts.next_call_date` alanına dayanır.
- Not kaydında segment seçilince:  
  `next_call_date = (not_tarihi || bugün) + segment.gun_offset` (`gun_offset` min 1)
- **Dinamik segment** (`show_in_dynamic=true`): Ulaşılamadı (+1), Teklif Verildi (+1), Takip (+2), Orta Vadede (+7)…
- **Kapanış segmenti** (`show_in_dynamic=false`): Satıldı, Süreci Biten, Tedaviye Uygun Değil → `next_call_date=null`; `status=arsiv`
- **5× ulaşılamadı:** `ulasilamadi_tekrar_aranacak` notlarında `dynamic_attempt_count` artar; 5’te otomatik `5_kez_ulasilamadi` + arşiv
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

## P0 canlı (2026-07-27)

Lead, atama, dinamik arama, not, randevu, danışan düzenleme, teklif, basit ödeme, ay sonu rapor.

| Ürün | URL |
|------|-----|
| Hasta CRM (Stella UI) | `https://nefalix.com/hasta-crm` |
| Klinik CRM (basit) | `https://nefalix.com/klinik-crm` |

- **Store + API:** `nefalix-hasta-crm-app/store.js` → `clinic-*` (`sbCrmRequest` / `SUPABASE_URL_PROD`)
- **Import:** `execution/import-stella-definitions.py --prod`, `import-stella-crm.py --prod`
- **Paralel koşu SOP:** `directives/stella_migration.md`
- **Spec:** `docs/Stella_Phase1_Spec.md`

## P1

- Meta FB lead otomatik → `clinic-lead-intake`
- Teklif PDF
- WhatsApp panel (Evolution) hasta kartı
- Stella tam not/teklif geçmiş import

## Cursor — Abdülkadir ilk prompt

```text
Proje: nefalix-landing (Klinik CRM) + n8n-repo (spec)
Önce oku: n8n-repo/.tmp/handoff.md, directives/clinic_crm.md, docs/Nefalix_Urun_Mimarisi.md §4.1
Canlı: https://nefalix.com/klinik-crm veya /hasta-crm — giriş kodu abdulkadir
Düzenlenecek dosyalar: nefalix-hasta-crm-app/store.js, api/_lib/clinic-crm.js
Önce oku: directives/stella_migration.md
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
