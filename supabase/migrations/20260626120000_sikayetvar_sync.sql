-- Şikayetvar senkron: dedup + klinik son tarama zamanı

ALTER TABLE reputation_mentions
  ADD COLUMN IF NOT EXISTS external_id TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_reputation_mentions_external
  ON reputation_mentions (clinic_id, source, external_id)
  WHERE external_id IS NOT NULL;

ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS sikayetvar_synced_at TIMESTAMPTZ;

COMMENT ON COLUMN reputation_mentions.external_id IS 'Kaynak platform şikayet/yorum ID (örn. Şikayetvar complaintId)';
COMMENT ON COLUMN clinics.sikayetvar_synced_at IS 'Son Şikayetvar tarama zamanı (wf-14 / sync-sikayetvar.py)';
