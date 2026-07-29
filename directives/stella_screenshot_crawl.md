# Stella ekran arşivi — aşamalı crawl

## Hedef

390 PNG’yi **parça parça** işle; her aşama bitince state güncelle → bir sonraki aşamaya geç. Tek seferde tüm arşivi okuma.

**Paket:** `.tmp/stella-discovery/nefalix-crm/` (veya LFS zip unzip)  
**State:** `.tmp/stella-crawl-state.json`  
**Çıktı birikimi:** `docs/stella_crawl/` (aşama MD’leri) → özet `docs/Stella_Gap_Action_Map.md`  
**Canlı doğrulama:** `https://medidentistanbul.stellamedi.com` (Estesoft/.env — şifre chat’e yazma)

## Çalıştırma

```bash
# Sonraki bekleyen aşamayı işle (manifest + örnek PNG listesi + state)
python3 execution/stella-screenshot-stage.py

# Belirli aşama
python3 execution/stella-screenshot-stage.py --stage 1

# Aşama bitti işaretle (agent görselleri okuyup MD yazdıktan sonra)
python3 execution/stella-screenshot-stage.py --complete 1
```

**Agent kuralı:** `status=pending` olan en düşük `stage` için:

1. Script’i çalıştır → dosya listesini al  
2. Listedeki PNG’leri Read ile oku (aşama başına max ~25; fazlaysa alt-batch)  
3. `docs/stella_crawl/stage-NN-*.md` yaz (ekran → URL → Nefalix gap → P0/P1)  
4. `--complete N`  
5. Gap map’e 5–10 satırlık delta ekle  
6. Hemen sonraki aşamaya geç (kullanıcı durdurana kadar)

## Aşama sırası (P0 önce)

| # | id | Klasör(ler) | ~PNG | Amaç |
|---|-----|-------------|------|------|
| 1 | `crm_lead` | `crm sekmesi içerikleri` + kök PNG | ~17 | Lead, dinamik arama listesi |
| 2 | `hasta_karti` | hasta kartı klasörü | ~33 | Kart sekmeleri, not/teklif/randevu |
| 3 | `danisan` | `danışan sekmesi içerikleri` | ~22 | Danışan liste/form |
| 4 | `randevu` | `randevu sekmesi` | ~26 | Takvim, durum renkleri |
| 5 | `gelirler` | `gelirler sekmesi` | ~30 | Kasa, satış, bakiye |
| 6 | `ana_ekran` | ana ekran + ev işareti | ~18 | Dashboard paneller |
| 7 | `giderler` | `giderler sekmesi` | ~20 | Gider kayıt |
| 8 | `whatsapp` | `whatsapp sekmesi` | ~17 | Stella WA (Nefalix=Evolution) |
| 9 | `rapor_a` | `rapor sekmesi` (ilk yarı) | ~43 | CRM/finans rapor |
| 10 | `rapor_b` | `rapor sekmesi` (ikinci yarı) | ~42 | devam |
| 11 | `sistem_a` | `sistem sekmesi` (1/3) | ~40 | Yetki, tanım |
| 12 | `sistem_b` | `sistem sekmesi` (2/3) | ~40 | devam |
| 13 | `sistem_c` | `sistem` kalan + `destek` | ~42 | kapanış |

## Stella UI tıkla-doğrula

API ≠ panel. Panel: `ESTESOFT_STELLA_API_BASE` + panel kullanıcı/şifre (`.env` / kullanıcı).

Her P0 aşamasında (1–5) canlıda:

1. İlgili menüye gir  
2. 2–3 kritik tıklama (liste → kart → kaydet alanı)  
3. Sonucu `docs/stella_crawl/stage-NN-*.md` içine **Canlı doğrulama** bölümü olarak yaz  

Şifre/token commit etme.

## Edge

- Klasör adları Unicode (NFC/NFD) — script `Path.iterdir` kullanır, hardcode basename kırılgan olabilir  
- Cloud agent: önce LFS zip veya VPS scp  
- Kullanıcı “dur” derse state’te kal; devam = aynı komut  
