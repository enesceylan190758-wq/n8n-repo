# Vertex AI / Gemini Geçişi (GCP Kredisi)

OpenAI **ayrı** faturalandırma. GCP Free Trial kredisi (**₺13.769,97**, 2026-09-21) yalnızca **Google Cloud** hizmetlerinden düşer — **Vertex AI** dahil.

## Güncel durum (2026-06-24)

- VPS/n8n aktif proje: `utility-cumulus-484107-v3`
- Service account: `nefalixai@utility-cumulus-484107-v3.iam.gserviceaccount.com`
- Model: `gemini-2.5-flash`
- Bölge: `europe-west1`
- Vertex `generateContent` smoke test başarılı.
- Kredi ekranındaki Free Trial aynı proje/billing hesabına bağlıysa Vertex harcaması kredi bakiyesinden düşer; farklı Google hesabındaki ayrı billing hesabına bağlıysa proje billing linki o hesaba taşınmalı veya yeni service account ile proje değiştirilmelidir.

## Hedef

| Önce | Sonra |
|------|--------|
| `@n8n/.../lmChatOpenAi` (gpt-4o-mini) | `@n8n/.../lmChatGoogleVertex` (gemini-1.5-flash) |
| `OPENAI_API_KEY` | GCP service account + `GCP_PROJECT_ID` |
| wf-10 OpenAI REST | Vertex `generateContent` + `GCP_ACCESS_TOKEN` |

## Kurulum (tek sefer)

### 1. GCP Console

1. [Vertex AI API](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com) etkinleştir (proje: `project-860dace6-d98e-44e1-994`).
2. **IAM → Service Accounts → Create** → rol: **Vertex AI User**.
3. JSON key indir → repoda **commit etme**: `.tmp/gcp-service-account.json`
4. Bölge: `europe-west1` (İstanbul’a yakın latency).

### 2. Ortam değişkenleri (`.env`)

```bash
GCP_PROJECT_ID=project-860dace6-d98e-44e1-994
GCP_REGION=europe-west1
VERTEX_GEMINI_MODEL=gemini-1.5-flash
GOOGLE_APPLICATION_CREDENTIALS=.tmp/gcp-service-account.json
```

### 3. Tek komut kurulum (VPS)

```bash
# JSON yüklendikten sonra VPS'te:
cd /opt/nefalix && bash execution/setup-vertex-pilot.sh
```

Script sırasıyla: `.env` GCP alanları → token → n8n credential → docker → workflow import → Vertex test → saatlik cron.

### 3b. Manuel adımlar

### 4. Token yenileme (wf-10 code node)

`GCP_ACCESS_TOKEN` ~1 saat geçerli. VPS cron:

```cron
0 * * * * cd /opt/nefalix && WRITE_GCP_TOKEN_TO_ENV=1 python3 execution/refresh-gcp-access-token.py && docker compose up -d n8n
```

## Workflow listesi

| Workflow | AI kullanımı |
|----------|----------------|
| wf-01 NPS mesajı | Vertex agent |
| wf-02 Google review agent | Vertex agent |
| wf-04 Sentinel | Vertex agent |
| wf-05 Recall | Vertex agent |
| wf-06 Inbox taslak | Vertex agent |
| wf-10 Google taslak cron | Vertex REST (code node) |

## Vertex Prompt Designer faydası

[Vertex AI Prompt Designer](https://console.cloud.google.com/vertex-ai/studio) walkthrough:

- NPS / inbox / yorum promptlarını **canlı test** (maliyet düşük: flash model).
- **System instruction** + örnek hasta mesajları ile A/B.
- **JSON çıktı şeması** (sentiment, draftReply) — wf-02/10 ile uyumlu.
- Prompt versiyonlarını kaydet → `execution/nefalix_prompts.py` ile senkron.
- **Grounding** (ileride): klinik SSS PDF → RAG — WhatsApp bot daha doğru yanıt.
- Tüm kullanım **GCP kredisinden** düşer; OpenAI hesabı kapatılabilir.

## Geri alma

```bash
git checkout workflows/  # OpenAI JSON
export N8N_OPENAI_CRED_ID=...
python3 execution/import-workflows.py
```

## Edge case

- `gemini-1.5-flash` bölgede yoksa → `gemini-2.0-flash` veya `gemini-2.5-flash` dene (`VERTEX_GEMINI_MODEL`).
- 403 Vertex → API enable + service account rolü kontrol.
- Boş AI yanıt → safety filter; prompt'ta teşhis iddiası azalt.
