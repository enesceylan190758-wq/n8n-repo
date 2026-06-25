-- Google Places API senkronu: place_id + yorum upsert

ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS google_place_id TEXT,
  ADD COLUMN IF NOT EXISTS google_reviews_synced_at TIMESTAMPTZ;

CREATE UNIQUE INDEX IF NOT EXISTS idx_google_reviews_clinic_external
  ON google_reviews (clinic_id, external_review_id)
  WHERE external_review_id IS NOT NULL;

COMMENT ON COLUMN clinics.google_place_id IS 'Google Places API place id (places/ChIJ...)';
COMMENT ON COLUMN clinics.google_reviews_synced_at IS 'Son Google yorum senkron zamanı';
