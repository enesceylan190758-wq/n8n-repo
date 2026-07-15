#!/usr/bin/env bash
# Günlük sosyal medya cron — VPS host (09:30 Europe/Istanbul)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARK="# nefalix-daily-social"
CRON_LINE="30 9 * * * cd ${ROOT} && set -a && . ./.env && set +a && PYTHONUNBUFFERED=1 /usr/bin/python3 -u execution/publish-daily-social.py >> /var/log/nefalix-social.log 2>&1"

TMP="$(mktemp)"
(crontab -l 2>/dev/null || true) | grep -vF "$MARK" | grep -v "publish-daily-social.py" >"$TMP" || true
{
  cat "$TMP"
  echo "$MARK"
  echo "CRON_TZ=Europe/Istanbul"
  echo "$CRON_LINE"
} | crontab -
rm -f "$TMP"

touch /var/log/nefalix-social.log
chmod 644 /var/log/nefalix-social.log 2>/dev/null || true

if ! grep -q "^SOCIAL_NOTIFY_TO=" "$ROOT/.env" 2>/dev/null; then
  echo "SOCIAL_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com" >>"$ROOT/.env"
fi

echo "✓ Sosyal cron: her gün 09:30 Europe/Istanbul"
echo "  Log: /var/log/nefalix-social.log"
echo "  Onay maili: SOCIAL_NOTIFY_TO"
crontab -l | grep -A2 "$MARK" || true
