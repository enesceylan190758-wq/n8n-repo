# Nefalix marka envanteri

| Dosya | Boyut | Kullanım |
|-------|-------|----------|
| `nefalix-logo.png` | 1024×1024 | Ana kaynak (PNG) |
| `nefalix-logo-512.png` | 512×512 | Sosyal / kartvizit |
| `favicon-192.png` | 192×192 | Favicon |
| `qr-kartvizit-enes.png` | 1200×1200 | Enes kart → `/k/enes` |
| `qr-kartvizit-abdulkadir.png` | 1200×1200 | Abdülkadir → `/k/abdulkadir` |
| `qr-kartvizit-medident.png` | 1200×1200 | MediDent İstanbul → `/k/medident` |
| `qr-kartvizit-site.png` | 1200×1200 | Site ana sayfa |

**QR yeniden üret:** `python3 execution/generate-brand-qr.py --preset medident`

**Canlı dijital kart:** `directives/kartvizit_qr.md` — Mac deploy: `bash execution/deploy-kartvizit-cards.sh`
