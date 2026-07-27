# Stella Discovery Assets — konumlar

**Amaç:** PC’deki Stella ekran görüntüleri / Excel / Onat ses kaydını agent’ın kalıcı erişebileceği yerde tutmak.  
**Not:** ~200MB binary; Git LFS yok → **VPS** kaynak gerçek. Bu dosya yalnızca path + envanter (git’te).

## Kaynak (PC)

- `~/Downloads/nefalix crm/`
- `~/Downloads/Onat Sk..m4a`

## Local (workspace, gitignore `.tmp/`)

```
/Users/enesceylan/n8n-repo/.tmp/stella-discovery/
  MANIFEST.json
  README.md
  Onat-Sk.m4a
  nefalix-crm/          # 415 dosya (390 png + 4 xlsx + klasör içerikleri)
  nefalix crm/          # eski kısmi kopya (varsa ignore; asıl = nefalix-crm)
```

Zip: `.tmp/stella-discovery-2026-07-27.zip` (~224MB)

## VPS (kalıcı / bulut)

Host: `root@93.127.186.45`

```
/opt/nefalix/.tmp/stella-discovery-2026-07-27.zip
/opt/nefalix/.tmp/stella-discovery/
  MANIFEST.json
  README.md
  Onat-Sk.m4a
  nefalix-crm/
```

Doğrulama:

```bash
ssh root@93.127.186.45 'find /opt/nefalix/.tmp/stella-discovery -type f | wc -l; du -sh /opt/nefalix/.tmp/stella-discovery'
```

## Envanter (MANIFEST)

| Tür | Adet |
|-----|------|
| PNG (ekran) | 390 |
| XLSX | 4 |
| M4A (Onat) | 1 |
| Diğer / isimsiz | ~21 |

### Excel dosyaları

- `Danisan Bakiyeleri Raporu.xlsx`
- `Danisan Listesi (8).xlsx`
- `Dinamik Arama.xlsx`
- `Kasa Raporu.xlsx`

### Ekran klasörleri (`nefalix-crm/`)

- ana ekran özetler paneller
- crm içindeki dinamik arama listesinde hasta ismine tıklanınca çıkan hasta kartı içerikleri
- crm sekmesi içerikleri
- danışan sekmesi içerikleri
- destek sekmesi
- ev işareti sekmesi
- gelirler sekmesi
- giderler sekmesi
- randevu sekmesi
- rapor sekmesi
- sistem sekmesi
- whatsapp sekmesi

## Git politikası (Mac → cloud)

- Binary paket **Git LFS** ile: `discovery/stella-discovery-2026-07-27.zip` (bkz. `discovery/README.md`).
- Path dokümanı + gap/action MD normal git’te.
- VPS kopyası yedek: `scp` → `/opt/nefalix/.tmp/stella-discovery/`
- Yeniden sync: `rsync` Downloads → `.tmp/stella-discovery/nefalix-crm/` → zip → `discovery/` + LFS push + (opsiyonel) VPS scp.

## Durum (2026-07-27 doğrulandı)

- [x] Local sync: `.tmp/stella-discovery/` (390 PNG + 4 XLSX + Onat-Sk.m4a; `.DS_Store` hariç içerik = VPS)
- [x] VPS: `/opt/nefalix/.tmp/stella-discovery/` — **397 dosya**, 205MB; zip **171MB**
- [x] Path dokümanı git’te (`docs/stella_discovery_assets.md`)
- [ ] LFS zip: `discovery/stella-discovery-2026-07-27.zip` (Mac push bekleniyor)
- [ ] Gap/action çıkarımı (adım 2 — cloud’da LFS pull sonrası)
