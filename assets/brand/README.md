# Nefalix marka envanteri

| Dosya | Boyut | Kullanım |
|-------|-------|----------|
| `nefalix-logo.png` | 1024×1024 | Ana kaynak (PNG) |
| `nefalix-logo-512.png` | 512×512 | Sosyal / orta boy |
| `favicon-192.png` | 192×192 | Favicon, Apple touch |
| `favicon-32.png` | 32×32 | Küçük favicon |
| `qr-kartvizit-site.png` | 1200×1200 | **Kartvizit QR** → nefalix.com (logo ortada) |
| `qr-kartvizit-site-plain.png` | 1200×1200 | Aynı link, logosuz (minimal baskı) |
| `qr-kartvizit-whatsapp.png` | 1200×1200 | WhatsApp sohbet |
| `qr-kartvizit-demo.png` | 1200×1200 | Cal.com demo randevu |

**QR yeniden üret:** `python3 execution/generate-brand-qr.py --preset site`

**Canlı yollar:** `/assets/brand/nefalix-logo.png` (eski `/nefalixai-logo.png` → 301)

**Web:** `partials/site-nav.html` + footer `logo-lockup`  
**Dashboard:** `dashboard.html`, `login.html`, `setup-password.html`

Güncelleme: 2026-07-07
