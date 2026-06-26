-- İç-Dış korelasyon tablosu: çalışan eNPS ↔ hasta yıldız derecelendirmesi
-- Blueprint: operational_sentiment — board-ready yönetici özetleri için

CREATE TABLE IF NOT EXISTS operational_sentiment (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id         UUID REFERENCES locations(id) ON DELETE CASCADE,
  period              VARCHAR(10) NOT NULL,           -- 'Q2_2026', '2026-06' vb.
  patient_star_rating NUMERIC(3,2),                  -- Genel Google yıldız ortalaması
  negative_review_pct INT,                           -- Negatif yorum yüzdesi
  staff_pulse_score   INT CHECK (staff_pulse_score BETWEEN 0 AND 100),
  enps_score          INT,                           -- Çalışan NPS (-100 ile +100)
  burnout_rate        INT,                           -- Tükenmişlik yüzdesi (tahmin/anket)
  turnover_rate       INT,                           -- Personel devir hızı yüzdesi
  nps_promoter_pct    INT,                           -- Hasta promoter yüzdesi
  nps_detractor_pct   INT,                           -- Hasta detractor yüzdesi
  correlation_score   NUMERIC(5,4),                  -- Pearson r katsayısı (hesaplanmış)
  executive_summary   TEXT,                          -- AI-generated board özeti (JSON veya markdown)
  risk_level          TEXT DEFAULT 'normal'
    CHECK (risk_level IN ('low','normal','elevated','critical')),
  updated_at          TIMESTAMPTZ DEFAULT now(),
  UNIQUE (location_id, period)
);

CREATE INDEX IF NOT EXISTS idx_operational_sentiment_location
  ON operational_sentiment(location_id, period DESC);

-- Son 4 çeyreği getiren view (korelasyon grafiği için)
CREATE OR REPLACE VIEW v_sentiment_trend AS
SELECT
  os.*,
  l.business_name,
  l.branch_name,
  l.clinic_id
FROM operational_sentiment os
JOIN locations l ON l.id = os.location_id
ORDER BY os.period DESC;

ALTER TABLE operational_sentiment ENABLE ROW LEVEL SECURITY;

CREATE POLICY "manager_reads_own_sentiment"
  ON operational_sentiment FOR SELECT TO authenticated
  USING (
    location_id IN (
      SELECT lo.id FROM locations lo
      JOIN dashboard_users du ON du.clinic_id = lo.clinic_id
      WHERE du.id = auth.uid()
    )
  );

CREATE POLICY "service_role_all_sentiment"
  ON operational_sentiment FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON operational_sentiment TO service_role;
