# Saha CRM — Takvim randevu + Klinik kartı

Kaynak: canlı `https://nefalix.com/saha` → `crm.html`  
Hedef repo: **nefalix-landing** (bu cloud ortamında private repo erişimi yoktu; patch burada).

## Değişiklikler

| Alan | İyileştirme |
|------|-------------|
| Takvim saatleri | Randevu varsa yeşil blokta klinik + kim görüşecek; tık → detay |
| Takvim gün mini | Randevu satırına tık → detay |
| Randevu detayı | Klinik linki, katılımcılar, oluşturan, durum, not |
| Klinik adı | Kokpit / Dinamik / Arama / Havuz / Randevular / Notlar → kart |
| Klinik kartı | Sol panel: Detaylar, Düzenle, Görüşmeler, Randevular, Notlar |
| Düzenleme | Yalnızca `abdulkadir` (`ak`) ve `enes` (`en`) |
| Dinamik Arama | `hatirlatma` / `segmentAta` **dokunulmadı** |

## Uygulama

```bash
cd /Users/enesceylan/nefalix-landing
# A) doğrudan kopya
cp /path/to/patches/nefalix-landing/crm.html ./crm.html

# B) veya patch
patch -p1 < /path/to/patches/nefalix-landing/crm-takvim-klinik-kart.patch
```

**Deploy:** onay sonrası `vercel --prod` (otomatik deploy etme).
