#!/usr/bin/env bash
# Günlük GEO + haftalık citation hatırlatma cron
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARK="# nefalix-daily-geo"
CRON_GEO="15 9 * * * cd ${ROOT} && set -a && . ./.env && set +a && PYTHONUNBUFFERED=1 /usr/bin/python3 -u execution/publish-daily-geo.py >> /var/log/nefalix-geo.log 2>&1"
CRON_WEEK="0 10 * * 0 cd ${ROOT} && set -a && . ./.env && set +a && PYTHONUNBUFFERED=1 /usr/bin/python3 -u execution/send-geo-weekly-reminder.py >> /var/log/nefalix-geo.log 2>&1"

TMP="$(mktemp)"
(crontab -l 2>/dev/null || true) \
  | grep -vF "$MARK" \
  | grep -v "publish-daily-geo.py" \
  | grep -v "send-geo-weekly-reminder.py" >"$TMP" || true
{
  cat "$TMP"
  echo "$MARK"
  echo "CRON_TZ=Europe/Istanbul"
  echo "$CRON_GEO"
  echo "$CRON_WEEK"
} | crontab -
rm -f "$TMP"

touch /var/log/nefalix-geo.log
chmod 644 /var/log/nefalix-geo.log 2>/dev/null || true

if ! grep -q "^GEO_NOTIFY_TO=" "$ROOT/.env" 2>/dev/null; then
  if grep -q "^BLOG_NOTIFY_TO=" "$ROOT/.env" 2>/dev/null; then
    echo "GEO_NOTIFY_TO=$(grep '^BLOG_NOTIFY_TO=' "$ROOT/.env" | cut -d= -f2-)" >>"$ROOT/.env"
  else
    echo "GEO_NOTIFY_TO=enes.ceylan190758@gmail.com,akadirysr@gmail.com" >>"$ROOT/.env"
  fi
fi

echo "✓ GEO cron: her gün 09:15 + Pazar 10:00 Europe/Istanbul"
echo "  Log: /var/log/nefalix-geo.log"
crontab -l | grep -A4 "$MARK" || true
