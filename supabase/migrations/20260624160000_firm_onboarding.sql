-- Firma onboarding: otomasyon ancak gereksinimler tamamlanınca açılır

ALTER TABLE clinics
  ADD COLUMN IF NOT EXISTS automation_enabled BOOLEAN NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS integration_config JSONB NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS manager_whatsapp_phone TEXT,
  ADD COLUMN IF NOT EXISTS crm_type TEXT,
  ADD COLUMN IF NOT EXISTS evolution_instance_name TEXT;

COMMENT ON COLUMN clinics.automation_enabled IS 'Tüm entegrasyon alanları dolu → true; n8n workflow''ları bu firmayı işler';
COMMENT ON COLUMN clinics.integration_config IS 'API anahtarları, webhook durumu, notlar (hassas alanlar)';

-- Medident pilot zaten canlı
UPDATE clinics
SET automation_enabled = true
WHERE slug = 'medident-istanbul' OR id = '51738ea8-c12e-40ce-a0e2-42869496d76b';

-- Demo firma logoları (nefalix-landing /public)
UPDATE clinics SET logo_url = '/logos/demo/byotell.svg' WHERE slug = 'demo-byotell-istanbul';
UPDATE clinics SET logo_url = '/logos/demo/antwell.svg' WHERE slug = 'demo-antwell-hotels';
UPDATE clinics SET logo_url = '/logos/demo/hilton.svg' WHERE slug = 'demo-hilton-bomonti';
UPDATE clinics SET logo_url = '/logos/demo/bosch.svg' WHERE slug = 'demo-bosch-car-kadikoy';
UPDATE clinics SET logo_url = '/logos/demo/king-auto.png' WHERE slug = 'demo-king-auto';
UPDATE clinics SET logo_url = '/logos/demo/yamanlar.png' WHERE slug = 'demo-yamanlar-expertiz';
