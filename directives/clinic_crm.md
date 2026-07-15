# Klinik CRM (Stella mantığı)

## Ne bu?
Estesoft Stella iş mantığının Nefalix kopyası — Medident pilot klinik için lead → atama → not/segment → Dinamik Arama → randevu döngüsü. Saha CRM (`/crm`) ve klinik dashboard (`/dashboard`) ile ayrı üründür.

Plan/spec: `docs/nefalix-stella-crm-plan.md` · Excel envanter: `docs/Nefalix_Stella_CRM_Plani.xlsx`

## Adres
- Canlı: https://nefalix.com/klinik-crm
- Giriş: yalnızca kullanıcı adı — `enes` (yönetici) · `abdulkadir` · `kader` (temsilci)
- Kullanıcılar DB'de: `public.crm_users` (kod + rol). Yeni kullanıcı = tabloya insert, kod deploy gerekmez.

## Veri katmanı (Supabase, VPS self-host)
Migration: `supabase/migrations/20260715120000_clinic_crm.sql`

| Tablo | İçerik |
|-------|--------|
| `crm_users` | Giriş kodu, ad, rol (`yonetici`/`temsilci`) |
| `crm_segments` | Stella segment kataloğu: `show_in_dynamic` + `gun_offset` |
| `crm_contacts` | Lead + danışan tek tablo (`stage`: lead/danisan, `status`: aktif/arsiv), `next_call_date` |
| `crm_contact_notes` | Not geçmişi (not + segment + yazan) |
| `crm_appointments` | Randevular (saat, hizmet, personel, oda, tip, durum) |

Erişim yalnızca `service_role` (RLS yok, grant bazlı).

### Dinamik Arama mantığı (cron YOK)
Not kaydında segment seçilince: `next_call_date = (not tarihi || bugün) + segment.gun_offset`.
Dinamik Arama ekranı = `next_call_date <= bugün AND status = aktif` sorgusu — tarih geçtikçe kayıt kendiliğinden listeye düşer.
- Dinamik segmentler (`show_in_dynamic=true`): Ulaşılamadı (+1), Teklif Verildi (+1), Takip (+2), Orta Vadede (+7)…
- Kapanış segmentleri (`show_in_dynamic=false`): Satıldı, Süreci Biten, Tedaviye Uygun Değil → `next_call_date=null`; bu üçü ayrıca `status=arsiv` yapar.
- Offset değiştirmek = `crm_segments.gun_offset` update; kod değişmez.

## API (Vercel — Hobby function limiti: hepsi api/blog.js altında)
Modül: `nefalix-landing/api/_lib/clinic-crm.js` · Rewrite'lar: `vercel.json`

| Endpoint | İş |
|----------|-----|
| `POST /api/clinic/login` `{kod}` | Cookie oturum (`nefalix_clinic`, 14 gün, HMAC) |
| `GET /api/clinic/bootstrap` | Oturum + segment kataloğu + kullanıcı listesi |
| `GET /api/clinic/leads?stage=lead\|danisan\|all&q=` · `POST` | Liste / manuel kayıt |
| `POST /api/clinic/assign` | Temsilciye ata → `stage=danisan`, `next_call_date=bugün` |
| `GET /api/clinic/dynamic?pool=1&all=1` | Dinamik kuyruk (temsilci bazlı; pool=atanmamış; all=yönetici tümü) |
| `POST /api/clinic/note-save` | Not + segment → `next_call_date` hesabı |
| `GET/POST /api/clinic/contact` | Danışan kartı (bilgi+not+randevu) / güncelleme |
| `GET/POST /api/clinic/appointments` | Takvim listele (`from`/`to`) / oluştur / güncelle |
| `POST /api/clinic/lead-intake` | **Public** site formu lead'i (honeypot `website` alanı; telefon dedup) |

## Otomatik lead girişi
1. **WhatsApp:** Evolution → n8n `nefalix-06-inbox-routing` → `CRM Lead Upsert` code node — telefon `crm_contacts`'ta yoksa `stage=lead`, kaynak `WHATSAPP <instance>` ile insert. Varsa atlar (dedup).
2. **Site demo formu:** `shared.js` guided demo formu submit'te `/api/clinic/lead-intake`'e fire-and-forget POST atar (cal.com akışını bozmaz).

## Deploy
- **UI + API:** `cd ~/nefalix-landing && vercel --prod --yes`
- **Migration (VPS prod):**
  ```bash
  scp supabase/migrations/<dosya>.sql root@93.127.186.45:/opt/nefalix/supabase/migrations/
  ssh root@93.127.186.45 'docker exec -i supabase_db_n8n-repo psql -U postgres -v ON_ERROR_STOP=1 < /opt/nefalix/supabase/migrations/<dosya>.sql'
  ```
- **Workflow (tek dosya import):** scp ile `/opt/nefalix/workflows/` sonra VPS'te `import-workflows.py`'nin `import_workflow()` fonksiyonu ile tek dosya (bkz. self-anneal).

## Kapsam durumu
- **Canlı (P0):** giriş, Dinamik Arama (+Havuz), Lead listesi + atama, Danışan listesi/kartı, not+segment, randevu takvimi + detay modal + durum güncelleme, WhatsApp/site lead intake
- **Sonra (P1/P2):** Kasa/Gider, Teklifler, Raporlar, WhatsApp panel, Salesline — plan: `docs/nefalix-stella-crm-plan.md` §5-6

## Self-anneal
- **2026-07-15:** Lokal Supabase kapalıyken `npx supabase migration up` bağlanamıyor → prod migration doğrudan VPS `supabase_db_n8n-repo` container'ına psql ile uygulanır (yukarıdaki komut).
- **2026-07-15:** `import-workflows.py` hepsini import eder; tek workflow için VPS'te `importlib` ile modül yükleyip `iw.login(); iw.import_workflow(Path('workflows/nefalix-06-inbox-routing.json'))` çağır.
- **2026-07-15:** Vercel Hobby function limiti — yeni endpoint dosyası AÇMA; `api/blog.js` action dispatch + `api/_lib/clinic-crm.js` kalıbını kullan.
