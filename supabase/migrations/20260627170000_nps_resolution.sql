-- NPS kriz takibi: yönetici notu + tamamlandı (aylık rapor için)
ALTER TABLE nps_responses
  ADD COLUMN IF NOT EXISTS manager_note TEXT,
  ADD COLUMN IF NOT EXISTS resolution_status TEXT,
  ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS resolved_by TEXT;

ALTER TABLE nps_responses DROP CONSTRAINT IF EXISTS nps_responses_resolution_status_check;
ALTER TABLE nps_responses
  ADD CONSTRAINT nps_responses_resolution_status_check
  CHECK (resolution_status IS NULL OR resolution_status IN ('open', 'resolved'));

UPDATE nps_responses
SET resolution_status = 'open'
WHERE flow = 'detractor' AND (resolution_status IS NULL OR resolution_status = '');

CREATE INDEX IF NOT EXISTS idx_nps_resolved_report
  ON nps_responses (clinic_id, resolved_at DESC)
  WHERE flow = 'detractor' AND resolution_status = 'resolved';
