-- GEO/AEO iş zekası için çok-lokasyon tablosu
-- Blueprint: locations table (multi-branch support)

CREATE TABLE IF NOT EXISTS locations (
  id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clinic_id                UUID REFERENCES clinics(id) ON DELETE CASCADE,
  business_name            VARCHAR(255) NOT NULL,
  branch_name              VARCHAR(255),
  website_url              TEXT,
  nap_address              TEXT,
  nap_phone                VARCHAR(50),
  google_place_id          TEXT,
  google_maps_url          TEXT,
  google_business_status   VARCHAR(50) DEFAULT 'Unclaimed'
    CHECK (google_business_status IN ('Claimed','Unclaimed','Verified','Suspended')),
  facebook_business_status VARCHAR(50),
  schema_org_type          TEXT DEFAULT 'LocalBusiness',
  created_at               TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_locations_clinic ON locations(clinic_id);

ALTER TABLE locations ENABLE ROW LEVEL SECURITY;

-- Yöneticiler kendi kliniklerinin lokasyonlarını okuyabilir
CREATE POLICY "manager_reads_own_locations"
  ON locations FOR SELECT TO authenticated
  USING (
    clinic_id IN (
      SELECT clinic_id FROM dashboard_users WHERE id = auth.uid()
    )
  );

CREATE POLICY "service_role_all_locations"
  ON locations FOR ALL TO service_role
  USING (true)
  WITH CHECK (true);

GRANT ALL ON locations TO service_role;

-- Pilot klinik için seed lokasyon
INSERT INTO locations (clinic_id, business_name, branch_name, website_url, nap_address, nap_phone, google_business_status, schema_org_type)
VALUES (
  '51738ea8-c12e-40ce-a0e2-42869496d76b',
  'MediDent Ağız ve Diş Sağlığı Polikliniği',
  'Kartal',
  'https://medidentistanbul.com',
  'Acıbadem Cd. 195F, Kartal, İstanbul',
  '+905491190819',
  'Verified',
  'Dentist'
) ON CONFLICT DO NOTHING;
