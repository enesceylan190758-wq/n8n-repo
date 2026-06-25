#!/usr/bin/env bash
# VPS üzerinde çalışır — hassas Docker portlarını dış dünyaya kapatır
set -euo pipefail

cd /opt/nefalix

echo "▶ .env izinleri (sadece root)"
chmod 600 .env 2>/dev/null || true
chown root:root .env 2>/dev/null || true

echo "▶ DOCKER-USER — Supabase / Evolution / MCP portları (dış erişim DROP)"
BLOCK_PORTS=(54321 54322 54323 54324 54327 8080 3000)
for port in "${BLOCK_PORTS[@]}"; do
  if ! iptables -C DOCKER-USER -p tcp -m tcp --dport "$port" ! -s 127.0.0.1 -j DROP 2>/dev/null; then
    iptables -I DOCKER-USER -p tcp -m tcp --dport "$port" ! -s 127.0.0.1 -j DROP
    echo "  DROP external :$port"
  fi
done

if command -v netfilter-persistent >/dev/null 2>&1; then
  netfilter-persistent save
elif [[ -d /etc/iptables ]]; then
  iptables-save > /etc/iptables/rules.v4
fi

echo "▶ Docker compose — Evolution/MCP sadece localhost"
docker compose -f docker-compose.yml -f docker-compose.evolution.yml -f docker-compose.prod.yml up -d

echo "▶ Caddy yeniden yükle"
docker compose -f docker-compose.yml -f docker-compose.evolution.yml -f docker-compose.prod.yml restart caddy 2>/dev/null || true

echo "▶ Doğrulama (dışarıdan 54321 kapalı olmalı — bu sunucudan test)"
if curl -sf --max-time 3 "http://$(hostname -I | awk '{print $1}'):54321/rest/v1/" >/dev/null 2>&1; then
  echo "⚠️  UYARI: Supabase hâlâ dış IP'den erişilebilir görünüyor — sağlayıcı firewall kontrol edin"
else
  echo "✓ Supabase dış erişim engellendi (veya timeout)"
fi

curl -sf http://127.0.0.1:5678/healthz >/dev/null && echo "✓ n8n localhost OK"
