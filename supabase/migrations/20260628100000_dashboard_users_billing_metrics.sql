-- Dashboard firma kullanıcıları + Stripe abonelik alanları
CREATE TABLE IF NOT EXISTS dashboard_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  salt TEXT,
  password_hash TEXT,
  role TEXT NOT NULL DEFAULT 'manager' CHECK (role IN ('admin', 'manager')),
  clinic_id UUID REFERENCES clinics(id) ON DELETE CASCADE,
  first_name TEXT,
  last_name TEXT,
  phone TEXT,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'disabled')),
  setup_token_hash TEXT,
  setup_token_expires_at TIMESTAMPTZ,
  password_set_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_dashboard_users_clinic ON dashboard_users(clinic_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_users_setup_token
  ON dashboard_users(setup_token_hash)
  WHERE setup_token_hash IS NOT NULL;

ALTER TABLE dashboard_users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_dashboard_users"
  ON dashboard_users FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON dashboard_users TO service_role;

ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT,
  ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
  ADD COLUMN IF NOT EXISTS plan_tier TEXT,
  ADD COLUMN IF NOT EXISTS subscription_status TEXT DEFAULT 'none',
  ADD COLUMN IF NOT EXISTS subscription_current_period_end TIMESTAMPTZ;

ALTER TABLE clinics DROP CONSTRAINT IF EXISTS clinics_plan_tier_check;
ALTER TABLE clinics
  ADD CONSTRAINT clinics_plan_tier_check
  CHECK (plan_tier IS NULL OR plan_tier IN ('standard', 'professional', 'enterprise'));

ALTER TABLE clinics DROP CONSTRAINT IF EXISTS clinics_subscription_status_check;
ALTER TABLE clinics
  ADD CONSTRAINT clinics_subscription_status_check
  CHECK (subscription_status IN ('none', 'active', 'trialing', 'past_due', 'canceled', 'incomplete'));

CREATE TABLE IF NOT EXISTS stripe_webhook_events (
  event_id TEXT PRIMARY KEY,
  event_type TEXT NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE stripe_webhook_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_stripe_webhook_events"
  ON stripe_webhook_events FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON stripe_webhook_events TO service_role;
