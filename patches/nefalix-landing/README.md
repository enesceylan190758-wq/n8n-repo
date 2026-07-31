# Saha CRM — Takvim + Klinik kartı (tam sekmeler)

Hedef: `nefalix-landing/crm.html` → `https://nefalix.com/saha`

## Takvim
- Randevu olan günlerde yeşil rozet: `saat + klinik adı` (Stellamedi tarzı; kişi yerine klinik)
- Rozaete / saate tık → randevu detayı (kim görüşecek, durum, klinik linki)
- Klinik adına tık → klinik kartı

## Klinik kartı — sol sekmeler (hepsi çalışır)
| Sekme | İçerik |
|-------|--------|
| Detaylar | Tüm kurum / adres / CRM alanları |
| Düzenle | Form (yalnızca abdulkadir + enes); `hatirlatma` dokunulmaz |
| İlgili kişiler | Liste + ekle/sil |
| Görüşmeler | Form + geçmiş (`segmentAta` ile Dinamik Arama uyumlu) |
| Teklifler | Liste + Yeni teklif formu |
| Sözleşme | Boş durum / kayıt formu |
| Notlar | Not kaydet + geçmiş |
| Dosyalar | Meta kayıt (ad/boyut) |
| Aktivite | Görüşme + randevu + teklif + ödeme birleşik |
| Tahsilat | Toplam / açık bakiye + ödeme ekle |
| Randevular | Klinik randevu listesi |

## Uygulama
```bash
cd /Users/enesceylan/nefalix-landing
cp /path/to/patches/nefalix-landing/crm.html ./crm.html
# Deploy: onay sonrası vercel --prod
```

## 2026-07-28 ek
- Segment: **Gün İçinde Aranacak** (`gun1`, 1 gün) → atanınca Dinamik Arama **Bugün** listesinde
- Görüşme notlarında **Notu düzenle** (kayıt sonrası + geçmiş + Görüşme Notları sayfası)

## 2026-07-29 ek
- Geçmiş görüşme notlarında **sekme/segment her zaman seçilebilir**; Kaydet ile not + (isteğe bağlı) klinik aşaması / `hatirlatma` güncellenir

## 2026-07-30 ek
- **Manuel hatırlatma / dönüş tarihi**: Bugün, +1…+5, +7 gün kısayolları + tarih seçici
- Yerler: Görüşme sonucu, klinik kartı Detaylar, Görüşmeler formu, Dinamik Arama → Hatırlatma
- Tarih seçilince klinik `hatirlatma` alanına yazılır → Dinamik Arama listesine düşer
