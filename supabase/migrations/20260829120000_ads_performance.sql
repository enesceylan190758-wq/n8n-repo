-- Reklam performans senkronu (Meta Ads Graph API + Google Ads API)
-- Klinik başına reklam hesabı eşlemesi + günlük kampanya metrikleri.

CREATE TABLE IF NOT EXISTS ad_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('meta', 'google')),
  account_id TEXT NOT NULL, -- Meta: act_<id> | Google: customer_id (xxx-xxx-xxxx)
  account_name TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'token_expired')),
  last_synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (clinic_id, platform, account_id)
);

CREATE INDEX IF NOT EXISTS idx_ad_accounts_clinic ON ad_accounts(clinic_id);

ALTER TABLE ad_accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_ad_accounts"
  ON ad_accounts FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON ad_accounts TO service_role;

CREATE TABLE IF NOT EXISTS ad_insights_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('meta', 'google')),
  account_id TEXT NOT NULL,
  campaign_id TEXT NOT NULL,
  campaign_name TEXT,
  date DATE NOT NULL,
  currency TEXT DEFAULT 'TRY',
  spend NUMERIC(12, 2) DEFAULT 0,
  impressions BIGINT DEFAULT 0,
  clicks BIGINT DEFAULT 0,
  leads BIGINT DEFAULT 0,
  conversions BIGINT DEFAULT 0,
  cpc NUMERIC(12, 4),
  ctr NUMERIC(8, 4),
  synced_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (clinic_id, platform, campaign_id, date)
);

CREATE INDEX IF NOT EXISTS idx_ad_insights_clinic_date ON ad_insights_daily(clinic_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_ad_insights_platform ON ad_insights_daily(platform);

ALTER TABLE ad_insights_daily ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_ad_insights_daily"
  ON ad_insights_daily FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON ad_insights_daily TO service_role;

COMMENT ON TABLE ad_accounts IS 'Klinik ↔ Meta/Google reklam hesabı eşlemesi';
COMMENT ON TABLE ad_insights_daily IS 'Meta Graph API / Google Ads API günlük kampanya metrikleri';
