# Agent orchestrator — koordinatör + işçi

## Rol ayrımı

| Rol | Kim | Ne yapar | Ne yapmaz |
|-----|-----|----------|-----------|
| **Koordinatör** (bu sohbet / parent) | Sen | Plan, state, sıradaki parça, `Task` ile işçi başlat, sonucu birleştir, kullanıcıya özet | 390 PNG okuma, uzun crawl, ağır implementasyon |
| **İşçi** (subagent / cloud) | `Task` | Tek aşama: oku → yaz → `--complete N` | Sonraki aşamayı kendi başlatmaz (hook/koordinatör yapar) |

State kaynağı gerçeği: `.tmp/stella-crawl-state.json` (veya ileride başka `*-state.json`).

## Stella ekran crawl (örnek boru)

```
Kullanıcı: "crawl devam"
    → Koordinatör: lock aç + python3 execution/emit-stella-worker-brief.py
    → Task(worker) tek aşama
    → İşçi bitince hook subagentStop → followup
    → Koordinatör sonraki Task … pending kalmayana / kullanıcı “dur” diyene
```

Komutlar:

```bash
# Orchestrator açık (hook zinciri aktif)
touch .tmp/stella-crawl-orchestrator.lock

# Sıradaki işçi prompt’unu bas
python3 execution/emit-stella-worker-brief.py

# Durdur
rm -f .tmp/stella-crawl-orchestrator.lock
```

SOP ekranlar: `directives/stella_screenshot_crawl.md`  
Rule: `.cursor/rules/coordinator-staged-work.mdc`  
Hook: `.cursor/hooks.json` → `subagentStop`

## Genel kalıp (başka büyük işler)

1. **State dosyası** — aşama listesi + status (`pending` / `in_progress` / `done`)
2. **Emit brief** — bir sonraki aşama için kopyala-yapıştır `Task` prompt
3. **Koordinatör rule** — “ben parçalamam, işçiye veririm”
4. **Hook** — `subagentStop` + `followup_message` + `loop_limit`
5. **Lock** — istemeden sonsuz döngü olmasın; kullanıcı başlatır/durdurur

Cloud: `environment: cloud` ile aynı brief; binary VPS/LFS’ten çekilir (gap map’te yazıldığı gibi).

## Cursor Browser (Stella panel tıkla-doğrula)

Stella canlı UI için **harici MCP gerekmez** — Cursor’un yerleşik `cursor-ide-browser` sunucusu kullanılır (`mcp.json`’a eklenmez).

### Bir kez (UI)

1. **Cursor Settings** → **Tools & MCP** → **Browser Automation** (veya **Connect to Browser**) → **Browser Tab** (Off değil).
2. **Cursor Settings** → **Agents** → **MCP Tools Protection** → **kapalı** (browser tool’ları sessizce engellenmesin).
3. İsteğe bağlı: **Auto-Run** → **Run Everything** veya browser tool’ları allowlist’te.
4. **Developer: Reload Window** (`Cmd+Shift+P`) veya Cursor yeniden başlat.
5. Yeni Agent sohbeti aç (eski sohbet MCP listesini cache’leyebilir).

### Doğrulama

Agent sohbetinde MCP listesinde `cursor-ide-browser` **ready** olmalı; tool’lar: `browser_navigate`, `browser_snapshot`, `browser_click`, …

Stella: `https://medidentistanbul.stellamedi.com` — şifreleri dosyaya yazma; panel girişi kullanıcı veya mevcut oturum.

### n8n MCP (ayrı konu)

`~/.cursor/mcp.json` içindeki HTTP URL (`…/mcp-server/http`) bu instance’ta **404** döner → `user-n8n` error normal.

Workflow MCP için repodaki stdio kurulum: `cp .cursor/mcp.json.example .cursor/mcp.json` + n8n Cloud API key (`docs/SETUP.md`). Global `mcp.json` ile çakışmaması için ya global’i düzelt ya da sadece proje `mcp.json` kullan.
