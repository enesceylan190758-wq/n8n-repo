-- Günlük GEO paket kayıtları (alıntı sorusu → cevap)
CREATE TABLE IF NOT EXISTS geo_daily_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_date DATE NOT NULL,
  bucket TEXT,
  prompt TEXT NOT NULL,
  direct_answer TEXT,
  bullets JSONB DEFAULT '[]'::jsonb,
  faq JSONB DEFAULT '[]'::jsonb,
  internal_links JSONB DEFAULT '[]'::jsonb,
  linkedin_one_liner TEXT,
  answer_html TEXT,
  status TEXT NOT NULL DEFAULT 'published',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (run_date)
);

CREATE INDEX IF NOT EXISTS idx_geo_daily_runs_date
  ON geo_daily_runs (run_date DESC);

ALTER TABLE geo_daily_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_geo_daily_runs"
  ON geo_daily_runs FOR ALL TO service_role
  USING (true) WITH CHECK (true);

CREATE POLICY "anon_read_geo_daily_runs"
  ON geo_daily_runs FOR SELECT TO anon
  USING (status = 'published');

GRANT SELECT ON geo_daily_runs TO anon;
GRANT ALL ON geo_daily_runs TO service_role;
