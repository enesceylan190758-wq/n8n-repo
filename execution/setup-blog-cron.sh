#!/usr/bin/env bash
# Günlük blog cron — VPS host (Cursor/AI açık olması gerekmez)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARK="# nefalix-daily-blog"
# 09:05 — saatlik GCP token refresh (0 * * * *) bittikten sonra
CRON_LINE="5 9 * * * cd ${ROOT} && set -a && . ./.env && set +a && PYTHONUNBUFFERED=1 /usr/bin/python3 -u execution/publish-daily-blog.py >> /var/log/nefalix-blog.log 2>&1"

# Eski UTC 06:00 satırını temizle
TMP="$(mktemp)"
(crontab -l 2>/dev/null || true) | grep -vF "$MARK" | grep -v "publish-daily-blog.py" >"$TMP" || true
{
  cat "$TMP"
  echo "$MARK"
  echo "CRON_TZ=Europe/Istanbul"
  echo "$CRON_LINE"
} | crontab -
rm -f "$TMP"

touch /var/log/nefalix-blog.log
chmod 644 /var/log/nefalix-blog.log 2>/dev/null || true

# Alıcılar (yoksa ekle)
if ! grep -q "^BLOG_NOTIFY_TO=" "$ROOT/.env" 2>/dev/null; then
  echo "BLOG_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com" >>"$ROOT/.env"
fi

echo "✓ Blog cron: her gün 09:05 Europe/Istanbul"
echo "  Log: /var/log/nefalix-blog.log"
echo "  Mail: info@nefalix.com → BLOG_NOTIFY_TO"
crontab -l | grep -A2 "$MARK" || true
