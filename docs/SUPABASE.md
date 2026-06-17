# Supabase Kurulum — Nefalix

## Yerel (Docker — önerilen geliştirme)

```bash
cd /Users/enesceylan/n8n-repo
export PATH="$HOME/.local/node/bin:$PATH"
npx supabase start
```

Çıktıdaki değerleri `.env` dosyana ekle:

```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

Migration'ları uygula (start sırasında otomatik veya):

```bash
npx supabase db reset
```

Studio: http://127.0.0.1:54323

---

## Cloud (production)

1. https://supabase.com → New Project
2. SQL Editor → `supabase/migrations/20260617190000_nefalix_platform.sql` içeriğini yapıştır → Run
3. Settings → API → URL + `service_role` key → `.env`

---

## n8n'de Supabase bağlantısı

1. n8n → **Credentials** → **Supabase**
2. Host: `SUPABASE_URL` (ör. `http://127.0.0.1:54321` veya `https://xxx.supabase.co`)
3. Service Role Key: `SUPABASE_SERVICE_ROLE_KEY`

Her workflow'a **Supabase** node ekle:
- **Insert** → ilgili tablo
- **Select** → Recall için `months_since_visit` sorgusu

---

## Tablolar

| Tablo | Açıklama |
|-------|----------|
| `clinics` | Klinik / lokasyon |
| `patients` | Hasta + İYS izni |
| `appointments` | HBYS randevular |
| `nps_responses` | Modül 1 NPS |
| `google_reviews` | Modül 3 yorumlar |
| `inbox_messages` | Modül 2 mesajlar |
| `enps_responses` | Modül 4 çalışan |
| `reputation_mentions` | Sentinel |
| `recall_campaigns` | Recall |
| `automation_events` | Tüm workflow log |

---

## Pilot veri

Migration otomatik ekler:
- **MediDent İstanbul Kartal** (`slug: medident-kartal`)

Test hasta ekle:

```sql
INSERT INTO patients (clinic_id, full_name, phone, iys_consent)
SELECT id, 'Ayşe Yılmaz', '+905551234567', true
FROM clinics WHERE slug = 'medident-kartal';
```

---

## n8n + Supabase REST (credential yoksa)

```bash
curl -X POST "$SUPABASE_URL/rest/v1/nps_responses" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"score":9,"flow":"promoter"}'
```
