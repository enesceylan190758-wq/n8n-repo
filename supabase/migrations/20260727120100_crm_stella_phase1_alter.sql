-- Stella Phase1 incremental — mevcut VPS Klinik CRM şemasına ekler (idempotent)

ALTER TABLE public.crm_segments
  ADD COLUMN IF NOT EXISTS durum text DEFAULT 'notr',
  ADD COLUMN IF NOT EXISTS hide_in_report boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS max_dynamic_attempts integer;

CREATE TABLE IF NOT EXISTS public.crm_reference_sources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text UNIQUE NOT NULL,
  label text NOT NULL,
  aktif boolean NOT NULL DEFAULT true,
  sira integer NOT NULL DEFAULT 100,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.crm_contacts
  ADD COLUMN IF NOT EXISTS stella_customer_id text,
  ADD COLUMN IF NOT EXISTS email text,
  ADD COLUMN IF NOT EXISTS reference_source_id uuid REFERENCES public.crm_reference_sources(id),
  ADD COLUMN IF NOT EXISTS dynamic_attempt_count integer NOT NULL DEFAULT 0;

ALTER TABLE public.crm_contacts DROP CONSTRAINT IF EXISTS crm_contacts_stella_customer_id_key;
ALTER TABLE public.crm_contacts ADD CONSTRAINT crm_contacts_stella_customer_id_key UNIQUE (stella_customer_id);

ALTER TABLE public.crm_appointments
  ADD COLUMN IF NOT EXISTS stella_appointment_id text;

ALTER TABLE public.crm_appointments DROP CONSTRAINT IF EXISTS crm_appointments_stella_appointment_id_key;
ALTER TABLE public.crm_appointments ADD CONSTRAINT crm_appointments_stella_appointment_id_key UNIQUE (stella_appointment_id);

ALTER TABLE public.crm_appointments DROP CONSTRAINT IF EXISTS crm_appointments_durum_check;
ALTER TABLE public.crm_appointments ADD CONSTRAINT crm_appointments_durum_check
  CHECK (durum = ANY (ARRAY['beklemede','geldi','tamamlandi','iptal','gelmedi','ertelendi']));

CREATE TABLE IF NOT EXISTS public.crm_offers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id uuid NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  contact_id uuid NOT NULL REFERENCES public.crm_contacts(id) ON DELETE CASCADE,
  title text,
  currency text NOT NULL DEFAULT 'EUR',
  amount numeric(12, 2) NOT NULL DEFAULT 0,
  hotel text,
  transfer text,
  lines jsonb NOT NULL DEFAULT '[]'::jsonb,
  status text NOT NULL DEFAULT 'taslak',
  temsilci text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  created_by uuid REFERENCES public.crm_users(id)
);

CREATE TABLE IF NOT EXISTS public.crm_payments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id uuid NOT NULL DEFAULT '51738ea8-c12e-40ce-a0e2-42869496d76b',
  contact_id uuid REFERENCES public.crm_contacts(id) ON DELETE SET NULL,
  payment_date date NOT NULL DEFAULT CURRENT_DATE,
  amount numeric(12, 2) NOT NULL,
  currency text NOT NULL DEFAULT 'EUR',
  method text,
  description text,
  appointment_id uuid REFERENCES public.crm_appointments(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  created_by uuid REFERENCES public.crm_users(id)
);

CREATE INDEX IF NOT EXISTS idx_crm_offers_contact ON public.crm_offers (contact_id);
CREATE INDEX IF NOT EXISTS idx_crm_payments_contact ON public.crm_payments (contact_id, payment_date);

UPDATE public.crm_users SET rol = 'yonetici', ad = 'Abdülkadir Yaşar', aktif = true WHERE kod = 'abdulkadir';
UPDATE public.crm_users SET rol = 'yonetici', aktif = true WHERE kod = 'enes';
INSERT INTO public.crm_users (kod, ad, rol) VALUES ('kader', 'Kader Hanım', 'temsilci')
ON CONFLICT (kod) DO UPDATE SET ad = EXCLUDED.ad, aktif = true;
