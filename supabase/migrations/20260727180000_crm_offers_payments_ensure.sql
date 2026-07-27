-- Ensure crm_offers + crm_payments (VPS Klinik CRM) — idempotent
-- Fixes clinic-offers / clinic-payments Proxy 502 when tables missing.

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

-- PostgREST embed: contact:crm_contacts(...) needs FK discoverable
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'crm_offers_contact_id_fkey'
  ) THEN
    ALTER TABLE public.crm_offers
      ADD CONSTRAINT crm_offers_contact_id_fkey
      FOREIGN KEY (contact_id) REFERENCES public.crm_contacts(id) ON DELETE CASCADE;
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

GRANT ALL ON public.crm_offers TO service_role;
GRANT ALL ON public.crm_payments TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.crm_offers TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.crm_payments TO authenticated;

NOTIFY pgrst, 'reload schema';
