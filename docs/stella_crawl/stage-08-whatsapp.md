# Stage 08 — WhatsApp (Stella)

**Status:** done  
**PNG total:** 17  
**Sample read:** 17/17  
**Tarih:** 2026-07-28

## WHATSAPP menü (dropdown)

1. Whatsapp Yönetim Paneli · 2. Whatsapp Raporları · 3. Meta Yönetim Paneli

(Üst bar WhatsApp ikonu → `/sirius/messages` inbox — stage-06.)

## Dosya → URL haritası

| Dosya (kısa) | URL | Ekran |
|--------------|-----|--------|
| 12.32.12 | `/integrations/whatsappManagementPanel` | **Whatsapp hesapları** (boş tablo) |
| 12.32.14–.16 | `?tab=templates` | **Template mesajlar** (boş) |
| 12.32.17, .34 | `?tab=sendingpreferences` | **Template Tercihleri** — randevu hatırlatma toggle + yurt içi/dışı template |
| 12.32.19, .27–.29 | `?tab=autoresponders` | **Otomatik yanıtlayıcılar** (WA/IG/Messenger; boş) |
| 12.32.20, .24 | `?tab=autoassign` | **Otomatik atama kuralları** + Yeni kural |
| 12.32.22 | `?tab=settings` | **Ayarlar** — medya kaydet toggles; otomatik atama sonrası danışan oluştur |
| 12.32.40, .43, .48 | `/reporting/whatsappReports` | **Chat Analiz** + **Silinen Mesajlar** raporları |
| 12.32.54–.58 | `/integrations/metaManagementPanel` | **Meta Yönetim Paneli** — otomatik yanıtlayıcılar |

## Bulgular

### Whatsapp Yönetim Paneli (`/integrations/whatsappManagementPanel`)
Alt sekmeler: **Whatsapp hesapları** · Template mesajlar · WhatsApp Template Tercihleri · Otomatik yanıtlayıcılar · Whatsapp otomatik atama kuralları · Ayarlar.

**Hesaplar:** Kolonlar Ad · Telefon · Sağlayıcı · Varsayılan sender mı? · Durum · İşlemler. **+ Hesap Ekle**. Örnek klinikte hesap yok.

**Template mesajlar:** Arama kriterleri · **Templateleri Güncelle** · İşlemler. Örnek boş.

**Template Tercihleri:** Bilgi kutusu — randevu hatırlatması için “Randevu Hatırlatma Şablonu” gerekli.  
Toggle **Randevu Hatırlatması Gönder** (OFF→ON örnekleri). **Yurt İçi Template** · **Yurt Dışı Template** (Template Seç). Kaydet.

**Otomatik yanıtlayıcılar:** WA + Instagram + Messenger. Varsayılan yanıtlayıcı (boş ifade) · tam eşleşme kuralı. **Yeni Whatsapp otomatik yanıt**. Filtre: Gelen mesajda… Örnek boş.

**Otomatik atama kuralları:** **Yeni Whatsapp otomatik atama kuralı**. Örnek boş.

**Ayarlar:** Gelen/giden medyayı otomatik kaydet (OFF) · **Otomatik Atama Sonrası Danışan Oluştur** (ON). Kaydet.

### Whatsapp Raporları (`/reporting/whatsappReports`)
Sekmeler: **Chat Analiz Raporu** · **Silinen Mesajlar Raporu**.  
Filtre: Tarih aralığı / Silinme tarih aralığı · Aramayı kaydet · İşlemler → **Excel İndir**. Örnek aralıklarda kayıt yok.

### Meta Yönetim Paneli (`/integrations/metaManagementPanel`)
Meta (∞) markalı panel; **Otomatik yanıtlayıcılar** (cross-channel). **Yeni Meta otomatik yanıt**. Örnek boş.

## Canlı doğrulama (Cursor browser MCP)

| URL | Sonuç |
|-----|--------|
| `/home/index` | **OK** — oturum Enes Ceylan |
| `/integrations/whatsappManagementPanel` | **OK** — 6 alt sekme (hesaplar, template, tercihler, autoresponder, autoassign, ayarlar) |
| `/reporting/whatsappReports` | **OK** — Chat Analiz + Silinen Mesajlar sekmeleri |
| `/integrations/metaManagementPanel` | **OK** — Meta Yönetim Paneli yüklendi |
| Kayıt oluşturma | **Yapılmadı** |

## Gap delta → Nefalix

| Stella | Nefalix | Öncelik |
|--------|---------|---------|
| WA hesap bağlama (sağlayıcı, varsayılan sender) | Evolution/Chatwoot pilot — Stella panel **YOK** | **P0** |
| Template mesaj + Meta sync + randevu hatırlatma (içi/dışı) | İYS/template stub | **P0** |
| Otomatik yanıtlayıcı + atama kuralları + danışan auto-create | WhatsAppPanel **KISMİ** | **P0** |
| Chat analiz + silinen mesaj raporu + Excel | **YOK** | P1 |
| Meta IG/Messenger autoresponder | **YOK** | P2 |
| Sirius inbox (`/sirius/messages`) | Üst ikon mesaj kutusu | P1 |
