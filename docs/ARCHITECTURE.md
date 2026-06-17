# Nefalix Mimari: Workflow vs Supabase

## Kısa cevap

| Katman | Nasıl? | Neden? |
|--------|--------|--------|
| **n8n workflow'ları** | Ayrı ayrı (6 modül) | Bakım, hata izolasyonu, bağımsız aç/kapa |
| **Veri** | Tek yer → **Supabase** | Tüm modüller aynı DB'ye yazar/okur |
| **Dashboard (ileride)** | Supabase + SaaS UI | Tek ekranda her şey |

**Hepsini tek dev workflow'a toplama** — önerilmez. 500+ satırlık monolith workflow debug edilemez, bir hata hepsini durdurur.

---

## Önerilen yapı

```
                    ┌─────────────────┐
   HBYS / WhatsApp  │  n8n Workflow'lar │  (ayrı, modüler)
   Google / Web      │  01 Feedback      │
        │            │  02 Google AI     │
        └──────────► │  03 eNPS          │
                     │  04 Sentinel      │
                     │  05 Recall        │
                     │  06 Inbox         │
                     │  + Web Chatbot    │
                     └────────┬────────┘
                              │ yaz/oku
                              ▼
                     ┌─────────────────┐
                     │    SUPABASE     │  ← TEK MERKEZ
                     │  patients       │
                     │  appointments   │
                     │  nps_responses  │
                     │  google_reviews │
                     │  inbox_messages │
                     │  automation_events │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ Dashboard (SaaS) │  Aşama 3
                     └─────────────────┘
```

---

## Workflow'lar neden ayrı?

1. **Farklı tetikleyiciler** — HBYS webhook, cron, chat trigger
2. **Bağımsız pilot** — sadece NPS'i MediDent'e açarsın
3. **Hata izolasyonu** — Recall bozulsa chatbot çalışır
4. **PDF MVP aşamaları** — Aşama 1/2/3 modül modül eklenir

---

## Ortak bağlantı: Supabase

Her workflow kritik adımda Supabase'e kayıt atar:

| Workflow | Tablo |
|----------|-------|
| Feedback Loop | `nps_responses`, `automation_events` |
| Google AI | `google_reviews` |
| Inbox | `inbox_messages` |
| eNPS | `enps_responses` |
| Sentinel | `reputation_mentions` |
| Recall | `recall_campaigns` |

İleride dashboard bu tablolardan okur — workflow sayısı önemli değil.

---

## İsteğe bağlı: Orkestratör workflow

Tek webhook istiyorsan ince bir **router** eklenebilir:

```
HBYS webhook → Router workflow → Execute Workflow (01 Feedback)
```

Router sadece yönlendirir; iş mantığı modül workflow'larında kalır.

---

## Supabase kurulum

Bkz. [SUPABASE.md](./SUPABASE.md)
