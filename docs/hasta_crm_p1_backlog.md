# Hasta CRM P1 Backlog (daily-ops after cutover)

**Goal:** Stella kesimi sonrası günlük kullanım — sahte/eksik panelleri canlı veriye bağla.  
**State:** `.tmp/hasta-crm-p1-state.json`  
**Live:** https://nefalix.com/hasta-crm  
**Kaynak gap:** `docs/Stella_Gap_Action_Map.md` + `docs/stella_crawl/stage-0{1,6,7}.md`

| # | ID | Item | Gap | Durum |
|---|-----|------|-----|-------|
| 1 | p1-01-dashboard-kpi | Ana ekran KPI kartları → canlı (aktif danışan, gün randevu, kasa, ciro farkı) + linkler | #16 / stage-06 | **done** + live |
| 2 | p1-02-lead-filters | Lead listesi: segment + temsilci + ülke filtreleri | #2 / stage-01 | **done** + live |
| 3 | p1-03-gider-kur-cards | Giderler: TRY/EUR özet kartları + yöntem kırılımı | #15 / stage-07 | **done** + live |
| 4 | p1-04-salesline-pack | Salesline kanban pack + menü doğrula (store `salesSegments` zaten var) | stage-01 salesline | **done** + live |
| 5 | p1-05-firma-odeme-stub | Firma listesi/ödeme minimum stub (getFirma boş) | stage-07 firma | **done** + live |

**Deploy batch 1 (2026-07-28):** p1-01…p1-04 → `dpl_8jNSKypcgMBsu7zqwZdHmFBKnbhm`  
**Deploy batch 2 (2026-07-28):** p1-05 + store firma persist → `dpl_6exgkcuGbMz1sofgVZ6WW8UvqYKi` aliased `nefalix.com`  
**Smoke:** login `enes` · Dashboard 600 · Lead filtre · Gider kart · Salesline · Firma `Test Lab P1`

**P1 TOP5 slice:** COMPLETE  

**Sonraki (P1+/P2 öneri):** Son İşlemler audit · Bakiye listesi · Rapor indeks · WA inbox bridge
