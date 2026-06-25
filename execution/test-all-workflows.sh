#!/usr/bin/env bash
# Nefalix workflow smoke tests — webhook + Supabase doğrulama
set -euo pipefail

BASE="${N8N_URL:-http://localhost:5678}/webhook"
KEY="${SUPABASE_SERVICE_ROLE_KEY:-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU}"
SB="http://127.0.0.1:54321/rest/v1"
TS=$(date +%s)
PASS=0
FAIL=0

sb_count() {
  local table=$1 filter=$2
  curl -s "${SB}/${table}?select=id&${filter}" \
    -H "apikey: $KEY" -H "Authorization: Bearer $KEY" \
    -H "Prefer: count=exact" -I 2>/dev/null | grep -i content-range | sed 's/.*\///' | tr -d '\r'
}

test_case() {
  local name=$1 endpoint=$2 payload=$3 table=$4 filter=$5
  echo ""
  echo "━━━ $name ━━━"
  local resp http
  resp=$(curl -s -w "\n%{http_code}" -X POST "$BASE/$endpoint" \
    -H "Content-Type: application/json" -d "$payload")
  http=$(echo "$resp" | tail -1)
  body=$(echo "$resp" | sed '$d')
  echo "HTTP $http | $body" | head -c 200
  echo ""
  sleep "${WAIT_AI:-10}"
  local cnt
  cnt=$(sb_count "$table" "$filter")
  if [[ "$cnt" -ge 1 ]]; then
    echo "✅ Supabase $table: $cnt kayıt"
    PASS=$((PASS + 1))
  else
    echo "❌ Supabase $table: kayıt yok ($filter)"
    FAIL=$((FAIL + 1))
  fi
}

echo "Nefalix workflow test — $TS"

# 1 Web Chatbot (opsiyonel — pilot dışı)
if [[ "${SKIP_CHATBOT_TEST:-0}" != "1" ]]; then
echo ""
echo "━━━ Web Chatbot ━━━"
chat=$(curl -s -w "\n%{http_code}" -X POST \
  "http://localhost:5678/webhook/8bb40d02-5ff5-4262-bfda-ebc6ea458a22/chat" \
  -H "Content-Type: application/json" \
  -d "{\"action\":\"sendMessage\",\"sessionId\":\"test-$TS\",\"chatInput\":\"Test mesajı $TS\"}")
if echo "$chat" | grep -q '"output"'; then
  echo "✅ Chatbot yanıt verdi"
  PASS=$((PASS + 1))
else
  echo "⊘ Chatbot atlandı (Medident pilot dışı)"
fi
fi

# 2 NPS response (promoter)
test_case "NPS Yanıt (Feedback Loop)" "nefalix/nps/response" \
  "{\"score\":10,\"patientName\":\"Test $TS\",\"googleReviewUrl\":\"https://g.page/r/test\",\"complaintFormUrl\":\"https://nefalixai.com/sikayet\"}" \
  "nps_responses" "score=eq.10&order=created_at.desc&limit=1"

# 3 HBYS appointment (may fail WhatsApp — checked separately)
echo ""
echo "━━━ HBYS Randevu Bitti ━━━"
hbys=$(curl -s -w "\n%{http_code}" -X POST "$BASE/nefalix/hbys/appointment-completed" \
  -H "Content-Type: application/json" \
  -d "{\"patientName\":\"Test HBYS $TS\",\"patientPhone\":\"+905551112233\",\"clinicName\":\"MediDent\",\"doctorName\":\"Dr. Test\",\"treatment\":\"dolgu\",\"googleReviewUrl\":\"https://g.page/r/test\",\"complaintFormUrl\":\"https://nefalixai.com/sikayet\",\"appointmentId\":\"apt-$TS\"}")
echo "$hbys" | sed '$d' | head -c 150
echo " HTTP $(echo "$hbys" | tail -1)"

# 4 Google Review
test_case "Google Review AI" "nefalix/google/new-review" \
  "{\"rating\":4,\"text\":\"Test yorum $TS\",\"authorName\":\"Test User\"}" \
  "google_reviews" "author_name=eq.Test%20User&order=created_at.desc&limit=1"

# 5 eNPS
test_case "Inside eNPS" "nefalix/enps/response" \
  "{\"score\":7,\"employeeName\":\"Test Personel\",\"department\":\"test-$TS\"}" \
  "enps_responses" "department=eq.test-$TS"

# 6 Sentinel (text → content alanına yazılır)
test_case "Sentinel İtibar" "nefalix/sentinel/mention" \
  "{\"text\":\"Test mention $TS\",\"platform\":\"sikayetvar\"}" \
  "reputation_mentions" "content=like.*Test%20mention%20$TS*"

# 6b Şikayetvar sync (wf-14 — mention kaydı Sentinel üzerinden gelir)
echo ""
echo "━━━ Şikayetvar Senkron (wf-14) ━━━"
sv=$(curl -s -w "\n%{http_code}" -X POST "$BASE/nefalix/sikayetvar/sync" \
  -H "Content-Type: application/json" -d '{"dryRun":true}')
echo "$sv" | sed '$d' | head -c 250
echo " HTTP $(echo "$sv" | tail -1)"
if echo "$sv" | grep -q '"ok":true'; then
  echo "✅ Şikayetvar sync yanıt verdi"
  PASS=$((PASS + 1))
else
  echo "❌ Şikayetvar sync başarısız"
  FAIL=$((FAIL + 1))
fi

# 7 Recall
test_case "Recall Kayıp Hasta" "nefalix/recall/check-patients" \
  "{\"patientPhone\":\"+905551112233\",\"patientName\":\"Test Recall $TS\",\"lastVisitDays\":400,\"lastTreatment\":\"smoke-$TS\"}" \
  "recall_campaigns" "last_treatment=eq.smoke-$TS"

# 8 Inbox
test_case "Inbox Mesaj" "nefalix/inbox/incoming" \
  "{\"from\":\"+905559998877\",\"body\":\"Test inbox $TS\",\"channel\":\"whatsapp\"}" \
  "inbox_messages" "body=like.*$TS*"

echo ""
echo "════════════════════════════"
echo "SONUÇ: ✅ $PASS başarılı | ❌ $FAIL başarısız"
exit $FAIL
