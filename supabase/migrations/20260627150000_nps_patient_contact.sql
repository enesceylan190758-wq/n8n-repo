-- NPS yanıtlarında hasta iletişim bilgisi (panel alarm / geri arama)
ALTER TABLE nps_responses
  ADD COLUMN IF NOT EXISTS patient_name TEXT,
  ADD COLUMN IF NOT EXISTS patient_phone TEXT;

CREATE INDEX IF NOT EXISTS idx_nps_detractor_recent
  ON nps_responses (clinic_id, created_at DESC)
  WHERE flow = 'detractor';
