# Stage 13 — Sistem (3/3) + Destek

**Status:** done  
**PNG total:** 42 (sistem slice 80+ + destek 3)  
**Sample read:** 5/30 (tanımlamalar devam + destek)  
**Tarih:** 2026-07-28

## Destek menü

Kayıtlarım · Yeni Destek Kaydı

## Dosya → URL haritası

| URL | Ekran |
|-----|--------|
| `/helpdesk/index` | **Kayıtlarım** — destek ticket listesi |
| `/helpdesk/new` (muhtemel) | Yeni Destek Kaydı (buton) |
| `/definitions/*` | Diğer tanımlamalar (segment, referans, oda, vb. — PNG devam) |

## Bulgular

### Helpdesk (`/helpdesk/index`)
**Yeni Destek Kaydı** butonu. Sol panel: Tüm Talepler / Sadece Açık · Ara.  
Örnek kayıtlar: yönetici ataması · silinen dosya · telefon numarası kaydı — durum **Cevaplandı**.

### Tanımlamalar (devam)
Banka hesabı formu: Unvan · Referans · IBAN · Swift · Banka adı · Kur · Kaydet.  
Finansal tanımlar Stella gelir/gider/Kasa ile bağlı.

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/helpdesk/index` | PNG doğrulandı |
| `/supportTicket` | Boş shell — `/helpdesk/index` doğru rota |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Helpdesk ticket UI | `Destek` stub | P2 |
| Tam tanımlamalar ağacı (segment/oda/referans) | import-stella-definitions hedef | **P0** |
