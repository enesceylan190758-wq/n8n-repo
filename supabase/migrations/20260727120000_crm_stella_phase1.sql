-- Medident Stella → Nefalix Klinik CRM (Phase 1)
-- Pilot clinic_id sabit UUID (MediDent Kartal)

CREATE TABLE IF NOT EXISTS crm_users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kod TEXT UNIQUE NOT NULL,
  ad TEXT NOT NULL,
  rol TEXT NOT NULL DEFAULT 'temsilci' CHECK (rol IN ('temsilci', 'yonetici')),
  aktif BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm_segments (
  code TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  show_in_dynamic BOOLEAN NOT NULL DEFAULT true,
  gun_offset INTEGER NOT NULL DEFAULT 1,
  durum TEXT DEFAULT 'notr',
  hide_in_report BOOLEAN NOT NULL DEFAULT false,
  max_dynamic_attempts INTEGER,
  sira INTEGER NOT NULL DEFAULT 100,
  aktif BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm_reference_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT UNIQUE NOT NULL,
  label TEXT NOT NULL,
  aktif BOOLEAN NOT NULL DEFAULT true,
  sira INTEGER NOT NULL DEFAULT 100,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  stella_customer_id TEXT UNIQUE,
  file_no TEXT,
  stage TEXT NOT NULL DEFAULT 'lead' CHECK (stage IN ('lead', 'danisan')),
  status TEXT NOT NULL DEFAULT 'aktif' CHECK (status IN ('aktif', 'arsiv')),
  ad TEXT NOT NULL,
  telefon TEXT,
  ulke TEXT,
  kaynak TEXT,
  reference_source_id UUID REFERENCES crm_reference_sources(id),
  kampanya TEXT,
  email TEXT,
  assigned_to UUID REFERENCES crm_users(id),
  segment_code TEXT REFERENCES crm_segments(code),
  next_call_date DATE,
  dynamic_attempt_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES crm_users(id),
  updated_by UUID REFERENCES crm_users(id)
);

CREATE TABLE IF NOT EXISTS crm_contact_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
  body TEXT NOT NULL,
  segment_code TEXT REFERENCES crm_segments(code),
  note_date DATE,
  created_by UUID REFERENCES crm_users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS crm_appointments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  stella_appointment_id TEXT UNIQUE,
  contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
  start_at TIMESTAMPTZ NOT NULL,
  end_at TIMESTAMPTZ,
  hizmet TEXT,
  personel TEXT,
  oda TEXT,
  tip TEXT,
  durum TEXT NOT NULL DEFAULT 'beklemede',
  not_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES crm_users(id),
  updated_by UUID REFERENCES crm_users(id)
);

CREATE TABLE IF NOT EXISTS crm_offers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  contact_id UUID NOT NULL REFERENCES crm_contacts(id) ON DELETE CASCADE,
  title TEXT,
  currency TEXT NOT NULL DEFAULT 'EUR',
  amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
  hotel TEXT,
  transfer TEXT,
  lines JSONB NOT NULL DEFAULT '[]'::jsonb,
  status TEXT NOT NULL DEFAULT 'taslak',
  temsilci TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES crm_users(id)
);

CREATE TABLE IF NOT EXISTS crm_payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id UUID NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  contact_id UUID REFERENCES crm_contacts(id) ON DELETE SET NULL,
  payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
  amount NUMERIC(12, 2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'EUR',
  method TEXT,
  description TEXT,
  appointment_id UUID REFERENCES crm_appointments(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES crm_users(id)
);

CREATE INDEX IF NOT EXISTS idx_crm_contacts_dynamic ON crm_contacts (status, next_call_date, assigned_to);
CREATE INDEX IF NOT EXISTS idx_crm_contacts_stella ON crm_contacts (stella_customer_id);
CREATE INDEX IF NOT EXISTS idx_crm_appointments_start ON crm_appointments (start_at);
CREATE INDEX IF NOT EXISTS idx_crm_offers_contact ON crm_offers (contact_id);
CREATE INDEX IF NOT EXISTS idx_crm_payments_contact ON crm_payments (contact_id, payment_date);

-- Seed users (idempotent)
INSERT INTO crm_users (kod, ad, rol) VALUES
  ('enes', 'Enes Ceylan', 'yonetici'),
  ('abdulkadir', 'Abdülkadir Yaşar', 'yonetici'),
  ('kader', 'Kader Hanım', 'temsilci')
ON CONFLICT (kod) DO UPDATE SET ad = EXCLUDED.ad, rol = EXCLUDED.rol, aktif = true;
