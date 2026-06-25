# Şikayetvar Senkronu (İtibar / Sentinel)

## Hedef
Kliniklerin Şikayetvar marka sayfasını periyodik tarayıp **yeni şikayetleri** wf-04 Sentinel'e iletmek. AI duygu analizi ve `reputation_mentions` kaydı Sentinel tarafında yapılır.

## Araçlar

| Araç | Rol |
|------|-----|
| `execution/sync-sikayetvar.py` | CLI / VPS cron senkronu |
| `workflows/nefalix-14-sikayetvar-sync.json` | n8n: 4 saatte bir + manuel webhook |
| `workflows/nefalix-04-sentinel-reputation.json` | Mention AI analizi + Supabase |

## Önkoşul

1. Migration:
   ```bash
   npx supabase migration up
   # VPS: cd /opt/nefalix && npx supabase migration up
   ```

2. Klinik kaydında `sikayetvar_url` dolu olmalı:
   ```sql
   UPDATE clinics SET sikayetvar_url = 'https://www.sikayetvar.com/ozel-medident-agiz-ve-dis-sagligi-poliklinigi'
   WHERE id = '51738ea8-c12e-40ce-a0e2-42869496d76b';
   ```
   MediDent seed migration'da zaten var.

3. n8n env: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `WEBHOOK_URL`

## Çalıştırma

**n8n manuel webhook:**
```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/sikayetvar/sync
```

**Tek klinik:**
```bash
curl -X POST https://api.nefalixai.com/webhook/nefalix/sikayetvar/sync \
  -H 'Content-Type: application/json' \
  -d '{"clinic_id":"51738ea8-c12e-40ce-a0e2-42869496d76b"}'
```

**CLI (dry-run):**
```bash
python3 execution/sync-sikayetvar.py --dry-run
python3 execution/sync-sikayetvar.py --clinic-id 51738ea8-c12e-40ce-a0e2-42869496d76b
```

**VPS cron yedek (n8n dışı):**
```cron
15 */4 * * * cd /opt/nefalix && set -a && source .env && python3 execution/sync-sikayetvar.py >> /var/log/nefalix-sikayetvar-sync.log 2>&1
```

## Akış

```
wf-14 (4h cron / webhook)
  → clinics.sikayetvar_url marka sayfası HTML parse
  → dedup: reputation_mentions.external_id veya url
  → yeni şikayet → POST /webhook/nefalix/sentinel/mention
wf-04 Sentinel
  → Vertex AI duygu analizi
  → reputation_mentions (source=sikayetvar, external_id=complaintId)
  → alert_urgent ise WhatsApp gateway (rate limit)
```

## KVKK

- Yalnızca **public** şikayet başlığı, kısa özet ve URL işlenir
- Şikayet sahibi adı/telefonu çekilmez veya saklanmaz
- İstek arası gecikme: `SIKAYETVAR_REQUEST_DELAY_SEC` (default 2s)

## Yeni klinik

`clinics` tablosuna `sikayetvar_url` ekle (tam marka profil URL'si).

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| `sikayetvar_url olan klinik yok` | DB'de URL güncelle |
| VPS'ten 403 | Otomatik `r.jina.ai` proxy; veya `SIKAYETVAR_USE_JINA=1` |
| Aynı şikayet tekrar | `external_id` + `automation_events` dedup |
| Sentinel AI hata (model yok) | wf-04 `VERTEX_GEMINI_MODEL=gemini-2.5-flash` + import |
| Şikayet listesi boş | Marka slug / jina parse; HTML yapısı değişmiş olabilir |
| wf-04 eski (platform okumuyor) | `import-workflows.py` tekrar çalıştır |

## Self-anneal notları

- Şikayetvar resmi public API yok — HTML/RSC payload parse (2026-06)
- VPS/datacenter IP 403 → `https://r.jina.ai/{url}` fallback (jina reader proxy)
- Marka sayfası Next.js RSC; `complaintId` + `title` + `href` regex ile çıkarılır
- Detay sayfasında tam metin kısmen kesik olabilir; başlık + özet Sentinel için yeterli
