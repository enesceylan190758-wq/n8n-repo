# Stack Başlatma

## Hedef
Yerel Nefalix pilot ortamını çalışır hale getir: Docker n8n + Supabase.

## Önkoşul
- Docker Desktop yüklü ve açık
- Node/npx (Supabase CLI için)

## Adımlar

1. Docker'ı aç:
   ```bash
   open -a Docker
   ```

2. n8n stack:
   ```bash
   cd ~/n8n-repo
   docker compose up -d
   ```

3. Supabase local:
   ```bash
   npx supabase start
   ```

4. Doğrula:
   - n8n UI: http://localhost:5678
   - Supabase Studio: http://127.0.0.1:54323
   - Kong API: http://127.0.0.1:54321

## Edge Cases

| Sorun | Çözüm |
|-------|--------|
| n8n Supabase credential "Invalid URL" | URL: `http://host.docker.internal:54321` (127.0.0.1 değil) |
| Supabase port meşgul | `npx supabase stop` sonra tekrar start |
| Docker kapalı | Tüm workflow + chat durur |

## Çıktı
- `nefalix-n8n` container healthy
- `supabase_kong` healthy
