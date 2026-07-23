-- AI Search Readiness & GEO/AEO metrik takip tablosu
-- Blueprint: ai_readiness_scores — her teknik audit sonrası yazılır

CREATE TABLE IF NOT EXISTS ai_readiness_scores (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  location_id            UUID REFERENCES locations(id) ON DELETE CASCADE,
  overall_score          INT CHECK (overall_score BETWEEN 0 AND 100),
  discoverability_score  INT,   -- Bot erişilebilirliği, sayfa hızı, teknik altyapı
  answer_readiness_score INT,   -- LLM için alıntılanabilir metin, FAQ yapısı
  trust_signals_score    INT,   -- Yorum hızı, otorite, güncellik
  llm_txt_present        BOOLEAN DEFAULT FALSE,
  schema_markup_valid    BOOLEAN DEFAULT FALSE,
  nap_consistent         BOOLEAN DEFAULT FALSE,
  robots_allows_ai       BOOLEAN DEFAULT TRUE,
  page_speed_score       INT,
  faq_schema_present     BOOLEAN DEFAULT FALSE,
  grade                  CHAR(1) CHECK (grade IN ('A','B','C','D')),
  audit_details          JSONB DEFAULT '{}',   -- Alt kontrol detayları (ham sonuçlar)
  recommendations        JSONB DEFAULT '[]',   -- Önceliklendirilmiş öneri listesi
  audit_date             TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_readiness_location
  ON ai_readiness_scores(location_id, audit_date DESC);

-- Klinik bazlı son skor view'ı (dashboard'da kullanılır)
CREATE OR REPLACE VIEW v_latest_ai_scores AS
SELECT DISTINCT ON (location_id)
  ars.*,
  l.business_name,
  l.branch_name,
  l.clinic_id,
  l.website_url
FROM ai_readiness_scores ars
JOIN locations l ON l.id = ars.location_id
ORDER BY location_id, audit_date DESC;

ALTER TABLE ai_readiness_scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "manager_reads_own_scores"
  ON ai_readiness_scores FOR SELECT TO authenticated
  USING (
    location_id IN (
      SELECT lo.id FROM locations lo
      JOIN dashboard_users du ON du.clinic_id = lo.clinic_id
      WHERE du.id = auth.uid()
    )
  );

CREATE POLICY "service_role_all_ai_scores"
  ON ai_readiness_scores FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON ai_readiness_scores TO service_role;

-- clinics tablosuna GEO özet alanları
ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS llms_txt_url TEXT,
  ADD COLUMN IF NOT EXISTS geo_grade     CHAR(1);

-- google_reviews tablosuna AEO alanları
ALTER TABLE google_reviews
  ADD COLUMN IF NOT EXISTS quote_ready_passage  TEXT,
  ADD COLUMN IF NOT EXISTS answer_quality_score INT;
