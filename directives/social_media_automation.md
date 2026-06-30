# Sosyal Medya Otomasyonu (Instagram — manuel yükleme)

> Sistem üretir → Drive'a koyar → sen Instagram planlayıcıdan yüklersin.

## Akış

```
Pazartesi 09:00 (wf-17 cron)
    ↓
GPT görsel + caption üret
    ↓
Google Drive klasörüne paket yükle
  (yedek: /opt/nefalix/.tmp/social-ready/)
    ↓
Sen: Drive'dan indir → Instagram planlayıcı → zamanla → yayınla
```

**Yok:** WhatsApp, Meta API, onay adımı, otomatik Instagram paylaşımı.

## Paket içeriği

Her post için bir klasör:

```
2026-06-29_post_01_post_01_brand_hero/
  ├── image.png      ← Instagram'a yükle
  └── caption.txt    ← kopyala-yapıştır (caption + hashtag)
```

## Kurulum

### 1. Migration

```bash
supabase db push
```

### 2. Google Drive (5 dk)

1. [Google Drive](https://drive.google.com) → yeni klasör: **Nefalix Sosyal Medya**
2. Klasörü paylaş → service account e-postası (`.tmp/gcp-service-account.json` içindeki `client_email`) → **Düzenleyici**
3. Klasör URL'sinden ID al: `https://drive.google.com/drive/folders/BURASI_ID`

```bash
# .env
SOCIAL_DRIVE_FOLDER_ID=1abc...xyz
GOOGLE_APPLICATION_CREDENTIALS=.tmp/gcp-service-account.json
OPENAI_API_KEY=sk-...
```

4. [Google Cloud Console](https://console.cloud.google.com) → API'ler → **Google Drive API** etkinleştir (aynı GCP projesi)

### 3. Drive olmadan (en basit)

`SOCIAL_DRIVE_FOLDER_ID` boş bırak → dosyalar sadece VPS'te:

```
/opt/nefalix/.tmp/social-ready/2026-06-29_post_01_.../
```

Mac'te Google Drive masaüstü uygulaması bu klasörü sync edebilir veya `scp` ile çekersin.

### 4. Workflow

```bash
python3 execution/import-workflows.py
```

## Komutlar

```bash
# Sonraki postu üret + Drive'a yükle
python3 execution/social-generate-next.py

# Belirli post
python3 execution/social-generate-next.py --slug post_03_promoter_rule

# Webhook (canlı)
curl -X POST https://api.nefalixai.com/webhook/nefalix/social/generate -d '{}'
```

## Env

| Değişken | Zorunlu | Açıklama |
|----------|---------|----------|
| `OPENAI_API_KEY` | Evet | GPT görsel |
| `SUPABASE_*` | Evet | Kuyruk |
| `SOCIAL_DRIVE_FOLDER_ID` | Hayır | Drive hedef klasör |
| `GOOGLE_APPLICATION_CREDENTIALS` | Drive için | GCP service account JSON |
| `SOCIAL_IMAGE_PROVIDER` | Hayır | `openai` (varsayılan) |

## Instagram planlayıcı (senin işin)

1. Drive'dan `image.png` indir
2. Instagram uygulaması → Profesyonel panel → Planlanmış içerikler
3. Görseli yükle, `caption.txt` içeriğini yapıştır
4. Tarih/saat seç → Planla

~2 dakika/post.

## Edge cases

| Sorun | Çözüm |
|-------|--------|
| Drive 403 | Klasörü service account mailine paylaş |
| Drive API kapalı | GCP Console → Drive API enable |
| PyJWT yok | `pip install PyJWT cryptography` |
| OpenAI fail | Otomatik HTML şablon fallback |

## İletişim (postlarda)

- Mail: `nefalixai@gmail.com`
- Tel: yok
