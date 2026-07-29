# Stage 04 — Randevu

**Status:** done  
**PNG total:** 26  
**Sample read:** 25/25 (script sample; 1 PNG not in sample list)  
**Tarih:** 2026-07-28

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 12.16.41–.46 | `/appointment-new` | **Yeni Randevu** — danışan ara → seçim sonrası form |
| 12.16.52–.17.32 | `/appointment/calendar/general` | **Genel Takvim** (ay/hafta/gün/ajanda) + filtreler + modal |
| 12.17.38 | aynı + modal | Takvimden **Yeni Randevu** hızlı modal |
| 12.17.43–.56 | `/appointment` | **Randevular** liste + KPI kartlar |
| 12.18.02–.03 | `/calendarEvent` | **Etkinlikler** (blokaj / izin / özel) |

## Bulgular

### Yeni Randevu (`/appointment-new`)
1. Önce **Danışan Ara** typeahead (zorunlu).  
2. Seçim sonrası sekmeler: Danışan Bilgileri · Randevular · Ödemeler · Teklifler · Etiketler · Seçimi Temizle.  
3. Alanlar: Oda, Personel (+ ekle), hizmet rozeti, Tarih, süre (dk), manuel saat (Evet → başlangıç/bitiş), Durum, Tip, Notlar.  
4. Toggle: anket gönderme · video görüşmesi.  
Butonlar: Vazgeç · Kaydet. Alternatif: Detaylı Oluştur · Etkinliğe Dönüştür (takvim modal).

### Genel Takvim (`/appointment/calendar/general`)
- Takvim tipi dropdown: Genel · Personel · Personel (Dikey) · Oda · Oda (Dikey).  
- Görünüm: Ay / Hafta / Gün / Ajanda (+ Takvim Gösterim Tipi: Aylık/Haftalık/Günlük/Ajanda).  
- **Renk kaynağı:** Durum · Personel · Hizmet · Hizmet grubu.  
- Filtre: Randevu Durum · Oda · Personel.  
- **Durum değerleri:** Beklemede · Ertelendi · Geldi/İşlem Yaptırmadı · Gelmedi · İptal · Tamamlandı.  
- **Oda örnekleri:** DENTALZONE/MJA — Kontrol, Op Odası, Prova/Geçici, Yeni Muayene.  
- Personel: Abdülkadir · Enes · Kuays.  
- İşlemler: Yeni Randevu · Yeni Etkinlik · Randevu Listesi.  
- Legend: İlk Randevu · Bakiyesi Olan · Online · İptal · Doğum Günü.  
- Randevu tık → detay modal (durum dropdown, Hızlı Düzenle, İşlemler: Düzenle · Danışan sayfası · Ödeme oluştur · Yeni Teklif · İşlem Kartı · Sil).  
- Düzenle formu: oda/personel/hizmet/tarih/süre/saat/durum/tip/notlar + anket/video toggle.

### Randevular listesi (`/appointment`)
Kolonlar: Tarih, Saat, Danışan, Personel, Tip, Oda, Hizmetler, Durum (inline), İşlem Kartı, dosya ikonu, İşlemler.  
Filtre zengin: Danışan, Oda, Durum, Tip, Hizmet, Personel, Segment, İlk randevu, Referans, Satış temsilcisi, … + **Aramayı kaydet**.  
Sms / E-Posta toplu.  
Alt KPI (ör. 2026 yılı ~90 kayıt): Bekleyen 9 · İptal 3 · Tamamlanan 78 · İstatistik (toplam saat ~82 · tekil danışan 68).

### Etkinlikler (`/calendarEvent`)
Personel/oda blokları (izin, bayram, serbest açıklama). Filtre: Danışan, Oda, Personel, Sadece Yıllık İzin, Tarih. Sil/düzenle.

## Canlı doğrulama (Stella UI)

| Adım | Sonuç |
|------|--------|
| `/appointment-new` | **OK** — `Stella - Yeni Randevu` |
| `/appointment/calendar/general` | **OK** — title `Estesoft Stella`, URL doğru |
| Yeni kayıt / silme | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Takvim: ay/hafta/gün/ajanda + oda/personel dikey | `RandevuTakvim` — görünüm KISMİ; oda/personel takvim **YOK** | **P0** |
| Durum renkleri + Renk kaynağı (durum/personel/hizmet) | Durum var; renk kaynağı seçimi **YOK** | **P0** |
| Oda + hizmet + randevu tipi + süre/manuel saat | `YeniRandevu` — oda/tip/süre KISMİ | **P0** |
| Randevu modal → ödeme / teklif / işlem kartı / danışan | Aksiyon menüsü KISMİ | P0/P1 |
| Liste KPI (bekleyen/iptal/tamamlanan/saat) | `RandevuListe` — KPI **YOK** | **P0** |
| Etkinlik / yıllık izin blokajı | **YOK** | P1 |
| Aramayı kaydet | **YOK** | P2 |
| Anket gönderme / video randevu toggle | **YOK** | P2 |
