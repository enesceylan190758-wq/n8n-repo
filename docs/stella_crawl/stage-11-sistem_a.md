# Stage 11 — Sistem (1/3)

**Status:** done  
**PNG total:** 40  
**Sample read:** 8/25 (ayarlar/personel/api/entegrasyon temsil; kalan alt menü stage-12)  
**Tarih:** 2026-07-28

## SİSTEM menü

Yetki · Ayarlar · Güvenlik Ayarları · Personel · Prim Ayarlamaları · Entegrasyonlar · Api Yönetimi · Hizmet · Paket · Ürün · Tanımlamalar · Toplu Sms Gönderim Onayları

## Dosya → URL haritası

| URL | Ekran |
|-----|--------|
| `/management/generalSettings` | **Genel Ayarlar** (logo/renk/şablon + toggles) |
| `/management/smsSettings` | **Sms Gönderim Tercihleri** (KVKK + dijital izin, IYS metni) |
| `/staff` | **Personeller** listesi |
| `/integrations` | **Entegrasyonlar** kart grid |
| `/integrations/apiIntegration` | **API Entegrasyonu** (+ Swagger v1.1) |

### Ayarlar sol menü (PNG)
Genel · Danışan Kayıt · Tablet Kayıt · Sms · WhatsApp Template · Anket · Form · Puan · Satış · Hedefler

## Bulgular

### Genel Ayarlar
Logo · Renk (#8BA777 ör.) · Şablon (Mint). Toggles: geçmiş randevu auto-tamamla · ödeme→randevu durumu · çakışan randevu izni (ON) · gider onay mekanizması · işlem kartı sıralama. Randevu hatırlatma saati · mesai 09:00–19:00.

### Personel (`/staff`)
Kolonlar: Ad · Yetki grubu · Personel grubu · Son giriş · Sisteme/mobil giriş · Takvimde göster · İşlemler.  
Örnek: Tam Yetkili / Satış Temsilcisi. Paket personel limiti uyarısı (3/3).

### Entegrasyonlar (`/integrations`)
Kartlar: WhatsApp (#messaging, kredi) · E-Posta · Facebook · TikTok · Web Form · Google Calendar · Google Ads · Nes (fatura) · Sonitel (#callcenter) · Ödeme Geçmişi.

### API (`/integrations/apiIntegration`)
Swagger **Estesoft Stella API v1.1** — AccountingApi (List, ListCustomerDebts, PayCustomerDebt) · AppointmentApi/New · …  
**Not:** Canlı ekranda API anahtarı görünür — dokümana yazılmadı.

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/management/generalSettings` | **OK** — Genel Ayarlar form + Kaydet |
| `/staff` | **OK** — yüklendi |
| `/integrations/apiIntegration` | **OK** — API Entegrasyonu / Anahtar Oluştur linki |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| Klinik genel ayarlar (logo, mesai, randevu kuralları) | `Ayarlar` **KISMİ** | **P0** |
| KVKK/İYS SMS şablonları | İYS stub | **P0** |
| Personel + yetki grubu + limit | `Personel` / `Yetki` **KISMİ** | **P0** |
| Entegrasyon marketplace | Evolution/Meta **YOK** (ayrı pilot) | P1 |
| Stella REST API (Accounting/Appointment) | n8n/Supabase hedef | P1 |
