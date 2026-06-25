#!/usr/bin/env bash
# Estesoft panelinde yapıştırılacak webhook bilgisi + doğrulama
set -euo pipefail

HOST="${N8N_PUBLIC_HOST:-api.nefalixai.com}"
WEBHOOK_URL="https://${HOST}/webhook/nefalix/estesoft/webhook"

cat <<EOF

╔══════════════════════════════════════════════════════════════════╗
║  Estesoft → Nefalix NPS Webhook Kurulumu                        ║
╚══════════════════════════════════════════════════════════════════╝

1) Estesoft klinik paneline gir (Medident hesabı)
2) Geliştirici / API bölümü (API anahtarını aldığın yer)
3) "Webhook" veya "Abonelik" (subscribe) menüsü
4) Yeni webhook ekle:

   URL (kopyala):
   ${WEBHOOK_URL}

   Method: POST
   Content-Type: application/json

5) Olaylar (en az biri):
   • appointment.completed  (varsa — tercih)
   • appointment.updated    (durum = tamamlandı)
   • Randevu tamamlandı / closed / completed

6) Kaydet → panelde "Test gönder" varsa çalıştır

Nefalix tarafı hazır (workflow: Nefalix - Estesoft HBYS Adapter).

Estesoft kendi randevu sonrası anketini açık tutuyorsa çakışır —
Nefalix NPS için Estesoft anketini kapat veya tek kanal seç.

Swagger'da webhook subscribe endpoint görürsen ESTESOFT_BASE_URL'i
.env'e yaz; API ile otomatik kayıt eklenebilir.

EOF

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ "${RUN_TEST:-1}" == "1" ]]; then
  echo ""
  bash "$SCRIPT_DIR/test-estesoft-nps.sh" "${TEST_PHONE:-}"
fi
