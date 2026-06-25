-- Firma sektörü: klinik (varsayılan), otel, oto servis
ALTER TABLE clinics ADD COLUMN IF NOT EXISTS sector TEXT NOT NULL DEFAULT 'clinic'
  CHECK (sector IN ('clinic', 'hotel', 'auto'));

CREATE INDEX IF NOT EXISTS idx_clinics_sector ON clinics(sector);

UPDATE clinics SET sector = 'clinic' WHERE sector IS NULL OR sector = '';
