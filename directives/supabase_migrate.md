# Supabase Migration

## Hedef
Şema güncelle, seed ver, n8n clinic_id uyumunu koru.

## Araçlar

**Tüm migration'ları sıfırla (dev):**
```bash
npx supabase db reset
```

**Sadece yeni migration uygula:**
```bash
npx supabase migration up
```

## Kritik: Sabit clinic UUID

MediDent pilot klinik ID **değişmemeli**:
```
51738ea8-c12e-40ce-a0e2-42869496d76b
```

`db reset` sonrası workflow'lardaki hardcoded id ile seed uyumlu olmalı.
Seed: `supabase/migrations/20260618060000_medident_seed.sql`

## db reset sonrası checklist

1. `npx supabase db reset`
2. `python3 execution/import-workflows.py`
3. `bash execution/test-all-workflows.sh`
4. n8n Supabase credential test (host.docker.internal)

## Dashboard anon read

Migration `20260618070000_dashboard_anon_read.sql` — pilot panel `anon` key ile okuyabilir.

## Self-anneal
- **2026-06-18:** Reset sonrası clinic_id değişiyordu → seed'e explicit UUID eklendi → FK hataları çözüldü.
